import logging

import os
import time
import shutil
import glob
import subprocess
import re
import json

from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("tools-task-2")

PYTHON_PATH = "/usr/bin/python"
TARGET_DIR = os.path.join(os.path.dirname(__file__), "targets")

test_state = {
    "queue": [],
    "current_test": None,
    "status": False,
    "coverage": 0,
}

@mcp.read_resource("mcp://env/globals")
def read_global_state() -> str:
    # 1. Gather your live variables
    state = {
        "cwd": os.getcwd(),
        "memory_usage": get_ram_usage(),
        "active_flags": global_flags_dict
    }
    
    # 2. Return them as a formatted string (JSON is usually best for LLMs)
    return json.dumps(state, indent=2)


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
    """
    logger.info(f"Starting list_files()")
    if not os.path.exists(TARGET_DIR):
        logger.error(f"Target directory {TARGET_DIR} does not exist")
        return "Error: Target directory does not exist."
    
    files = glob.glob(os.path.join(TARGET_DIR, "results_*/", "test_example*.py"))
    
    relpaths = [os.path.relpath(f, TARGET_DIR) for f in files]

    if relpaths == None:
        logger.warning(f"Target directory is empty.")
    else:
        logger.info(f"Listing files in : {TARGET_DIR}")    
    # 4. Return as a string
    return "\n".join(relpaths)


@mcp.tool()
def read_file(file_path: str) -> str:
    """
    Read the contents of a Python file in the target directory to generate tests for.
    Args:
        file_path (str): The path of the Python file to read.
    """
    logger.info(f"Starting read_file()")
    secure_path = _get_secure_path(TARGET_DIR, file_path)

    if not os.path.exists(secure_path):
        logger.error(f"Given file {secure_path} does not exist.")
        return f"Error: Given file does not exist on {secure_path}."

    with open(secure_path, 'r') as file:
        content = file.read()
        logger.info("Returning file content")
        return content
    

@mcp.tool()
def write_file(file_path: str, content: str, overwrite: bool = False) -> str:
    """
    Write content to a Python file in the target directory.
    Args:
        file_name (str): The name of the original Python file.
        content (str): The content to write to the file.
    """
    logger.info("Starting Write_file().")
    secure_path = _get_secure_path(TARGET_DIR, file_path)

    if os.path.exists(secure_path) and not overwrite:
        logger.error(f"Filepath {secure_path} already exists, and no clearance to overwrite.")
        return (f"Error: File '{secure_path}' already exists. "
                "If you really want to overwrite it, call this tool again with overwrite=True.")
                
    try:
        os.makedirs(os.path.dirname(secure_path), exist_ok=True)
        
        with open(secure_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"Successfully wrote to {secure_path}")
        return f"Success: File written to {secure_path}"
        
    except Exception as e:
        logger.error("Exception occurred while writing to file")
        return f"Error writing file: {str(e)}"

def run_pytest(test_file_path: str) -> str:
    """
    Run pytest on the given test file and return stdout/stderr.
    Useful for checking syntax errors or assertion failures.
    Args: 
        test_file_path: relpath of the test file. Should be an element of list_files()

    Returns:
        result of the pytest, capturing stdout and stderr

    Raises:
        Error: If {test_file_path} does not exist

    """
    if not os.path.exists(test_file_path):
        return f"Error: File {test_file_path} does not exist."

    env = os.environ.copy()
    env["PYTHONPATH"] = TARGET_DIR + os.pathsep + env.get("PYTHONPATH", "")

    try:
        # Run pytest normally
        result = subprocess.run(
            ["pytest", test_file_path],
            env=env,
            capture_output=True,
            text=True,
            timeout=10 # Safety timeout
        )
        return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    except subprocess.TimeoutExpired:
        return "Error: Pytest timed out."
    except Exception as e:
        return f"Error running pytest: {str(e)}"
    
@mcp.tool()
def measure_coverage(test_file_path: str) -> str:
    """
    Run pytest coverage and return the percentage AND missing lines.
    Args:
        test_file_path: Path to the test file (e.g. task2_results.../test_example1.py)
    """
    if not os.path.exists(test_file_path):
        return f"Error: File {test_file_path} does not exist."

    # 1. Infer the target module name from the test file name
    # e.g., "test_example1.py" -> "example1"
    filename = os.path.basename(test_file_path)
    if not filename.startswith("test_") or not filename.endswith(".py"):
        return "Error: Test file must follow pattern 'test_example#.py'"
    
    target_module = filename.replace("test_", "").replace(".py", "")
    
    # 2. Setup JSON report path
    json_report_path = f"coverage_{target_module}.json"

    # 3. Prepare Environment (PYTHONPATH must include targets/)
    env = os.environ.copy()
    env["PYTHONPATH"] = TARGET_DIR + os.pathsep + env.get("PYTHONPATH", "")

    # 4. Run Pytest with Coverage
    # --cov=targets.example1 tells coverage to only look at that specific file
    cmd = [
        "pytest", 
        test_file_path, 
        f"--cov={target_module}", 
        f"--cov-report=json:{json_report_path}"
    ]

    try:
        subprocess.run(cmd, env=env, capture_output=True, text=True, check=False)

        # 5. Parse the JSON report
        if not os.path.exists(json_report_path):
            return "Error: Coverage report was not generated. The test might have failed silently."

        with open(json_report_path, 'r') as f:
            cov_data = json.load(f)

        # Clean up report file
        os.remove(json_report_path)

        # 6. Extract the specific file data
        # Coverage JSON keys usually look like "targets/example1.py" or absolute paths
        target_key = None
        for key in cov_data["files"].keys():
            if f"{target_module}.py" in key:
                target_key = key
                break
        
        if not target_key:
            return f"Error: Could not find coverage data for {target_module}.py in report."

        file_data = cov_data["files"][target_key]
        percent = int(file_data["summary"]["percent_covered"])
        missing_lines = file_data["missing_lines"]

        return json.dumps({
            "target": target_module,
            "coverage_percent": percent,
            "missing_lines": missing_lines
        })

    except Exception as e:
        return f"Error measuring coverage: {str(e)}"

# if __name__ == "__main__":
#     mcp.run(transport='stdio')
    
