import logging
import os
import sys
import shutil
import glob
import subprocess
import json

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("tools-task-3")

PYTHON_PATH = sys.executable

TARGET_DIR = os.path.join(os.path.dirname(__file__), "targets")
SBST_SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "sbst.py")

@mcp.tool()
def list_files() -> str:
    """
    targets 디렉토리 내의 모든 파이썬 파일을 재귀적으로 검색하여 나열합니다.
    AI가 작업 대상을 파악하는 첫 단계에 사용됩니다.
    """
    # 예외 처리: 타겟 디렉토리가 없는 경우 방어
    if not os.path.exists(TARGET_DIR):
        return "Target directory not found."
    
    # recursive=True 옵션을 사용하여 하위 폴더(예: example1/...)까지 모두 검색
    files = glob.glob(os.path.join(TARGET_DIR, "**", "*.py"), recursive=True)
    
    # AI에게 절대 경로 대신 상대 경로만 제공하여 혼란을 방지하고 토큰을 절약
    # 예: "C:/Users/.../targets/example1/example1.py" -> "example1/example1.py"
    relative_files = [os.path.relpath(f, TARGET_DIR) for f in files]
    
    return json.dumps(relative_files)

# [기존 도구 1] 개별 실행용 (유지)
# 전략 2(도구 병합)를 사용하더라도, 디버깅이나 개별 제어를 위해 남겨둠
# @mcp.tool()
def run_sbst(target_relative_path: str) -> str:
    """
    [실행 도구] 지정된 대상 파일에 대해 레거시 도구인 sbst.py를 실행합니다.
    """
    # 입력받은 상대 경로를 내부적으로 절대 경로로 변환
    target_full_path = os.path.join(TARGET_DIR, target_relative_path)
    
    # 파일 존재 여부 검증
    if not os.path.exists(target_full_path):
        return f"Error: File {target_relative_path} does not exist."

    # subprocess를 통해 별도 프로세스로 sbst.py 실행
    # 환경 변수나 의존성 충돌을 방지하기 위해 sys.executable 사용
    cmd = [PYTHON_PATH, SBST_SCRIPT_PATH, target_full_path]
    
    try:
        # timeout=120: sbst.py가 무한 루프에 빠질 경우를 대비해 
        # 2분 후 강제 종료하는 데드라인 설정 (Safety Guard)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        # 실행 결과(stdout) 또는 에러(stderr) 반환
        if result.returncode == 0:
            return f"SBST Execution Success:\n{result.stdout}"
        else:
            return f"SBST Execution Failed:\n{result.stderr}"
            
    except subprocess.TimeoutExpired:
        return "Error: SBST execution timed out."
    except Exception as e:
        return f"Error executing SBST: {str(e)}"

# [기존 도구 2] 개별 이동용 (유지)
# sbst.py가 결과 저장 위치를 변경할 수 없는 제약을 해결하기 위한 도구
# @mcp.tool()
def move_generated_test(target_relative_path: str, destination_dir: str) -> str:
    """
    sbst.py가 생성한 테스트 파일을 찾아 지정된 결과 폴더로 이동시킵니다.
    Legacy Tool(sbst.py)의 하드코딩된 저장 경로 문제를 해결하는 Wrapper 역할을 합니다.
    """
    # 원본 파일 경로를 기반으로 sbst.py가 생성했을 파일명 추론
    target_full_path = os.path.join(TARGET_DIR, target_relative_path)
    target_dir = os.path.dirname(target_full_path)
    target_filename = os.path.basename(target_full_path)
    
    # 규칙: sbst.py는 원본 파일명 앞에 'test_'를 붙여 같은 폴더에 저장함
    generated_test_name = f"test_{target_filename}"
    source_path = os.path.join(target_dir, generated_test_name)
    
    # 목적지 폴더가 없으면 생성 (안전한 파일 이동 보장)
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir, exist_ok=True)
        
    dest_path = os.path.join(destination_dir, generated_test_name)
    
    # 파일 이동 수행 (shutil.move 사용)
    if os.path.exists(source_path):
        shutil.move(source_path, dest_path)
        return f"Moved {generated_test_name} to {destination_dir}"
    else:
        return f"Error: Generated test file {generated_test_name} not found."

# =================================================================
# [최적화 전략 2] 도구 병합 (Tool Merging / Composite Tool)
# 실행(Run)과 이동(Move)을 서버 내부에서 연속으로 처리하는 슈퍼 도구
# 목적: LLM과 서버 간의 통신 횟수(Round Trip)를 2회 -> 1회로 줄여 실행 시간 단축
# =================================================================
@mcp.tool()
def run_sbst_and_move(target_relative_path: str, destination_dir: str) -> str:
    """
    sbst.py를 실행하고, 성공 시 생성된 파일을 즉시 목적지로 이동시킵니다.
    두 가지 작업을 한 번에 수행하여 네트워크 지연과 LLM 추론 시간을 절약합니다.
    """
    # 1. 실행 단계 (Run Step) - 기존 함수 재사용
    run_result = run_sbst(target_relative_path)
    
    # 실행 단계에서 실패하면 이동 단계는 수행하지 않고 즉시 종료
    if "Execution Failed" in run_result or "Error" in run_result:
        return f"Step 1 Failed (Run): {run_result}"
    
    # 2. 이동 단계 (Move Step) - 실행 성공 시에만 수행
    move_result = move_generated_test(target_relative_path, destination_dir)
    
    # 두 단계의 결과를 합쳐서 한 번에 반환
    return f"Composite Operation Complete:\n1. {run_result}\n2. {move_result}"

if __name__ == "__main__":
    # stdio 전송 방식을 사용하여 MCP 서버 구동
    mcp.run(transport='stdio')