import asyncio
import os
import json
import argparse
import re
from datetime import datetime
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI
from dotenv import load_dotenv
from openai.types.chat import ChatCompletionToolParam
from openai.types.shared_params.function_definition import FunctionDefinition

load_dotenv(override=True)

MAX_RETRIES = 15
TARGET_COVERAGE = 100 

class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.llm = OpenAI()
        self.best_results = {} 

    async def connect_to_server(self, server_script_path: str):
        server_params = StdioServerParameters(command="python", args=[server_script_path], env=None)
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await self.session.initialize()
        print("\n✅ Connected to server.")

    async def cleanup(self):
        await self.exit_stack.aclose()

    async def execute_tool(self, tool_name, tool_args):
        print(f"  🛠️  {tool_name}...", end="\r")
        result = await self.session.call_tool(tool_name, tool_args)
        print(f"  ✅ {tool_name} Done.    ") 
        output = result.content[0].text if result.content else ""
        return output

    def _parse_feedback(self, run_output, cov_output, current_score):
        feedback_points = []

        if "SyntaxError" in run_output or "IndentationError" in run_output:
            return "CRITICAL_SYNTAX_ERROR"

        runtime_errors = re.findall(r"E\s+(\w+Error):.+", run_output)
        runtime_errors = [e for e in runtime_errors if "Assertion" not in e]
        if runtime_errors:
            feedback_points.append(f"🔥 **RUNTIME CRASH DETECTED ({runtime_errors[0]})**:")
            feedback_points.append("- **ACTION**: Check inputs. Fix the crash first.")
            feedback_points.append(f"- Log:\n{run_output[-500:]}")
            return "\n".join(feedback_points)

        failures = re.findall(r"(E\s+assert.+)", run_output)
        if failures:
            feedback_points.append("❌ **ASSERTION FAILURE**:")
            for f in failures:
                feedback_points.append(f"- `{f}`")
            feedback_points.append("-> **ACTION**: TRUST THE CODE. Update test expectation.")


        if current_score > 0:
            missing_lines = []
            for line in cov_output.splitlines():
                if re.search(r"\.py\s+\d+", line):
                    parts = line.split()
                    if len(parts) >= 5 and "%" in parts[-2]:
                        missing_str = parts[-1]
                        if missing_str != "": missing_lines.append(missing_str)

            if missing_lines:
                feedback_points.append(f"🎯 **MISSING COVERAGE**: Lines `{', '.join(missing_lines)}`.")
        
        elif current_score == 0:
            return "ZERO_COVERAGE_ERROR"

        if not feedback_points:
            return f"Pytest Result:\n{run_output[-500:]}"
        
        return "\n".join(feedback_points)

    async def process_single_file(self, target_file_path: str, result_dir: str):
        target_filename = os.path.basename(target_file_path)
        module_name = os.path.splitext(target_filename)[0]
        test_filename = f"test_{module_name}.py"
        test_file_path = f"{result_dir}/{test_filename}"
        
        print(f"\n{'='*60}")
        print(f" 🚀 PROCESSING: {target_filename}")
        print(f"{'='*60}")
        
        target_content = await self.execute_tool('read_file', {'file_path': target_file_path})

        system_instruction = (
            "You are a Surgical Python QA Engineer. Goal: 100% Coverage.\n"
            "STRATEGY:\n"
            "1. **CRASHES FIRST**: Fix crashes immediately.\n"
            "2. **ASSERTION FAILURES**: If `assert` fails, TRUST THE CODE. Update expected value.\n"
            "3. **MISSING LINES**: Only add tests for specified lines.\n"
            "4. **NO HALLUCINATIONS**: Do not copy source code."
        )

        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"Target Source Code (`{target_filename}`):\n```python\n{target_content}\n```\n\nTask: Write `{test_filename}` to achieve 100% coverage."}
        ]
        
        current_best = 0
        best_code_content = ""
        
        for attempt in range(1, MAX_RETRIES + 1):
            print(f"\n[Attempt {attempt}/{MAX_RETRIES}] Thinking...")

            tool_schema = await self.session.list_tools()
            openai_tools = [ChatCompletionToolParam(type="function", function=FunctionDefinition(name=t.name, description=t.description, parameters=t.inputSchema)) for t in tool_schema.tools]
            
            response = self.llm.chat.completions.create(
                model="gpt-4o-mini", messages=messages, tools=openai_tools, tool_choice="auto"
            )
            ai_msg = response.choices[0].message
            messages.append(ai_msg)

            if ai_msg.tool_calls:
                for tool_call in ai_msg.tool_calls:
                    args = json.loads(tool_call.function.arguments)
                    if tool_call.function.name == "write_file":
                        args['file_path'] = test_file_path
                    
                    tool_output = await self.execute_tool(tool_call.function.name, args)
                    messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": tool_output})

            run_output = await self.execute_tool('run_pytest', {
                'test_file_path': test_file_path, 'target_file_path': target_file_path
            })

            cov_output = await self.execute_tool('measure_coverage', {
                'test_file_path': test_file_path, 'target_file_path': target_file_path
            })
            
            score = 0
            match = re.search(r'TOTAL\s+\d+\s+\d+\s+(\d+)%', cov_output)
            if match:
                score = int(match.group(1))

            if score > current_best:
                print(f"  📈 Score: {score}% (New Best!)")
                current_best = score
                self.best_results[module_name] = score
                
                best_code_content = await self.execute_tool('read_file', {'file_path': test_file_path})
                
                best_path = f"best_coverages/{test_filename}"
                await self.execute_tool('write_file', {'file_path': best_path, 'content': best_code_content})
            else:
                print(f"  📉 Score: {score}%")

            if score >= TARGET_COVERAGE:
                print(f"  🎉 SUCCESS! 100% Coverage.")
                break

            parsed_feedback = self._parse_feedback(run_output, cov_output, score)
        
            if (parsed_feedback == "CRITICAL_SYNTAX_ERROR" or parsed_feedback == "ZERO_COVERAGE_ERROR") and current_best > 0:
                print(f"  ⚠️ [ROLLBACK] Reverting to last best code ({current_best}%)...")

                await self.execute_tool('write_file', {'file_path': test_file_path, 'content': best_code_content})

                rollback_msg = (
                    f"⚠️ **ROLLBACK TRIGGERED**: Your last edit caused a Syntax Error or 0% coverage.\n"
                    f"I have reverted the file to the version with {current_best}% coverage.\n"
                    "**INSTRUCTION**: Try again. Do NOT make the same mistake. Check your syntax carefully."
                )
                messages.append({"role": "user", "content": rollback_msg})
                continue

            final_feedback = (
                f"Current Score: {score}%\n\n"
                f"{parsed_feedback}\n\n"
                "INSTRUCTION: Fix the failures or add missing tests."
            )
            print(f"  🤖 Feedback: {parsed_feedback.splitlines()[0] if parsed_feedback else 'None'} ...")
            messages.append({"role": "user", "content": final_feedback})

    async def run_task2(self):
        files_str = await self.execute_tool('list_files', {})
        try:
            target_files = eval(files_str)
        except:
            target_files = []
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        result_dir = f"task2_results_{timestamp}"
        print(f"📂 Working Directory: {result_dir}")

        for file_path in target_files:
            await self.process_single_file(file_path, result_dir)

        print(f"\n{'='*60}\n 📊 FINAL REPORT\n{'='*60}")
        print(json.dumps(self.best_results, indent=2))
        with open("best_coverages/results.json", "w") as f:
            json.dump(self.best_results, f)

async def main(server_script_path):
    client = MCPClient()
    try:
        await client.connect_to_server(server_script_path)
        await client.run_task2()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('server_script_path', type=str)
    args = parser.parse_args()
    asyncio.run(main(args.server_script_path))