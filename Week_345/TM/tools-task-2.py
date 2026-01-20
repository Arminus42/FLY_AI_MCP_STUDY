import logging
import os
import subprocess
import sys
import glob
from datetime import datetime
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

mcp = FastMCP("tools-task-2")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TARGET_DIR = os.path.join(BASE_DIR, "targets")
TIMESTAMP = datetime.now().strftime("%Y%m%d%H%M%S")
RESULTS_DIR = os.path.join(BASE_DIR, f"task2_results_{TIMESTAMP}")
BEST_COVERAGE_DIR = os.path.join(BASE_DIR, "best_coverages")
COVERAGE_FILE = os.path.join(BASE_DIR, ".coverage")

for directory in [TARGET_DIR, RESULTS_DIR, BEST_COVERAGE_DIR]:
    os.makedirs(directory, exist_ok=True)

def _get_secure_path(file_path: str) -> str:
    full_path = os.path.abspath(os.path.join(BASE_DIR, file_path))
    if not full_path.startswith(BASE_DIR):
        raise ValueError(f"Access denied: {file_path}")
    return full_path

def _run_subprocess_with_env(cmd, target_file_path=None):
    """환경변수 설정 헬퍼"""
    env = os.environ.copy()
    
    if target_file_path:
        full_target_path = _get_secure_path(target_file_path)
        target_dir_path = os.path.dirname(full_target_path)
        env["PYTHONPATH"] = target_dir_path + os.pathsep + env.get("PYTHONPATH", "")
    
    env["COVERAGE_FILE"] = COVERAGE_FILE
    
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env,
        timeout=15,
        stdin=subprocess.DEVNULL,
        cwd=BASE_DIR
    )

@mcp.tool()
def list_files() -> str:
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
    try:
        full_path = _get_secure_path(file_path)
        if not os.path.exists(full_path): return "Error: File not found."
        with open(full_path, "r", encoding="utf-8") as f: return f.read()
    except Exception as e: return f"Error: {e}"

@mcp.tool()
def write_file(file_path: str, content: str) -> str:
    try:
        full_path = _get_secure_path(file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f: f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e: return f"Error: {e}"

@mcp.tool()
def run_pytest(test_file_path: str, target_file_path: str) -> str:
    """
    Run pytest via `coverage run` to collect data into .coverage file.
    """
    try:
        full_test_path = _get_secure_path(test_file_path)
        full_target_path = _get_secure_path(target_file_path)
        target_dir = os.path.dirname(full_target_path)

        if os.path.exists(COVERAGE_FILE):
            try: os.remove(COVERAGE_FILE)
            except: pass

        cmd = [
            sys.executable, "-m", "coverage", "run",
            "--source", target_dir,
            "-m", "pytest", full_test_path
        ]
        
        result = _run_subprocess_with_env(cmd, target_file_path)
        output = result.stdout + "\n" + result.stderr
        
        if result.returncode == 0:
            return f"PASS\n{output}"
        else:
            return f"FAIL\n{output}"

    except subprocess.TimeoutExpired:
        return "TIMEOUT ERROR: Check for infinite loops."
    except Exception as e:
        return f"Error running pytest: {str(e)}"

@mcp.tool()
def measure_coverage(test_file_path: str, target_file_path: str) -> str:
    """
    Read the .coverage file and return a simple TEXT report.
    """
    try:
        if not os.path.exists(COVERAGE_FILE):
            return "Error: No .coverage file found. Did pytest run successfully?"
        cmd = [sys.executable, "-m", "coverage", "report", "-m"]
        
        result = _run_subprocess_with_env(cmd, target_file_path)
        
        return result.stdout

    except Exception as e:
        return f"Error measuring coverage: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport='stdio')