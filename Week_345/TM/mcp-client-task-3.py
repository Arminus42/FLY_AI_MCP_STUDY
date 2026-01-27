import asyncio
import os
import json
import argparse
import traceback
import time
from datetime import datetime
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
from openai.types.chat.chat_completion_message_tool_call_param import Function

load_dotenv(override=True)

class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.llm = OpenAI()
        self.messages = []
        self.tool_trajectory = [] 
        self.api_call_count = 0  # LLM 요청 횟수 카운터

    async def connect_to_server(self, server_script_path: str):
        server_params = StdioServerParameters(
            command="python",
            args=[server_script_path],
            env=None
        )
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await self.session.initialize()

    async def cleanup(self):
        await self.exit_stack.aclose()

    async def process_messages(self, messages: list):
        response = await self.session.list_tools()
        available_tools = [ChatCompletionToolParam(
            type="function",
            function=FunctionDefinition(
                name=tool.name,
                description=tool.description if tool.description else "",
                parameters=tool.inputSchema
            )
        ) for tool in response.tools]

        # LLM API 요청 카운트 증가
        self.api_call_count += 1
        
        response = self.llm.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=available_tools,
            tool_choice="auto"
        )

        finish_reason = response.choices[0].finish_reason

        if finish_reason == "stop":
            messages.append(ChatCompletionAssistantMessageParam(
                role="assistant",
                content=response.choices[0].message.content
            ))

        elif finish_reason == "tool_calls":
            tool_calls = response.choices[0].message.tool_calls
            
            messages.append(ChatCompletionAssistantMessageParam(
                role="assistant",
                tool_calls=[
                    ChatCompletionMessageToolCallParam(
                        id=tc.id,
                        function=Function(arguments=tc.function.arguments, name=tc.function.name),
                        type=tc.type
                    ) for tc in tool_calls
                ]
            ))

            for tc in tool_calls:
                print(f"[Tool Call] {tc.function.name}")
                self.tool_trajectory.append(tc.function.name)

            tasks = [asyncio.create_task(self.process_tool_call(tc)) for tc in tool_calls]
            messages.extend(await asyncio.gather(*tasks))
            return await self.process_messages(messages)

        return messages

    async def process_tool_call(self, tool_call) -> ChatCompletionToolMessageParam:
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)
        
        result = await self.session.call_tool(tool_name, tool_args)
        
        content = []
        if not result.isError:
            for item in result.content:
                if item.type == "text":
                    content.append(item.text)
        else:
            content.append(f"Error: {result.content}")

        return ChatCompletionToolMessageParam(
            role="tool",
            content=json.dumps({**tool_args, "result": content}),
            tool_call_id=tool_call.id
        )

    async def run_single_task(self, prompt: str, trajectory_file: str):
        """단일 작업 수행 및 성능 측정"""
        self.messages = [{"role": "user", "content": prompt}]
        self.tool_trajectory = [] 
        self.api_call_count = 0
        
        start_time = time.time() # 시간 측정 시작

        print(f"\n--- Starting Task: {os.path.basename(trajectory_file)} ---")
        try:
            await self.process_messages(self.messages)
            
            end_time = time.time() # 시간 측정 종료
            elapsed_time = end_time - start_time
            
            # 성능 지표 메시지 생성
            metrics_log = (
                f"Task Completed.\n"
                f"- Execution Time: {elapsed_time:.2f} sec\n"
                f"- LLM Requests: {self.api_call_count}\n"
                f"- Execution Time/LLM Requests: {elapsed_time/self.api_call_count:.2f}\n"
                f"- Tool Calls: {len(self.tool_trajectory)}\n"
            )
            print(metrics_log)
            
            # Trajectory 및 성능 지표 저장
            os.makedirs(os.path.dirname(trajectory_file), exist_ok=True)
            with open(trajectory_file, "w") as f:
                f.write("\n".join(self.tool_trajectory))
                f.write(f"\n\n[Performance Metrics]\n{metrics_log}")
            
            print(f"Trajectory saved to {trajectory_file}")
            
        except Exception as e:
            print(f"Error: {e}")
            traceback.print_exc()

async def main(server_script_path: str):
    client = MCPClient()
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    results_dir = f"task3_results_{timestamp}"
    trajectory_dir = "trajectory"
    
    await client.connect_to_server(server_script_path)
    
    try:
        targets = ["example1.py", "example2.py", "example3.py"]
        
        for target in targets:
            target_name = os.path.splitext(target)[0]
            
            test_file_path = os.path.join(results_dir, f"test_{target}")
            trajectory_file_path = os.path.join(trajectory_dir, f"trajectory_{target_name}.txt")
            
            # 프롬프트 엔지니어링
            prompt = (
                f"Please generate unit tests for the Python file '{target}' using the Search-Based Software Testing (SBST) approach. "
                f"After the test code is generated, save it to the file path '{test_file_path}'. "
                f"Ensure that the saved test file includes the necessary 'sys.path' setup so that it can correctly import the target module."
            )
            
            await client.run_single_task(prompt, trajectory_file_path)

    finally:
        await client.cleanup()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('server_script_path', type=str)
    args, unknown = parser.parse_known_args()
    
    asyncio.run(main(args.server_script_path))