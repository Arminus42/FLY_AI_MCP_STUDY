import asyncio
import json
import argparse
import traceback
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI
from dotenv import load_dotenv
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionMessageToolCallParam,
    ChatCompletionToolMessageParam,
    ChatCompletionToolParam,
)
from openai.types.chat.chat_completion_message_tool_call_param import Function
from openai.types.shared_params.function_definition import FunctionDefinition

# 환경 변수 로드 
load_dotenv()


async def main(server_script_path: str, prompt: str):
    """
    MCP 클라이언트 메인 함수
    
    Args:
        server_script_path: MCP 서버 스크립트 경로
        prompt: 처리할 사용자 프롬프트
    """
    client = MCPClient()
    try:
        # 서버 연결
        await client.connect_to_server(server_script_path)
        # 프롬프트 처리
        await client.workflow_loop(prompt)
    finally:
        # 리소스 정리
        await client.cleanup()


class MCPClient:
    """
    MCP 서버와 통신하며 LLM과 Tool을 연동하는 클라이언트
    
    주요 역할:
    1. MCP 서버와 STDIO 연결 수립
    2. LLM에게 사용 가능한 Tool 목록 전달
    3. LLM이 요청한 Tool 호출 실행
    4. Tool 결과를 LLM에게 다시 전달
    """
    
    def __init__(self):
        self.session: Optional[ClientSession] = None  # MCP 서버 세션
        self.exit_stack = AsyncExitStack()  # 비동기 리소스 관리
        self.llm = OpenAI()  # OpenAI LLM 클라이언트
        self.messages = []  # 대화 메시지 히스토리

    async def connect_to_server(self, server_script_path: str):
        """
        MCP 서버에 연결
        
        STDIO 트랜스포트를 사용하여 서버 프로세스 시작 및 연결
        서버는 표준 입출력을 통해 JSON-RPC 메시지로 통신
        
        Args:
            server_script_path: 서버 스크립트 파일 경로
        """
        # 서버 실행 파라미터 설정
        server_params = StdioServerParameters(
            command="python",  # Python으로 서버 실행
            args=[server_script_path],  # 서버 스크립트 경로
            env=None  # 환경 변수 (None이면 현재 환경 상속)
        )

        # STDIO 트랜스포트 설정
        # 서버 프로세스를 시작하고 stdin/stdout으로 통신 채널 생성
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = stdio_transport
        
        # MCP 세션 초기화
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )

        # 서버와 핸드셰이크 (프로토콜 버전 협상 등)
        await self.session.initialize()

        # 서버가 제공하는 Tool 목록 조회
        response = await self.session.list_tools()
        tools = response.tools
        print(f"\n서버 연결 완료. 사용 가능한 Tool: {[tool.name for tool in tools]}")

    async def cleanup(self):
        """리소스 정리 (연결 종료, 서버 프로세스 종료 등)"""
        await self.exit_stack.aclose()

    async def process_messages(self, messages: list[ChatCompletionMessageParam]):
        """
        LLM에게 메시지를 전달하고 Tool 호출을 처리하는 재귀 함수
        
        동작 흐름:
        1. 서버로부터 사용 가능한 Tool 목록 조회
        2. LLM에게 메시지와 Tool 목록 전달
        3. LLM 응답에 따라 분기:
           - finish_reason == "stop": 최종 응답 생성 완료
           - finish_reason == "tool_calls": Tool 호출 요청
        4. Tool 호출 시: Tool 실행 → 결과를 메시지에 추가 → 재귀 호출
        
        Args:
            messages: 대화 메시지 히스토리
        
        Returns:
            업데이트된 메시지 리스트
        """
        
        # 서버로부터 사용 가능한 Tool 목록 가져오기
        response = await self.session.list_tools()
        available_tools = [
            ChatCompletionToolParam(
                type="function",
                function=FunctionDefinition(
                    name=tool.name,
                    description=tool.description if tool.description else "",
                    parameters=tool.inputSchema  # JSON Schema 형식
                )
            ) for tool in response.tools
        ]

        # LLM에게 메시지와 Tool 목록 전달
        response = self.llm.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=available_tools,
            tool_choice="auto"  # LLM이 자동으로 Tool 사용 여부 결정
        )

        finish_reason = response.choices[0].finish_reason

        # Case 1: LLM이 최종 응답을 생성한 경우
        if finish_reason == "stop":
            messages.append(
                ChatCompletionAssistantMessageParam(
                    role="assistant",
                    content=response.choices[0].message.content
                )
            )

        # Case 2: LLM이 Tool 호출을 요청한 경우
        elif finish_reason == "tool_calls":
            tool_calls = response.choices[0].message.tool_calls
            assert tool_calls is not None
            
            # Tool 호출 로깅 (어떤 Tool을 호출하는지 출력)
            for tool_call in tool_calls:
                print(f"Tool 호출: {tool_call.function.name}")
            
            # LLM의 Tool 호출 요청을 메시지에 추가
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
            
            # 모든 Tool을 병렬로 실행 (asyncio.gather 사용)
            tasks = [
                asyncio.create_task(self.process_tool_call(tool_call))
                for tool_call in tool_calls
            ]
            tool_results = await asyncio.gather(*tasks)
            messages.extend(tool_results)
            
            # Tool 결과를 포함하여 다시 LLM 호출 (재귀)
            return await self.process_messages(messages)

        # Case 3: 에러 상황
        elif finish_reason == "length":
            raise ValueError(
                f"토큰 한도 초과 ({response.usage.total_tokens} 토큰). "
                "더 짧은 프롬프트를 사용해주세요."
            )
        elif finish_reason == "content_filter":
            raise ValueError("콘텐츠 필터 발동. 다른 프롬프트를 사용해주세요.")
        else:
            raise ValueError(f"알 수 없는 종료 이유: {finish_reason}")

        return messages

    async def process_tool_call(self, tool_call) -> ChatCompletionToolMessageParam:
        """
        개별 Tool 호출을 실행하고 결과를 반환
        
        동작:
        1. Tool 이름과 인자 추출
        2. MCP 서버의 Tool 실행
        3. 결과를 LLM에게 전달할 형식으로 변환
        
        Args:
            tool_call: LLM이 요청한 Tool 호출 정보
        
        Returns:
            Tool 실행 결과 메시지
        """
        assert tool_call.type == "function"

        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)
        
        # MCP 서버의 Tool 실행
        call_tool_result = await self.session.call_tool(tool_name, tool_args)

        # Tool 실행 실패 시 에러 처리
        if call_tool_result.isError:
            raise ValueError(f"Tool 실행 실패: {call_tool_result.content}")

        # 결과 수집 (텍스트만 지원)
        results = []
        for result in call_tool_result.content:
            if result.type == "text":
                results.append(result.text)
            else:
                raise NotImplementedError(f"지원하지 않는 결과 타입: {result.type}")

        # Tool 결과를 LLM에게 전달할 형식으로 변환
        # role="tool"로 설정하여 Tool 실행 결과임을 명시
        return ChatCompletionToolMessageParam(
            role="tool",
            content=json.dumps({**tool_args, tool_name: results}),
            tool_call_id=tool_call.id
        )

    async def workflow_loop(self, prompt: str):
        """
        사용자 프롬프트 처리 및 최종 응답 출력
        
        Args:
            prompt: 사용자 프롬프트
        """
        print(f"\n프롬프트 처리 중: {prompt}\n")

        # 초기 메시지 (사용자 프롬프트)
        self.messages = [{"role": "user", "content": prompt}]

        try:
            # LLM과 Tool 호출을 반복하며 메시지 처리
            self.messages = await self.process_messages(self.messages)

            # 최종 응답 출력
            for msg in self.messages:
                if msg.get("role") == "assistant" and msg.get("content"):
                    print("\n" + "=" * 50)
                    print("최종 응답:")
                    print("=" * 50)
                    print(msg["content"])
                    print("=" * 50)

        except Exception as e:
            print(f"오류 발생: {e}")
            traceback.print_exc()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MCP 클라이언트")
    parser.add_argument('server_script_path', type=str, help="서버 스크립트 경로 (.py)")
    parser.add_argument('prompt', type=str, help="처리할 프롬프트")
    args = parser.parse_args()

    # 비동기 메인 함수 실행
    asyncio.run(main(args.server_script_path, args.prompt))