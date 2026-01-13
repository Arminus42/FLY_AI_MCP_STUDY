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


mcp = FastMCP("tools-task-1")

PYTHON_PATH = "/usr/bin/python"
TARGET_DIR = os.path.join(os.path.dirname(__file__), "targets")
CONFIG = {'target_file': os.path.join(TARGET_DIR, 'example1/example1.py')}

@mcp.tool()
def list_files() -> str:
    """
    List all Python files in the target directory to generate tests for.
    """
    files = glob.glob(os.path.join(TARGET_DIR, 'example*/*.py'))

    if not files:
        return "No Python files found in the target directory."

    return "\n".join(files)

@mcp.tool()
def set_target_file(file_path: str) -> str:
    """
    Set the target file for subsequent operations.
    Args:
        file_path (str): The path of the Python file to set as target.
    """
    CONFIG["target_file"] = file_path
    return f"Target file set to {file_path}"

@mcp.tool()
def read_file() -> str:
    """
    Read the contents of a Python file in the target directory to generate tests for.
    """
    file_path = CONFIG['target_file']
    with open(file_path, "r") as f:
        return f.read()

@mcp.tool()
def write_file(file_path: str, content: str) -> str:
    """
    Write content to a Python file in the target directory.
    Args:
        file_name (str): The name of the original Python file.
        content (str): The content to write to the file.
    """

    if not file_path.startswith(TARGET_DIR):
        return f"Error: Access denied. You can only write files within {TARGET_DIR}"

    # timestamp = time.strftime("%Y%m%d%H%M%S")
    # base_dir = "/".join(file_path.split('/')[:-2])
    # os.makedirs(os.path.join(base_dir, f"results_{timestamp}"), exist_ok=True)
    # file_path = os.path.join(base_dir, f"results_{timestamp}", os.path.basename(file_path))
    # logging.info(f"Writing to {file_path}")

    try:
        with open(file_path, "w") as f:
            f.write(content)
            return f"Successfully wrote content to {file_path}"

    except Exception as e:
        return f"Error writing file: {e}"
    
    
if __name__ == "__main__":
    mcp.run(transport='stdio')
    
