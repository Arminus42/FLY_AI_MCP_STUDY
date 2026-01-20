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

MAX_RETRIES = 20
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
        print(f"  🛠️  [Tool Executing] {tool_name}...")
        
        result = await self.session.call_tool(tool_name, tool_args)
        
        output = result.content[0].text if result.content else ""
        return output

    async def process_single_file(self, target_file_path: str, result_dir: str):
        target_filename = os.path.basename(target_file_path)
        module_name = os.path.splitext(target_filename)[0]
        test_filename = f"test_{module_name}.py"
        test_file_path = f"{result_dir}/{test_filename}"
        
        print(f"\n{'='*60}")
        print(f" 🚀 PROCESSING: {target_filename}")
        print(f"{'='*60}")
        
        target_content = await self.execute_tool('read_file', {'file_path': target_file_path})

        messages = [
            {"role": "system", "content": (
                "You are an expert Python QA Engineer. Your goal is 100% Coverage.\n"
                "RULES:\n"
                f"1. Import `{module_name}` directly.\n"
                "2. TRUST THE CODE: If `assert` fails, update your test expectation.\n"
                "3. MISSING LINES: Pay attention to the `Missing` lines in the report.\n"
                "4. DO NOT COPY original source code into test file.\n"
                "5. Fix SyntaxErrors immediately."
            )},
            {"role": "user", "content": f"Target Code (`{target_filename}`):\n```python\n{target_content}\n```\nWrite `{test_filename}`."}
        ]
        
        current_best = 0
        
        for attempt in range(1, MAX_RETRIES + 1):
            print(f"\n[Attempt {attempt}/{MAX_RETRIES}] Generating test...")

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
                best_path = f"best_coverages/{test_filename}"
                content = await self.execute_tool('read_file', {'file_path': test_file_path})
                await self.execute_tool('write_file', {'file_path': best_path, 'content': content})
            else:
                print(f"  📉 Score: {score}%")

            if score >= TARGET_COVERAGE:
                print(f"  🎉 SUCCESS! 100% Coverage.")
                break

            feedback = (
                f"Coverage Report:\n{cov_output}\n\n"
                f"Pytest Output:\n{run_output[:1000]}\n"
                "Analyze the 'Missing' lines in the report and add tests."
            )
            messages.append({"role": "user", "content": feedback})

    async def run_task2(self):
        files_str = await self.execute_tool('list_files', {})
        try:
            target_files = eval(files_str)
        except:
            target_files = []
            print(f"Error parsing file list: {files_str}")
        
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