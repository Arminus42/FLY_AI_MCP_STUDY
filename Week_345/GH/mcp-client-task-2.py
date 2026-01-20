import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from openai import OpenAI
from dotenv import load_dotenv

from openai.types.chat import (
    ChatCompletionUserMessageParam,
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionMessageToolCallParam,
    ChatCompletionToolMessageParam,
    ChatCompletionToolParam,
)

from openai.types.chat.chat_completion_message_tool_call_param import Function
from openai.types.shared_params.function_definition import FunctionDefinition

import json
import argparse

import traceback

import time
import datetime


load_dotenv()

class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.llm = OpenAI()
        self.messages = []

    async def connect_to_server(self, server_script_path: str):
        server_params = StdioServerParameters(command="python", args=[server_script_path], env=None)
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await self.session.initialize()
        response = await self.session.list_tools()
        print("\nConnected to server with tools:", [tool.name for tool in response.tools])

    async def cleanup(self):
        await self.exit_stack.aclose()

    # [수정] 도구 호출 없이 순수 텍스트(코드)만 LLM으로부터 받아오는 함수
    async def get_llm_code(self, prompt: str):
        response = self.llm.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            # tools 인자를 생략하여 LLM이 도구 호출을 하지 못하게 함
        )
        return response.choices[0].message.content

    def clean_code(self, text):
        if "```" in text:
            parts = text.split("```")
            for part in parts:
                if part.strip().startswith("python"):
                    return part.replace("python", "", 1).strip()
                if len(part.strip()) > 0 and ("import" in part or "def" in part):
                    return part.strip()
        return text.strip()

    async def workflow_loop(self, initial_prompt: str):
        print("Coverage-driven Test Generation start...")
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        folder_name = f"task2_results_{timestamp}"
        
        # 파일 목록 직접 호출
        file_list_resp = await self.session.call_tool("list_files", {})
        target_files = [f.strip() for f in file_list_resp.content[0].text.split('\n') if f.strip()]
        
        final_coverages = {}
        for target_file in target_files:
            print(f"\n--- {target_file} processing ---")
            best_cov = 0
            no_improvement_count = 0
            module_name = target_file.replace(".py", "")
            test_file_name = f"test_{target_file}"
            
            code_resp = await self.session.call_tool("read_file", {"file_path": target_file})
            source_code = code_resp.content[0].text
            
            for attempt in range(1, 11):
                print(f"[{target_file}] Attempt {attempt}...")
                
                prompt = f"""[SYSTEM: STRICT CODE ONLY MODE]
대상 코드:
{source_code}

위 코드를 위한 pytest 파일을 작성해줘. 
- 파일명: {test_file_name}
- 반드시 `import {module_name}` 형식을 사용할 것.
- 현재 최고 커버리지: {best_cov}%
- 인사말, 설명, 마크다운(```python) 없이 코드만 출력해.
"""
                raw_content = await self.get_llm_code(prompt)
                test_code = self.clean_code(raw_content)
                
                if not test_code or len(test_code) < 10:
                    print("Code generation failed. Retrying...")
                    continue

                # 파일 저장
                await self.session.call_tool("save_test_file", {
                    "file_name": test_file_name, "content": test_code, "folder_name": folder_name
                })
                
                # 측정
                cov_resp = await self.session.call_tool("run_pytest_and_coverage", {
                    "test_file_path": test_file_name, "target_file_name": target_file
                })
                cov_result = json.loads(cov_resp.content[0].text)
                current_cov = cov_result.get("coverage", 0)
                print(f"Current Coverage: {current_cov}% (Best: {best_cov}%)")

                if current_cov > best_cov:
                    best_cov = current_cov
                    no_improvement_count = 0
                else:
                    no_improvement_count += 1

                if current_cov >= 100 or no_improvement_count >= 3:
                    break
            
            final_coverages[module_name] = best_cov

        await self.session.call_tool("finalize_results", {"coverage_data": json.dumps(final_coverages)})
        print(f"Final results: {final_coverages}")

async def main(server_script_path: str, prompt: str):
    client = MCPClient()
    try:
        await client.connect_to_server(server_script_path)
        await client.workflow_loop(prompt)
    finally:
        await client.cleanup()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('server_script_path')
    parser.add_argument('prompt')
    args = parser.parse_args()
    asyncio.run(main(args.server_script_path, args.prompt))
