import logging
import os
import sys
import subprocess
from datetime import datetime
from mcp.server.fastmcp import FastMCP


root_logger = logging.getLogger()
if root_logger.handlers:
    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)

# 모든 로그를 'server_debug.log' 파일로만 출력
logging.basicConfig(
    filename='server_debug.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True,
    encoding='utf-8'
)
logger = logging.getLogger(__name__)

mcp = FastMCP("tools-task-3")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TARGET_DIR = os.path.join(BASE_DIR, "targets")
SBST_SCRIPT_PATH = os.path.join(BASE_DIR, "sbst.py")

def _get_secure_path(root_dir: str, file_path: str) -> str:
    full_path = os.path.abspath(os.path.join(root_dir, file_path))
    if not full_path.startswith(root_dir):
        raise ValueError(f"Access denied: {file_path}")
    return full_path

def find_target_file(filename: str) -> str:
    """파일명으로 실제 경로를 찾는 함수."""
    # 1. targets/example1.py
    direct_path = os.path.join(TARGET_DIR, filename)
    if os.path.exists(direct_path):
        return direct_path
    
    # 2. targets/example1/example1.py
    base_name = os.path.splitext(filename)[0]
    nested_path = os.path.join(TARGET_DIR, base_name, filename)
    if os.path.exists(nested_path):
        return nested_path
    
    return None

@mcp.tool()
def list_files() -> str:
    """List all Python files in the target directory to generate tests for."""
    logger.info("Tool called: list_files")
    try:
        files = []
        if os.path.exists(TARGET_DIR):
            for root, _, filenames in os.walk(TARGET_DIR):
                for f in filenames:
                    if f.endswith(".py") and not f.startswith("test_"):
                        rel_path = os.path.relpath(os.path.join(root, f), TARGET_DIR)
                        files.append(rel_path)
        return str(files)
    except Exception as e:
        logger.error(f"Error in list_files: {e}")
        return str(e)

@mcp.tool()
def read_file(file_path: str) -> str:
    """Read contents of a Python file."""
    logger.info(f"Tool called: read_file ({file_path})")
    try:
        full_path = _get_secure_path(TARGET_DIR, file_path)
        if not os.path.exists(full_path):
            return f"Error: File '{file_path}' not found."
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error in read_file: {e}")
        return str(e)

@mcp.tool()
def write_file(file_path: str, content: str) -> str:
    """Write content to a file. Use this to save the generated test code."""
    logger.info(f"Tool called: write_file ({file_path})")
    try:
        full_path = os.path.abspath(os.path.join(BASE_DIR, file_path))
        target_abs_path = os.path.abspath(TARGET_DIR)

        # Guardrail 1: 프로젝트 외부 쓰기 금지
        if not full_path.startswith(BASE_DIR):
             return "Error: Cannot write outside project root."

        # Guardrail 2: Targets 폴더 보호
        if full_path.startswith(target_abs_path):
            logger.warning(f"Blocked write attempt to targets: {file_path}")
            return f"SECURITY ALERT: Writing to '{file_path}' inside 'targets' is FORBIDDEN. Please save to the results directory."

        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        logger.info(f"Successfully wrote to: {file_path}")
        return f"Successfully wrote to '{file_path}'."
    except Exception as e:
        logger.error(f"Error in write_file: {e}")
        return str(e)

@mcp.tool()
def run_sbst(target_filename: str) -> str:
    """
    Run Search-Based Software Testing (SBST) on a target file to generate unit test cases.
    Args:
        target_filename (str): The name of the target Python file (e.g., 'example1.py').
    """
    logger.info(f"Tool called: run_sbst ({target_filename})")
    
    try:
        # 1. 실제 파일 위치 찾기
        real_target_path = find_target_file(target_filename)
        if not real_target_path:
            logger.error(f"File not found: {target_filename}")
            return f"Error: Could not find '{target_filename}'."

        logger.info(f"Running SBST on: {real_target_path}")

        # 2. SBST 실행 (Deadlock 방지,  Log 파일 기록)
        with open("sbst_output.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"\n[{datetime.now()}] START SBST for {target_filename}\n")
            log_file.flush()
            
            # stdin=subprocess.DEVNULL : Deadlock 방지
            process = subprocess.run(
                [sys.executable, SBST_SCRIPT_PATH, real_target_path],
                stdout=log_file,
                stderr=log_file,
                text=True,
                encoding='utf-8',
                timeout=180,              # 타임아웃 3분
                stdin=subprocess.DEVNULL  # 입력 차단
            )

        # 3. 실행 결과 확인
        if process.returncode != 0:
            logger.error(f"SBST Failed with return code {process.returncode}")
            return "SBST Execution Failed. Check sbst_output.log for details."

        # 4. 생성된 임시 파일 찾기
        target_dir = os.path.dirname(real_target_path)
        generated_filename = f"test_{target_filename}"
        generated_file_path = os.path.join(target_dir, generated_filename)

        if not os.path.exists(generated_file_path):
            logger.error("Generated test file not found.")
            return "Error: Output file not found. SBST may have failed to generate tests."

        # 5. 내용 읽기
        with open(generated_file_path, "r", encoding="utf-8") as f:
            generated_code = f.read()

        # 6. 임시 파일 삭제
        try:
            os.remove(generated_file_path)
            logger.info(f"Cleaned up: {generated_file_path}")
        except Exception as e:
            logger.warning(f"Cleanup failed: {e}")

        # 7. LLM을 위한 경로 힌트 추가
        hint = f"# [MCP Info] Original file location: {os.path.relpath(real_target_path, BASE_DIR)}\n"
        
        return f"SBST Result:\n{hint}{generated_code}"

    except subprocess.TimeoutExpired:
        logger.error("SBST Timeout Expired")
        return "Error: Timeout - SBST execution took too long."
    except Exception as e:
        logger.error(f"Critical error in run_sbst: {e}")
        return f"Error running SBST: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport='stdio')