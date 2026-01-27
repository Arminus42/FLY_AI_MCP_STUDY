"""
[최적화 전략 실험]

1. 전략 1: 비동기 병렬 처리 ✅
   - 구현 방식: Python의 asyncio.gather를 활용하여 3개의 타겟(example1~3)을 동시에 실행.
   - 실험 결과: 순차 실행 대비 실행 시간이 단축됨 (기록은 기억이 안 남..)

2. 전략 2: 도구 병합 ✅
   - 구현 방식: 서버 측에 'run_and_move'라는 Tool을 구현하여 통신 횟수 최소화. (기존에 구현했던 툴 통합)
   - 실험 결과: 전략 1 대비 약 25%의 추가적인 시간 단축 확인 (약 5초대 진입).

3. 전략 3: 프롬프트 튜닝 
   - 구현 방식: 시스템 프롬프트로 "설명 생략, 행동만 수행"을 강제하여 토큰 생성 시간 단축 시도.
   - 실험 결과: 오히려 전체 실행 시간이 증가함 (약 27초)
   - 실패 원인: LLM의 추론(Reasoning) 과정을 과도하게 생략시키자, 어려운 타겟에서 오히려 재시도를 했지 않았을까 생각함.
   system_prompt = (
            "You are a low-latency automation bot. "
            "Your goal is to complete the task using the fewest possible steps. "
            "1. DO NOT explain your plan. "
            "2. DO NOT provide conversational filler. "
            "3. IMMEDIATELY call the necessary tool. "
            "4. When finished, output only 'DONE'."
        )
"""

import asyncio
from typing import Optional
from contextlib import AsyncExitStack
import os
import sys
import datetime
import json
import argparse
import traceback
import time

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

load_dotenv()

TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
RESULT_DIR = f"task3_results_{TIMESTAMP}"
TRAJECTORY_DIR = "trajectory"

os.makedirs(RESULT_DIR, exist_ok=True)
os.makedirs(TRAJECTORY_DIR, exist_ok=True)

class MCPClient:
    """
    단일 타겟 파일(예: example1.py)에 대해 MCP 서버와 대화하며 작업을 수행합니다.
    독립적인 세션을 관리하므로, 병렬 실행 시 데이터가 섞이지 않습니다.
    """
    def __init__(self, target_name):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack() # 비동기 리소스 관리 (자동 close)
        self.llm = OpenAI()                # LLM 클라이언트 (GPT-4o-mini)
        self.messages = []                 # 대화 히스토리 (Context)
        self.trajectory_log = []           # 실행 경로(Trajectory) 기록용 리스트
        
        # [지표 측정] 성능 분석을 위한 카운터 초기화
        self.request_count = 0             # LLM에게 요청한 횟수 (비용과 직결)
        self.tool_call_count = 0           # 도구를 실제로 호출한 횟수 (효율성 지표)
        self.target_name = target_name     # 로그 식별자 (예: example1)

    async def connect_to_server(self, server_script_path: str):
        """
        [서버 연결] MCP 서버 스크립트를 서브프로세스로 실행하고 연결합니다.
        """
        # 'python' 명령어 대신 sys.executable을 사용합니다.
        # 실행 환경(venv 등)의 파이썬 인터프리터를 그대로 상속받아 의존성 문제를 방지합니다.
        server_params = StdioServerParameters(
            command=sys.executable,
            args=[server_script_path],
            env=None
        )
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await self.session.initialize()
        
    async def cleanup(self):
        """리소스 정리 (서버 프로세스 종료)"""
        await self.exit_stack.aclose()

    def log_trajectory(self, role, content):
        """Trajectory 파일에 저장할 로그를 메모리에 기록합니다."""
        entry = f"[{role.upper()}]\n{content}\n"
        self.trajectory_log.append(entry)

    def print_log(self, message):
        """
        [병렬 처리 로그 관리]
        여러 작업이 동시에 돌 때 로그가 섞이므로, [example1] 처럼 태그를 붙여 출력합니다.
        """
        print(f"[{self.target_name}] {message}")

    async def process_messages(self, messages: list[ChatCompletionMessageParam]):
        """
        ReAct 패턴 구현부 (Think -> Act -> Observe Loop)
        LLM과 대화를 주고받으며 도구 호출이 끝날 때까지 재귀적으로 수행됩니다.
        """
        
        # 1. 현재 사용 가능한 도구 목록 조회 (동적으로 서버에서 가져옴)
        response = await self.session.list_tools()
        available_tools = [ChatCompletionToolParam(
            type="function",
            function=FunctionDefinition(
                name=tool.name,
                description=tool.description if tool.description else "",
                parameters=tool.inputSchema
            )
        ) for tool in response.tools]

        # [지표] LLM 요청 횟수 카운트 (성능 측정용)
        self.request_count += 1
        
        # 2. LLM 호출 (Tools 정의 포함)
        response = self.llm.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=available_tools,
            tool_choice="auto"
        )

        finish_reason = response.choices[0].finish_reason
        message_content = response.choices[0].message.content or ""

        # AI의 응답(Thought)이 있으면 기록
        if message_content:
            self.log_trajectory("assistant", message_content)

        # 3-A. 종료 조건: AI가 더 이상 도구를 호출하지 않을 때 (작업 완료)
        if finish_reason == "stop": 
            messages.append(ChatCompletionAssistantMessageParam(role="assistant", content=message_content))

        # 3-B. 도구 호출 요청 발생 (Tool Call)
        elif finish_reason == "tool_calls":
            tool_calls = response.choices[0].message.tool_calls
            assert tool_calls is not None
            
            for tool_call in tool_calls:
                self.tool_call_count += 1  # [지표] 도구 호출 횟수 증가
                self.log_trajectory("tool_call", f"Function: {tool_call.function.name}\nArgs: {tool_call.function.arguments}")
                self.print_log(f"Tool called: {tool_call.function.name}")

            # 대화 내역에 AI의 요청 추가
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
                        ) for tool_call in tool_calls
                    ]
                )
            )
            
            # [비동기 처리] 만약 AI가 여러 도구를 동시에 호출했다면, 병렬로 실행하여 속도 최적화
            tasks = [asyncio.create_task(self.process_tool_call(tool_call)) for tool_call in tool_calls]
            tool_results = await asyncio.gather(*tasks)
            messages.extend(tool_results)
            
            # 도구 실행 결과를 포함하여 다시 LLM 호출 (재귀 Loop)
            return await self.process_messages(messages)
            
        return messages

    async def process_tool_call(self, tool_call) -> ChatCompletionToolMessageParam:
        """단일 도구 실행 및 결과 반환"""
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)
        
        # MCP 세션을 통해 서버에 도구 실행 요청
        call_tool_result = await self.session.call_tool(tool_name, tool_args)
        
        result_text = call_tool_result.content[0].text
        self.log_trajectory("tool_result", f"Result from {tool_name}: {result_text[:200]}...") 

        return ChatCompletionToolMessageParam(
            role="tool",
            content=json.dumps({
                **tool_args,
                tool_name: [c.text for c in call_tool_result.content]
            }),
            tool_call_id=tool_call.id
        )

    async def run_task(self, target_file: str):
        """단일 타겟에 대한 전체 워크플로우 실행"""
        self.messages = []
        self.trajectory_log = []
        self.request_count = 0
        self.tool_call_count = 0
        
        self.print_log("Processing started (Optimized Strategy)")
        start_time = time.time()
        
        # [최적화 전략 2: 도구 병합 프롬프트]
        # AI에게 개별 단계(run -> move) 대신 '복합 도구(run_sbst_and_move)'를 사용하도록 강제합니다.
        # 이를 통해 LLM과의 통신 횟수(Turn)를 줄여 실행 속도를 높입니다.
        prompt = (
            f"Use the composite tool 'run_sbst_and_move' to run the SBST tool for '{target_file}' "
            f"and immediately move the result to '{RESULT_DIR}'. "
            f"Do NOT run the steps separately. Confirm when done."
        )
        
        self.messages.append({"role": "user", "content": prompt})
        self.log_trajectory("user", prompt)

        try:
            await self.process_messages(self.messages)
        except Exception as e:
            self.print_log(f"Error: {e}")
            traceback.print_exc()

        # [성능 지표 계산]
        end_time = time.time()
        duration = end_time - start_time
        avg_time = duration / self.request_count if self.request_count > 0 else 0

        # Trajectory 파일 마지막에 통계 요약 추가
        stats_log = (
            f"\n--- Performance Metrics ({self.target_name}) ---\n"
            f"Execution Time: {duration:.4f} sec\n"
            f"LLM Request Count: {self.request_count}\n"
            f"Tool Call Count: {self.tool_call_count}\n"
            f"Time per Request: {avg_time:.4f} sec\n"
        )
        self.trajectory_log.append(stats_log)
        self.print_log(f"Completed in {duration:.2f}s")

        # 실행 경로(Trajectory) 파일 저장
        example_id = target_file.split("/")[0] 
        traj_filename = f"trajectory_{example_id}.txt"
        
        with open(os.path.join(TRAJECTORY_DIR, traj_filename), "w", encoding="utf-8") as f:
            f.write("\n".join(self.trajectory_log))
            
        # 메인 함수로 통계 데이터 반환
        return {
            "target": self.target_name,
            "duration": duration,
            "requests": self.request_count,
            "tool_calls": self.tool_call_count,
            "avg_time": avg_time
        }

async def worker(server_script_path, target_file):
    """
    [세션 격리 작업자]
    각 타겟 파일마다 '새로운 클라이언트 인스턴스'를 생성합니다.
    이는 병렬 실행 시 대화 내역(Context)이 섞이는 것을 완벽하게 방지합니다.
    """
    client = MCPClient(target_name=target_file.split("/")[0])
    try:
        await client.connect_to_server(server_script_path)
        return await client.run_task(target_file)
    finally:
        await client.cleanup()

async def main(server_script_path: str):
    targets = ["example1/example1.py", "example2/example2.py", "example3/example3.py"]
    
    print(f"[Main] Starting parallel processing for {len(targets)} targets (Strategy 2: Tool Merging)...\n")
    start_total = time.time()

    # [최적화 전략 1: 비동기 병렬 처리]
    # asyncio.gather를 사용하여 3개의 작업을 '동시에' 시작합니다.
    # 전체 소요 시간은 (Task 1 + 2 + 3)이 아니라 max(Task 1, 2, 3)에 수렴
    results = await asyncio.gather(*(worker(server_script_path, target) for target in targets))
    
    total_duration = time.time() - start_total
    
    # [결과 요약 리포트 출력]
    print("\n" + "="*80)
    print(f"{'Target':<15} | {'Duration (s)':<15} | {'Requests':<10} | {'Tool Calls':<12} | {'Time/Req (s)':<15}")
    print("-" * 80)
    for res in results:
        print(f"{res['target']:<15} | {res['duration']:<15.4f} | {res['requests']:<10} | {res['tool_calls']:<12} | {res['avg_time']:<15.4f}")
    print("-" * 80)
    print(f"Total Wall Time: {total_duration:.4f} sec")
    print("="*80 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('server_script_path', help="Path to the server script")
    args = parser.parse_args()

    asyncio.run(main(args.server_script_path))