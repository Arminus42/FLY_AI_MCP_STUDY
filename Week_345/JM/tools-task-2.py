import os
import shutil
import subprocess
import re
import json
import sys
from datetime import datetime
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("tools-task-2")

# 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TARGETS_DIR = os.path.join(BASE_DIR, "targets")

# 결과 디렉토리 생성 (실행 시점 기준 타임스탬프)
TIMESTAMP = datetime.now().strftime("%Y%m%d%H%M%S")
RESULTS_DIR = os.path.join(BASE_DIR, f"task2_results_{TIMESTAMP}")
BEST_COVERAGES_DIR = os.path.join(BASE_DIR, "best_coverages")

os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(BEST_COVERAGES_DIR, exist_ok=True)

@mcp.tool()
def list_target_modules() -> str:
    """
    targets 디렉토리에 있는 모든 파이썬 모듈 이름(예: 'example1')을 리스트로 반환합니다.
    """
    modules = []
    if os.path.exists(TARGETS_DIR):
        for name in os.listdir(TARGETS_DIR):
            if name.startswith("example") and os.path.isdir(os.path.join(TARGETS_DIR, name)):
                modules.append(name)
    return str(sorted(modules))

@mcp.tool()
def read_target_code(module_name: str) -> str:
    """
    대상 파이썬 파일의 내용을 읽어옵니다.
    Args:
        module_name (str): 모듈 이름 (예: 'example1')
    """
    file_path = os.path.join(TARGETS_DIR, module_name, f"{module_name}.py")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"파일 읽기 오류: {str(e)}"

@mcp.tool()
def save_test_code(module_name: str, test_content: str) -> str:
    """
    생성된 테스트 코드를 결과 디렉토리에 저장합니다.
    파일명 규칙: test_{module_name}.py
    """
    file_name = f"test_{module_name}.py"
    file_path = os.path.join(RESULTS_DIR, file_name)
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(test_content)
        return f"저장 성공: {file_name} -> {RESULTS_DIR}"
    except Exception as e:
        return f"파일 쓰기 오류: {str(e)}"

@mcp.tool()
def run_pytest_and_measure_coverage(module_name: str) -> str:
    """
    해당 모듈에 대해 pytest를 실행하고 커버리지를 측정합니다.
    커버리지 퍼센트와 누락된 라인(Missing lines) 정보를 반환합니다.
    제약사항: 30초 타임아웃.
    """
    test_file = os.path.join(RESULTS_DIR, f"test_{module_name}.py")
    target_path = os.path.join(TARGETS_DIR, module_name) # PYTHONPATH에 추가할 경로
    
    if not os.path.exists(test_file):
        return "오류: 테스트 파일이 없습니다. 테스트 코드를 먼저 생성하고 저장해주세요."

    # 환경변수 설정: 'import example1'이 작동하도록 타겟 디렉토리를 PYTHONPATH에 추가
    env = os.environ.copy()
    env["PYTHONPATH"] = target_path + os.pathsep + env.get("PYTHONPATH", "")

    # 명령어 실행: python -m pytest test_file --cov=module --cov-report=term-missing
    cmd = [
        sys.executable, "-m", "pytest",
        test_file,
        f"--cov={module_name}",
        "--cov-report=term-missing"
    ]

    try:
        # 30초 타임아웃 설정
        result = subprocess.run(
            cmd, 
            cwd=RESULTS_DIR, # 결과 디렉토리에서 실행
            env=env,
            capture_output=True, 
            text=True, 
            timeout=30 
        )
        
        output = result.stdout + "\n" + result.stderr
        
        # 정규표현식으로 커버리지 파싱
        # 예: example1.py   20      5    75%   10-15
        match = re.search(rf"{module_name}\.py\s+\d+\s+\d+\s+(\d+)%", output)
        coverage = int(match.group(1)) if match else 0
        
        return f"실행 결과:\n{output}\n\n파싱된 커버리지: {coverage}%"

    except subprocess.TimeoutExpired:
        return "오류: Pytest가 30초 동안 응답이 없어 중단되었습니다 (Timeout)."
    except Exception as e:
        return f"Pytest 실행 중 오류 발생: {str(e)}"

@mcp.tool()
def mark_as_best_submission(module_name: str, coverage: int) -> str:
    """
    현재 테스트 파일을 'best_coverages' 폴더로 복사하고 JSON을 업데이트합니다.
    높은 커버리지를 달성했을 때 호출하세요.
    """
    test_file_name = f"test_{module_name}.py"
    src_path = os.path.join(RESULTS_DIR, test_file_name)
    dst_path = os.path.join(BEST_COVERAGES_DIR, test_file_name)
    
    json_path = os.path.join(BEST_COVERAGES_DIR, "coverages.json")
    
    try:
        # 파일 복사
        shutil.copy(src_path, dst_path)
        
        # JSON 업데이트
        data = {}
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                try:
                    data = json.load(f)
                except:
                    data = {}
        
        # 덮어쓰기 (최신 결과가 항상 저장됨)
        data[module_name] = coverage
        
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=4)
            
        return f"최고 기록 저장 완료: {module_name} ({coverage}%) -> best_coverages"
    except Exception as e:
        return f"최고 기록 저장 중 오류: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport='stdio')