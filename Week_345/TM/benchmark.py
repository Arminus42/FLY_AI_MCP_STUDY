import subprocess
import time
import sys
import statistics
import re

def run_universal_benchmark(client_script="mcp-client-task-3.py", server_script="tools-task-3.py", iterations=5):
    """
    내부 로그 포맷에 상관없이, 스크립트의 전체 실행 시간을 외부에서 측정합니다.
    """
    
    execution_times = []
    tool_call_counts = []
    
    print(f"🚀 [Universal Benchmark] Running '{client_script}' {iterations} times...")
    print(f"   (Target Server: {server_script})")
    print("=" * 60)

    # 도구 호출을 추정하기 위한 키워드 (MCP 표준 로그나 함수 이름)
    # 다른 사람의 코드라도 'run_sbst'나 'write_file'이라는 단어는 출력될 가능성이 높음
    tool_keywords = re.compile(r"(Tool Call|CallToolRequest|run_sbst|write_file)", re.IGNORECASE)

    for i in range(1, iterations + 1):
        print(f"▶️  Run {i}/{iterations} ...", end=" ", flush=True)
        
        # 1. 시간 측정 시작 (스톱워치)
        start_time = time.time()
        
        try:
            # 스크립트 실행
            result = subprocess.run(
                [sys.executable, client_script, server_script],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            # 2. 시간 측정 종료
            end_time = time.time()
            duration = end_time - start_time
            
            if result.returncode != 0:
                print("FAILED ❌")
                print(f"   [Error Output]: {result.stderr[:200]}...") # 에러 일부 출력
                continue

            # 3. 데이터 기록
            execution_times.append(duration)
            
            # 4. 도구 호출 횟수 추정 (출력 텍스트에서 키워드 카운팅)
            # 정확하지 않을 수 있지만, 대략적인 복잡도를 파악하는 데 도움됨
            tool_count = len(tool_keywords.findall(result.stdout))
            tool_call_counts.append(tool_count)
            
            print(f"DONE ✅ ({duration:.2f}s, approx {tool_count} tool logs)")

        except Exception as e:
            print(f"ERROR ❌ ({e})")

    print("=" * 60)
    
    if not execution_times:
        print("No successful runs.")
        return

    # 통계 계산
    avg_time = statistics.mean(execution_times)
    stdev_time = statistics.stdev(execution_times) if len(execution_times) > 1 else 0.0
    
    avg_tools = statistics.mean(tool_call_counts)

    print("\n📊 Benchmark Results (Total Script Execution)")
    print("=" * 60)
    print(f"Target Script : {client_script}")
    print(f"Iterations    : {iterations}")
    print("-" * 60)
    print(f"⏱️  Avg Total Time : {avg_time:.2f} sec (±{stdev_time:.2f})")
    print(f"🛠️  Avg Tool Logs  : {avg_tools:.1f} (Estimated from stdout)")
    print("=" * 60)
    print("* Note: 'Avg Tool Logs' counts keywords like 'run_sbst' in output.")
    print("* Note: LLM Request count cannot be measured externally.")

if __name__ == "__main__":
    # 실행하고 싶은 파일명이 다르면 여기서 수정하거나 인자로 받음
    target_client = "mcp-client-task-3.py"
    target_server = "tools-task-3.py"
    
    # 커맨드라인 인자 지원 (예: python benchmark.py my_client.py my_tools.py)
    if len(sys.argv) >= 2:
        target_client = sys.argv[1]
    if len(sys.argv) >= 3:
        target_server = sys.argv[2]
        
    run_universal_benchmark(target_client, target_server)