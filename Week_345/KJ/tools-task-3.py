import logging

import os
import time
import shutil
import glob
import subprocess
import re
import json
import sys
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("tools-task-3")

PYTHON_PATH = "/usr/bin/python"
TARGET_DIR = os.path.join(os.path.dirname(__file__), "targets")

@mcp.tool()
def list_files() -> str:
    """
    List all Python files in the target directory to generate tests for.
    """
    files = list(glob.glob(os.path.join(TARGET_DIR, 'example*/example*.py')))

    if not files:
        return "No Python files found in the target directory."

    return str(files)

@mcp.tool()
def run_sbst(file_path: str, save_path: str) -> str:
    """
    Run SBST.py for python file in the target directory to generate test.
    args:
        file_path (str): The path of the python file in the target dir.
        save_path (str): The path to save the generated test file.
    """
    abs_file_path = os.path.abspath(file_path)
    if not os.path.exists(abs_file_path):
        return f"Error: File not found at {abs_file_path}"

    cmd = [sys.executable, "sbst2.py", file_path, save_path]

    try:
        result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
            )
        
        output = []
        output.append(f"Pytest exited with code: {result.returncode}")
        if result.returncode != 0:
            output.append("WARNING: Pytest failed. Coverage file might not be generated or updated.")

        if result.stdout:
            output.append(f"--- Standard Output ---\n{result.stdout}")
        
        if result.stderr:
            # 특히 returncode 2나 4일 때 이 부분이 중요합니다.
            output.append(f"--- Standard Error (Issues found) ---\n{result.stderr}")
        output_string = "\n".join(output)
        logging.info(f"pytest result: {result.returncode}, {output_string}")
        return output_string


    except Exception as e:
        logging.info(f"Exception: {str(e)}")
        return f"An error occurred while running pytest: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport='stdio')
    
