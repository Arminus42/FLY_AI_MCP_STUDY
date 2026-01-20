import logging
import os
import sys
import glob
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# 외부 프로세스 실행을 위해 subprocess 모듈 추가
import subprocess

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

mcp = FastMCP("tools-task-2")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TARGET_DIR = os.path.join(BASE_DIR, "targets")

# results, coverages 폴더 설정
##########################################################################################
TIMESTAMP = datetime.now().strftime("%Y%m%d%H%M%S")
RESULTS_DIR = os.path.join(BASE_DIR, f"task2_results_{TIMESTAMP}")
BEST_COVERAGE_DIR = os.path.join(BASE_DIR, "best_coverages")
COVERAGE_FILE = os.path.join(BASE_DIR, ".coverage")

# 필요 directory 생성
for directory in [TARGET_DIR, RESULTS_DIR, BEST_COVERAGE_DIR]:
    os.makedirs(directory, exist_ok=True)
##########################################################################################

def _get_secure_path(file_path: str) -> str:
    full_path = os.path.abspath(os.path.join(BASE_DIR, file_path))
    if not full_path.startswith(BASE_DIR):
        raise ValueError(f"Access denied: {file_path}")
    return full_path

# 서브프로세스 실행 보조 함수
##########################################################################################
def _run_subprocess_with_env(cmd, target_file_path=None):
    """환경변수 설정 헬퍼"""
    env = os.environ.copy()
    
    if target_file_path:
        full_target_path = _get_secure_path(target_file_path)
        target_dir_path = os.path.dirname(full_target_path)

        # Import 에러 방지 (target directory를 PYTHONPATH에 추가)
        env["PYTHONPATH"] = target_dir_path + os.pathsep + env.get("PYTHONPATH", "")
    
    # coverage data 파일 위치 고정
    env["COVERAGE_FILE"] = COVERAGE_FILE
    
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env,
        timeout=15, # 무한 루프 방지 (15초 설정)
        stdin=subprocess.DEVNULL,# Blocking 방지
        cwd=BASE_DIR
    )
##########################################################################################


@mcp.tool()
def list_files() -> str:
    """
    List all Python files in the target directory to generate tests for.
    Returns a JSON string list of filenames.
    """
    files = []
    for root, _, filenames in os.walk(TARGET_DIR):
        for filename in filenames:
            if filename.endswith(".py"):
                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, BASE_DIR).replace("\\", "/")
                files.append(rel_path)
    return str(files)

@mcp.tool()
def read_file(file_path: str) -> str:
    """
    Read the contents of a Python file in the target directory to generate tests for.
    Args:
        file_path (str): The name of the Python file to read (e.g., 'calculator.py').
    """
    try:
        full_path = _get_secure_path(file_path)
        if not os.path.exists(full_path): return "Error: File not found."
        with open(full_path, "r", encoding="utf-8") as f: return f.read()
    except Exception as e: return f"Error: {e}"

@mcp.tool()
def write_file(file_path: str, content: str) -> str:
    """
    Write content to a Python file in the target directory.
    Args:
        file_path (str): The name of the file to write (e.g., 'test_calculator.py').
        content (str): The content to write to the file.
    """
    try:
        full_path = _get_secure_path(file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f: f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e: return f"Error: {e}"

# Pytest 실행 + coverage 수집 tool
##########################################################################################
@mcp.tool()
def run_pytest(test_file_path: str, target_file_path: str) -> str:
    """
    Run pytest via `coverage run` to collect data into .coverage file.
    """
    try:
        full_test_path = _get_secure_path(test_file_path)
        full_target_path = _get_secure_path(target_file_path)
        target_dir = os.path.dirname(full_target_path)

        # 저장된 coverage data 삭제
        if os.path.exists(COVERAGE_FILE):
            try: os.remove(COVERAGE_FILE)
            except: pass

        # 명령어 (pytest 실행, code coverage data 수집)
        cmd = [
            sys.executable, "-m", "coverage", "run",
            "--source", target_dir,
            "-m", "pytest", full_test_path
        ]
        
        # 환경에 맞춰 명령 실행
        result = _run_subprocess_with_env(cmd, target_file_path)

        # 출력 메시지와 오류 메시지 모두 전달
        output = result.stdout + "\n" + result.stderr
        
        if result.returncode == 0:
            return f"PASS\n{output}"
        else:
            return f"FAIL\n{output}"

    except subprocess.TimeoutExpired:
        return "TIMEOUT ERROR: Check for infinite loops."
    except Exception as e:
        return f"Error running pytest: {str(e)}"
##########################################################################################

# Coverage를 불러와 고쳐야 하는 명령어를 확인하는 tool
##########################################################################################
@mcp.tool()
def measure_coverage(test_file_path: str, target_file_path: str) -> str:
    """
    Read the .coverage file and return a simple TEXT report.
    """
    try:
        if not os.path.exists(COVERAGE_FILE):
            return "Error: No .coverage file found. Did pytest run successfully?"
        
        # coverage report 생성 - 실행되지 않은 줄 번호 체크
        cmd = [sys.executable, "-m", "coverage", "report", "-m"]
        
        # 환경에 맞춰 명령 실행
        result = _run_subprocess_with_env(cmd, target_file_path)
        
        return result.stdout

    except Exception as e:
        return f"Error measuring coverage: {str(e)}"
##########################################################################################

if __name__ == "__main__":
    mcp.run(transport='stdio')
