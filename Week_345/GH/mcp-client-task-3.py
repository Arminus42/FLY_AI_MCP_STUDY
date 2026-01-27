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


load_dotenv()

class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

    # 서버 실행 및 세션 초기화
    async def connect(self, server_script_path: str):
        server_params = StdioServerParameters(
            command="python",
            args=[server_script_path],
            env=None
        )
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        # 표준입출력으로 쓰고 읽음
        # transport = 클라이언트와 서버가 데이터를 주고받는 통신 통로
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        # 도구 호출 준비 상태로 만들기
        await self.session.initialize()

    async def close(self):
        await self.exit_stack.aclose()

    async def run_all(self):
        assert self.session is not None

        for target in ["example1.py", "example2.py", "example3.py"]: # 해당 파일만
            res = await self.session.call_tool("run_sbst", {"target": target}) # 3번 호출
            if res.isError:
                raise RuntimeError(res.content)

            texts = [c.text for c in res.content if c.type == "text"]
            print(f"{target}: {texts[0] if texts else res.content}")

# 연결 - 실행 - 정리
async def main(server_script_path: str):
    c = MCPClient()
    try:
        await c.connect(server_script_path)
        await c.run_all()
    finally:
        await c.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("server_script_path", type=str)
    args = parser.parse_args()

    asyncio.run(main(args.server_script_path))
