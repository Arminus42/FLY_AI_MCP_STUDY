import asyncio
from typing import Optional
from contextlib import AsyncExitStack
from datetime import datetime

# MCP 표준 라이브러리 (클라이언트 세션, STDIO 통신 모듈)
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from openai import OpenAI
from dotenv import load_dotenv

# OpenAI API 요청/응답 Type Hinting
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

# .env에서 환경 변수 로드
load_dotenv(override=True)

async def main(server_script_path: str, prompt: str):
    client = MCPClient()

    try:
        await client.connect_to_server(server_script_path) # MCP 서버와 연결
        await client.workflow_loop(prompt) # 유저 프롬프트를 처리하는 메인 loop 실행
    finally:
        await client.cleanup() # 서버 종료 시 리소스 정리


class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack() # 비동기 컨텍스트 매니저들을 한 번에 관리하기 위한 스택
        self.llm = OpenAI() # OpenAI 클라이언트 인스턴스
        self.messages = [] # 대화 히스토리 저장소

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        # 서버 실행 명령 설정: "python <script_path>" 형태로 서브 프로세스 실행 준비
        server_params = StdioServerParameters(
            command="python",
            args=[server_script_path],
            env=None
        )

        # stdio_client 컨텍스트에 진입하여 통신 통로(Transport) 생성
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        
        # Transport 위에 MCP ClientSession 생성 (프로토콜 레벨의 통신)
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
       
        # 세션 초기화
        await self.session.initialize()

        # 서버에 연결된 Tool 목록 조회
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])


    async def cleanup(self):
        await self.exit_stack.aclose() # 모든 비동기 컨텍스트 매니저 역순으로 종료 (세션->transport->프로세스 종료)

    async def process_messages(self, messages: list[ChatCompletionMessageParam], depth: int = 0):
        """Process a query and return the response"""

        # 무한 루프 방지용 깊이 제한
        if depth > 10:
            print("\n[System] Loop limit reached. Stopping execution to prevent infinite loop.")
            return messages

        # 1. 현재 사용 가능한 tool 목록을 다시 가져와서 OpenAI API 형식으로 변환
        response = await self.session.list_tools()
        available_tools = [ChatCompletionToolParam(
            type="function",
            function=FunctionDefinition(
                name=tool.name,
                description=tool.description if tool.description else "",
                parameters=tool.inputSchema
            )
        ) for tool in response.tools]

        # 2. OpenAI API 호출
        response = self.llm.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=available_tools,
            tool_choice="auto"
        )

        # 3. LLM의 응답 분석
        finish_reason = response.choices[0].finish_reason

        # 3-1. 종료조건: LLM이 최종 답변 생성
        if finish_reason == "stop": 
            messages.append(
                ChatCompletionAssistantMessageParam(
                    role="assistant",
                    content=response.choices[0].message.content
                )
            )

        # 3-2. 재귀조건: LLM이 도구 사용 요청
        elif finish_reason == "tool_calls":
            tool_calls = response.choices[0].message.tool_calls
            assert tool_calls is not None
            
            # 디버그 출력
            for tool_call in tool_calls:
                #print(tool_call.function.name)
                print("-"*80)
                print(f"\n[LLM Request] Tool: {tool_call.function.name}")
                print(f"              Args: {tool_call.function.arguments}")
                print("")
                
            # LLM의 요청을 대화 기록에 추가
            messages.append(
                ChatCompletionAssistantMessageParam(
                    role="assistant",
                    tool_calls=[
                        ChatCompletionMessageToolCallParam(
                            id=tool_call.id,
                            function=Function(
                                arguments=tool_call.function.arguments,
                                name=tool_call.function.name
                            ),
                            type=tool_call.type,
                        )
                        for tool_call in tool_calls
                    ]
                )
            )
            
            # 실제 도구 실행 (비동기 병렬 처리 가능)
            tasks = [
                asyncio.create_task(self.process_tool_call(tool_call))
                for tool_call in tool_calls
            ]
            
            messages.extend(await asyncio.gather(*tasks)) # 도구 실행 결과를 기다림
            return await self.process_messages(messages, depth = depth + 1) # 도구 실행 결과를 포함해 다시 LLM에게 요청
        
        # 예외 처리
        elif finish_reason == "length":
            raise ValueError(f"[ERROR] Length limit reached ({response.usage.total_tokens} tokens). Please try a shorter query.")

        elif finish_reason == "content_filter":
            raise ValueError("[ERROR] Content filter triggered. Please try a different query.")

        elif finish_reason == "function_call":
            raise ValueError("[ERROR] Deprecated API usage. LLM should use tool_calls instead.")

        else:
            raise ValueError(f"[ERROR] Unknown finish reason: {finish_reason}")

        return messages

    # LLM의 요청을 받아 실제 MCP 서버에 RPC 호출을 수행 및 결과 반환
    async def process_tool_call(self, tool_call) -> ChatCompletionToolMessageParam:
        assert tool_call.type == "function"

        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments) # LLM이 전달한 인자를 JSON으로 파싱
        call_tool_result = await self.session.call_tool(tool_name, tool_args) # MCP 세션을 통해 서버의 함수 실행

        if call_tool_result.isError:
            raise ValueError(f"[ERROR] Tool call failed: {call_tool_result.content}")

        # 결과 처리 (텍스트만 처리하도록 구현됨)
        results = []
        for result in call_tool_result.content:
            if result.type == "text":
                results.append(result.text)
            else:   # image, resource, etc.
                raise NotImplementedError(f"Unsupported result type: {result.type}")
        
        # 디버깅 출력
        #print(f"[Tool Output] Result: {results[:200]}...")

        # OpenAI에 돌려줄 "tool" 역할의 메시지 생성
        return ChatCompletionToolMessageParam(
            role="tool",
            content=json.dumps({
                **tool_args,
                tool_name: results
            }),
            tool_call_id=tool_call.id
        )

    # 메인 워크플로우 루프
    async def workflow_loop(self, prompt:str):
        print("Welcome to the MCP Client!")

        self.messages = []

        # 타임스탬프 폴더명 생성 (results_YYYYMMDDHHMMSS)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        result_dir_name = f"results_{timestamp}"

        # [Prompt] LLM에게 테스트 파일 생성 및 저장 규칙을 강제하는 System Prompt
        system_instruction = (
            f"You are an automated testing assistant.\n"
            f"RULES:\n"
            f"1. SOURCE & DESTINATION: Read from 'targets' and save generated tests ONLY to the new '{result_dir_name}' directory. Never modify 'targets'.\n"
            f"2. PATH SETUP: The test file and target file are in different directories. To import correctly, your generated code MUST add the target file's directory to `sys.path` before importing.\n"
            f"   - Use relative path logic: `sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../targets/TARGET_FOLDER_NAME')))`\n"
            f"3. IMPORT STYLE: After setting the path, use simple imports like `import example1` (do NOT use package paths like `example1.example1`).\n"
            f"4. STOP condition: Output a final confirmation message and STOP after writing the files."
        )

        
        # [Prompt] 시스템 메시지를 대화 기록 맨 앞에 추가
        self.messages.append({"role": "system", "content": system_instruction})

        user_input = prompt

        self.messages.append({"role":"user", "content":user_input}) # 유저 메시지 추가

        try:
            self.messages = await self.process_messages(self.messages) # 메시지 처리

            if self.messages:
                last_msg = self.messages[-1]
                if last_msg.get("role") == "assistant" and last_msg.get("content"):
                    print("-"*50)
                    print("Final Answer")
                    print("-"*50)
                    print(self.messages[-1].get("content"))

        except Exception as e:
            print(f"Error processing user input: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    
    # 명령줄 인자 파싱
    parser = argparse.ArgumentParser(description="MCP Client for connecting to a server.")
    parser.add_argument('server_script_path', help="Path to the server script (.py or .js)", type=str)
    parser.add_argument('prompt', type=str)
    args = parser.parse_args()

    # 메인 비동기 함수 실행
    asyncio.run(main(args.server_script_path, args.prompt))

    pass

    