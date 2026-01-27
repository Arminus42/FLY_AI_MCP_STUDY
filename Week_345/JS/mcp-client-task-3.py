import asyncio
import argparse
import json
import os
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI
from dotenv import load_dotenv
from openai.types.chat import (
    ChatCompletionToolMessageParam,
    ChatCompletionToolParam,
)
from openai.types.shared_params.function_definition import FunctionDefinition

load_dotenv()

# Simplified System Prompt
SYSTEM_PROMPT = """
You are a QA Automation Agent specialized in SBST. 
Your ONLY task is to call the `run_sbst` tool for the requested example file.
Do not write code. Do not analyze. Just run the tool.
"""

class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.llm = OpenAI()
        self.messages = []
        self.trajectory_log = []

    async def connect_to_server(self, server_script_path: str):
        print(f"Connecting to server: {server_script_path}...")
        server_params = StdioServerParameters(command="python", args=[server_script_path], env=None)
        
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        
        await self.session.initialize()
        print("Connected.")

    async def cleanup(self): 
        await self.exit_stack.aclose()

    def log_trajectory(self, role, content):
        """Accumulate logs for the trajectory file."""
        entry = f"[{role.upper()}]\n{content}\n"
        self.trajectory_log.append(entry)
        
        # Color output for console
        if role == "tool_result":
            print(f"\033[92m{entry.strip()}\033[0m")
        elif role == "assistant":
            print(f"\033[94m{entry.strip()}\033[0m")
        else:
            print(entry.strip())

    async def process_messages(self, messages: list):
        if not self.session:
            raise RuntimeError("Session not initialized.")

        # 1. Get Tools
        response = await self.session.list_tools()
        available_tools = [ChatCompletionToolParam(type="function", function=FunctionDefinition(
            name=t.name, description=t.description or "", parameters=t.inputSchema
        )) for t in response.tools]

        # 2. Call LLM
        response = self.llm.chat.completions.create(
            model="gpt-4o-mini", messages=messages, tools=available_tools, tool_choice="auto"
        )
        msg = response.choices[0].message

        # 3. Handle Response
        if msg.tool_calls:
            messages.append(msg)
            tool_names = [tc.function.name for tc in msg.tool_calls]
            self.log_trajectory("assistant", f"Tool Call: {tool_names}")
            
            tool_results = []
            for tc in msg.tool_calls:
                try: 
                    args = json.loads(tc.function.arguments)
                except: 
                    args = {}
                
                # Execute Tool
                result = await self.session.call_tool(tc.function.name, args)
                content = result.content[0].text if result.content else ""
                
                tool_results.append(ChatCompletionToolMessageParam(
                    role="tool", content=content, tool_call_id=tc.id
                ))
                self.log_trajectory("tool_result", f"{tc.function.name} -> {content}")

            messages.extend(tool_results)
            # Recursively let LLM confirm
            return await self.process_messages(messages)
        
        else:
            messages.append(msg)
            self.log_trajectory("assistant", msg.content)
            return messages

    async def run_for_example(self, example_name):
        print(f"\n\033[1m=== Processing {example_name} ===\033[0m")
        
        # Reset logs for this specific file
        self.trajectory_log = []
        self.messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Run SBST for {example_name}."}
        ]
        
        await self.process_messages(self.messages)
        
        # Save Trajectory File
        os.makedirs("trajectory", exist_ok=True)
        traj_path = os.path.join("trajectory", f"trajectory_{example_name}.txt")
        with open(traj_path, "w") as f:
            f.write("\n".join(self.trajectory_log))
        print(f"Trajectory saved to {traj_path}")

async def main(server_path):
    client = MCPClient()
    try:
        await client.connect_to_server(server_path)
        
        # Task 3 targets only
        targets = ["example1", "example2", "example3"]
        
        for target in targets:
            await client.run_for_example(target)
            
    finally:
        await client.cleanup()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('server_script_path', type=str)
    args = parser.parse_args()
    
    asyncio.run(main(args.server_script_path))