import logging
import os
import glob
import json
from datetime import datetime

from mcp.server.fastmcp import FastMCP

# 로깅 설정 (디버깅 용이성 확보)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("tools-task-1")

PYTHON_PATH = "/usr/bin/python"

# 메인, TARGET, RESULTS 디렉토리 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TARGET_DIR = os.path.join(BASE_DIR, "targets")
TIMESTAMP = datetime.now().strftime("%Y%m%d%H%M%S") # results 폴더 시간 스탬프
RESULTS_DIR = os.path.join(BASE_DIR, f"results_{TIMESTAMP}")

# 서버 시작 시 targets 디렉토리가 없으면 생성 (Safety Check)
if not os.path.exists(TARGET_DIR):
    os.makedirs(TARGET_DIR)
    logger.info(f"Created target directory: {TARGET_DIR}")

def _get_secure_path(OBJECT_DIR: str, file_path: str) -> str:
    """
    입력된 파일 경로가 OBJECT_DIR 내부인지 검증하고, 절대 경로를 반환합니다.
    (Path Traversal 공격을 방지합니다.)
    """
    # 입력된 경로를 절대 경로로 변환
    full_path = os.path.abspath(os.path.join(OBJECT_DIR, file_path))
    
    # 변환된 경로가 TARGET_DIR로 시작하는지 확인 (Sandboxing)
    if not full_path.startswith(OBJECT_DIR):
        raise ValueError(f"Access denied: {file_path} is outside the target directory.")
    
    return full_path

@mcp.tool()
def list_files() -> str:
    """
    List all Python files in the target directory to generate tests for.
    Returns a JSON string list of filenames.
    """
    try:
        # Target 절대 경로 확인
        abs_target_dir = os.path.abspath(TARGET_DIR)

        # TARGET_DIR 내의 모든 .py 파일 검색
        files = []
        for root, dirs, filenames in os.walk(abs_target_dir):
            for filename in filenames:
                # 발견된 모든 파일을 리스트에 담음
                if filename.endswith(".py"):
                    full_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(full_path, abs_target_dir)
                    rel_path = rel_path.replace("\\", "/")
                    files.append(rel_path)

        debug_msg = (
            f"- Searched in: {abs_target_dir}\n"
            f"- Total files found in dir (any extension): {files}"
        )

        return debug_msg
    
    except Exception as e:
        return f"Error listing files: {str(e)}"

@mcp.tool()
def read_file(file_path: str) -> str:
    """
    Read the contents of a Python file in the target directory to generate tests for.
    Args:
        file_path (str): The name of the Python file to read (e.g., 'calculator.py').
    """
    try:
        full_path = _get_secure_path(TARGET_DIR, file_path)
        
        if not os.path.exists(full_path):
            return f"Error: File '{file_path}' not found."
            
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        logger.info(f"Read file: {file_path}")
        return content
    except ValueError as ve:
        return str(ve)
    except Exception as e:
        return f"Error reading file '{file_path}': {str(e)}"

@mcp.tool()
def write_file(file_path: str, content: str) -> str:
    """
    Write content to a Python file in the target directory.
    Args:
        file_path (str): The name of the file to write (e.g., 'test_calculator.py').
        content (str): The content to write to the file.
    """
    try:
        full_path = _get_secure_path(BASE_DIR, file_path)

        rel_path = os.path.relpath(full_path, BASE_DIR)
        if not os.path.dirname(rel_path):
            error_msg = (
                f"Security Guardrail Triggered: Writing directly to the project root ('{file_path}') is FORBIDDEN.\n"
            )
            logger.warning(error_msg)
            return error_msg
        
        # 파일이 저장될 폴더가 없으면 자동으로 생성함
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # 파일 쓰기 (기존 파일이 있다면 덮어씁니다)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
                   
        logger.info(f"Wrote to file: {file_path}")
        return f"Successfully wrote to '{file_path}'."
    except ValueError as ve:
        return str(ve)
    except Exception as e:
        return f"Error writing file '{file_path}': {str(e)}"

if __name__ == "__main__":
    # stdio 전송 계층을 사용하여 서버 실행
    mcp.run(transport='stdio')
