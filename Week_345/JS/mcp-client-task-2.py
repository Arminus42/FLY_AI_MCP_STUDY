import asyncio
import argparse
import json
import sys
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI
from dotenv import load_dotenv
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageToolCallParam,
    ChatCompletionToolMessageParam,
    ChatCompletionToolParam,
)
from openai.types.shared_params.function_definition import FunctionDefinition

load_dotenv()

SYSTEM_PROMPT = """
You are an elite QA Automation Engineer. 
Your goal is to achieve 100% test coverage.
Always analyze the provided code context carefully before writing tests.
Do not use any other packages than pytest.
Do not use classes.
However, always write tests so that they are function of a series of asserts.
"""

# --- Logging Helpers ---
def log_tool_call(name, args):
    print(f"\n\033[94m[LLM-DECISION] Calling Tool: {name}\033[0m")
    print(f"\033[94m   Args: {args}\033[0m")

def log_tool_result(name, result):
    snippet = str(result).replace("\n", "\\n")
    if len(snippet) > 150: snippet = snippet[:150] + "..."
    print(f"\033[92m[TOOL-RESULT] {name} -> {snippet}\033[0m")

def log_step(step_name):
    print(f"\n\033[93m=== {step_name} ===\033[0m")

class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.llm = OpenAI()
        self.messages = []

    async def connect_to_server(self, server_script_path: str):
        print(f"Connecting to server: {server_script_path}...")
        server_params = StdioServerParameters(command="python", args=[server_script_path], env=None)
        
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        
        await self.session.initialize()
        
        response = await self.session.list_tools()
        print("\nConnected to server with tools:", [tool.name for tool in response.tools])

    async def cleanup(self): 
        await self.exit_stack.aclose()

    async def process_messages(self, messages: list):
        if not self.session:
            raise RuntimeError("Session not initialized. Call connect_to_server() first.")

        response = await self.session.list_tools()
        available_tools = [ChatCompletionToolParam(type="function", function=FunctionDefinition(
            name=t.name, description=t.description or "", parameters=t.inputSchema
        )) for t in response.tools]

        response = self.llm.chat.completions.create(
            model="gpt-5.2", messages=messages, tools=available_tools, tool_choice="auto"
        )
        finish_reason = response.choices[0].finish_reason

        if finish_reason == "stop":
            content = response.choices[0].message.content
            print(f"\n[ASSISTANT] {content}")
            messages.append(ChatCompletionAssistantMessageParam(role="assistant", content=content))
        elif finish_reason == "tool_calls":
            tool_calls = response.choices[0].message.tool_calls
            messages.append(ChatCompletionAssistantMessageParam(
                role="assistant",
                tool_calls=[ChatCompletionMessageToolCallParam(
                    id=tc.id, function=tc.function, type=tc.type
                ) for tc in tool_calls]
            ))
            tasks = []
            for tc in tool_calls:
                log_tool_call(tc.function.name, tc.function.arguments)
                tasks.append(asyncio.create_task(self.process_tool_call(tc)))
            tool_results = await asyncio.gather(*tasks)
            messages.extend(tool_results)
            return await self.process_messages(messages)
        return messages

    async def process_tool_call(self, tool_call) -> ChatCompletionToolMessageParam:
        try: args = json.loads(tool_call.function.arguments)
        except: args = {}
        try:
            res = await self.session.call_tool(tool_call.function.name, args)
            content = res.content[0].text if res.content else ""
        except Exception as e: content = f"Error: {e}"
        log_tool_result(tool_call.function.name, content)
        return ChatCompletionToolMessageParam(role="tool", content=content, tool_call_id=tool_call.id)

    async def workflow_loop(self):
        log_step("Phase 1: Initialization")
        self.messages = [
            {"role": "system", "content": SYSTEM_PROMPT },
            {"role": "user", "content": "Call init_queue() to start."}
        ]
        self.messages = await self.process_messages(self.messages)

        # MAIN LOOP: Iterate over files
        while True:
            # --- PHASE 2: Fetch Task ---
            # We clear messages here to ensure a fresh context for each file
            self.messages = [
                {"role": "system", "content": SYSTEM_PROMPT },
                {"role": "user", "content": "Call next_task() to start."}
            ] 
            log_step("Phase 2: Fetching Task")
            
            self.messages = [{"role": "user", "content": "If 'QUEUE_EMPTY', reply 'FINISHED'. Else summarize code."}]
            self.messages = await self.process_messages(self.messages)
            
            # Check for FINISHED signal
            last_content = ""
            if self.messages and self.messages[-1].get('content'):
                last_content = self.messages[-1]['content']

            if "FINISHED" in last_content or "QUEUE_EMPTY" in last_content:
                print("All tasks completed.")
                break

            # --- PHASE 3: Generate Tests (Hill Climbing) ---
            fails_in_a_row = 0
            log_step("Phase 3: Generating Tests")
            
            while fails_in_a_row < 3:
                step_prompt = """
                1. Call get_current_status().
                2. If coverage is 100%, reply "DONE".
                3. Call get_uncovered_context(context=2).
                4. Write ONE new pytest function to cover lines.
                5. Call submit_test_case().
                """
                self.messages.append({"role": "user", "content": step_prompt})
                self.messages = await self.process_messages(self.messages)
                
                # Check results
                last_tool_res = ""
                last_assistant_text = ""
                for m in reversed(self.messages):
                    if m.get('role') == 'tool': 
                        last_tool_res = m.get('content', '')
                        if "ACCEPTED" in last_tool_res or "REJECTED" in last_tool_res: break
                    if m.get('role') == 'assistant' and m.get('content'):
                        last_assistant_text = m['content']
                
                if "ACCEPTED" in last_tool_res: 
                    fails_in_a_row = 0
                elif "REJECTED" in last_tool_res: 
                    fails_in_a_row += 1
                elif "DONE" in last_assistant_text: 
                    break
                else: 
                    fails_in_a_row += 1

            # --- PHASE 4: Finalize Task ---
            log_step("Phase 4: Finalizing Task")
            self.messages.append({"role": "user", "content": "Call finalize_task()."})
            await self.process_messages(self.messages)
            
            # The loop naturally continues back to Phase 2 (Fetch Task)

async def main(server_path):
    client = MCPClient()
    try:
        await client.connect_to_server(server_path)
        await client.workflow_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('server_script_path', type=str)
    args = parser.parse_args()
    
    asyncio.run(main(args.server_script_path))