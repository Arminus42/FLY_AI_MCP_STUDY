import asyncio
import sys
import time
import ast  # 문자열로 된 리스트 파싱용
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from openai import OpenAI, RateLimitError
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

import json
import argparse
import traceback

load_dotenv()

class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.llm = OpenAI()
        self.messages = []
        # 파일 하나당 최대 턴 수 (충분함)
        self.max_retries = 30 

    async def connect_to_server(self, server_script_path: str):
        server_params = StdioServerParameters(
            command=sys.executable,
            args=[server_script_path],
            env=None
        )
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await self.session.initialize()
        
        response = await self.session.list_tools()
        print(f"\n[시스템] 서버 연결 성공. 도구 목록: {[tool.name for tool in response.tools]}")

    async def cleanup(self):
        try:
            await self.exit_stack.aclose()
        except Exception:
            pass

    async def process_messages(self, messages: list[ChatCompletionMessageParam]):
        if len(messages) > self.max_retries:
            print("[시스템] 해당 파일에 대한 최대 시도 횟수 초과. 다음으로 넘어갑니다.")
            return messages

        response = await self.session.list_tools()
        available_tools = [ChatCompletionToolParam(
            type="function",
            function=FunctionDefinition(
                name=tool.name,
                description=tool.description if tool.description else "",
                parameters=tool.inputSchema
            )
        ) for tool in response.tools]

        # ---------------------------------------------------------
        # [핵심] Rate Limit (429) 에러 발생 시 재시도 로직 (Exponential Backoff)
        # ---------------------------------------------------------
        max_api_retries = 5
        for attempt in range(max_api_retries):
            try:
                response_llm = self.llm.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    tools=available_tools,
                    tool_choice="auto"
                )
                break # 성공하면 루프 탈출
            except RateLimitError as e:
                wait_time = (2 ** attempt) + 1  # 2초, 3초, 5초... 늘려감
                print(f"\n[경고] OpenAI Rate Limit 도달! {wait_time}초 후 재시도합니다... ({attempt+1}/{max_api_retries})")
                time.sleep(wait_time)
            except Exception as e:
                print(f"\n[오류] API 호출 중 치명적 오류: {e}")
                raise e
        else:
            print("[오류] 재시도 횟수 초과로 작업을 중단합니다.")
            return messages
        # ---------------------------------------------------------

        finish_reason = response_llm.choices[0].finish_reason
        assistant_message = response_llm.choices[0].message

        if finish_reason == "stop": 
            # LLM이 할 말을 마치면 출력하고 종료 (다음 단계로)
            print(f"\n[AI 응답]: {assistant_message.content}")
            messages.append(
                ChatCompletionAssistantMessageParam(
                    role="assistant",
                    content=assistant_message.content
                )
            )

        elif finish_reason == "tool_calls":
            tool_calls = assistant_message.tool_calls
            assert tool_calls is not None
            
            messages.append(
                ChatCompletionAssistantMessageParam(
                    role="assistant",
                    tool_calls=[
                        ChatCompletionMessageToolCallParam(
                            id=tc.id,
                            function=Function(arguments=tc.function.arguments, name=tc.function.name),
                            type=tc.type,
                        ) for tc in tool_calls
                    ]
                )
            )

            for tool_call in tool_calls:
                print(f"[도구 호출] {tool_call.function.name}({tool_call.function.arguments})")

            # 도구 실행 (병렬 처리)
            tasks = [asyncio.create_task(self.process_tool_call(tc)) for tc in tool_calls]
            tool_results = await asyncio.gather(*tasks)
            messages.extend(tool_results)
            
            # 재귀 호출
            return await self.process_messages(messages)

        return messages

    async def process_tool_call(self, tool_call) -> ChatCompletionToolMessageParam:
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)
        
        try:
            call_tool_result = await self.session.call_tool(tool_name, tool_args)
            if call_tool_result.isError:
                content = f"오류 발생: {call_tool_result.content}"
            else:
                content = call_tool_result.content[0].text
        except Exception as e:
            content = f"도구 실행 예외: {str(e)}"

        preview = content[:150] + "..." if len(content) > 150 else content
        print(f"[도구 결과] {preview}")

        return ChatCompletionToolMessageParam(
            role="tool",
            content=content,
            tool_call_id=tool_call.id
        )

    async def workflow_loop(self, prompt: str):
        print("\n[시스템] 작업을 시작합니다. 대상 모듈 목록을 가져옵니다...")

        # 1. Python 레벨에서 직접 도구를 호출하여 모듈 리스트 확보
        list_result = await self.session.call_tool("list_target_modules", {})
        modules_str = list_result.content[0].text
        
        try:
            # 문자열 "['example1', 'example2']"를 실제 파이썬 리스트로 변환
            target_modules = ast.literal_eval(modules_str)
            print(f"[시스템] 발견된 모듈: {target_modules}")
        except Exception as e:
            print(f"[오류] 모듈 리스트 파싱 실패: {e}")
            return

        # 2. 각 모듈별로 '독립된' 대화 세션 시작 (Context Reset)
        for module_name in target_modules:
            print(f"\n{'='*50}")
            print(f"🚀 [Start] 모듈 처리 시작: {module_name}")
            print(f"{'='*50}")

            # [중요] 메시지 기록 초기화! (이전 파일의 기억을 지워 토큰 절약)
            self.messages = [] 
            
            # [요청하신 Surgical QA 프롬프트 적용]
            system_instruction = f"""
You are a Surgical Python QA Engineer. Your goal is to achieve 100% statement coverage for the '{module_name}' module.

[STRATEGY - FOLLOW STRICTLY]
1. **CRASHES FIRST**: If the test fails to run (ImportError, SyntaxError), fix these errors immediately.
2. **ASSERTION FAILURES**: If an `assert` fails, **TRUST THE SOURCE CODE**. Update your test expectation.
3. **MISSING LINES**: Only add tests for lines specified in the coverage report as "Missing".
4. **NO HALLUCINATIONS**: Do not copy source code or invent functions.

[WORKFLOW]
1. **Analyze**: Read the source code using the tool.
2. **Draft**: Create `test_{module_name}.py` (Handle edge cases).
3. **Save**: Save the test file.
4. **Verify**: Run pytest and measure coverage.
5. **Refine (Loop)**:
   - If coverage < 100%, analyze "Missing lines" and modify the test.
   - Save and Run again.
   - **LIMIT**: Repeat refinement maximum 3 times.
6. **Finalize**: 
   - Call `mark_as_best_submission` with the current result.

[MANDATORY FINAL STEP]
**EVEN IF COVERAGE IS NOT 100%, YOU MUST CALL `mark_as_best_submission` BEFORE EXITING.**
Do not end the conversation without saving your best attempt.
"""
            self.messages.append({"role": "user", "content": system_instruction})

            try:
                # 파일 하나당 타임아웃 3분 (충분함)
                await asyncio.wait_for(self.process_messages(self.messages), timeout=180)
            except asyncio.TimeoutError:
                print(f"[시스템] {module_name} 처리 시간 초과! 다음 파일로 넘어갑니다.")
            except Exception as e:
                print(f"[시스템] {module_name} 처리 중 에러: {e}")
                traceback.print_exc()
            
            # API Rate Limit 회복을 위해 파일 간 2초 휴식
            time.sleep(2)

        print("\n[시스템] 모든 모듈 처리가 완료되었습니다.")

async def main(server_script_path: str, prompt: str):
    client = MCPClient()
    try:
        await client.connect_to_server(server_script_path)
        await client.workflow_loop(prompt)
    finally:
        await client.cleanup()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('server_script_path', help="Path to server script")
    parser.add_argument('prompt', nargs='?', help="Prompt", default="")
    args = parser.parse_args()

    asyncio.run(main(args.server_script_path, args.prompt))