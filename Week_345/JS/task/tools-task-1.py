import logging

import os
import time
import shutil
import glob
import subprocess
import re
import json

from utils import *

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("tools-task-1")

PYTHON_PATH = "/usr/bin/python"
TARGET_DIR = os.path.join(os.path.dirname(__file__), "targets")

@mcp.tool()
def list_files() -> str:
    """
    List all Python files in the target directory to generate tests for.
    """
    if not os.path.exists(TARGET_DIR):
        return "Error: Target directory does not exist."
    
    # 2. Get all .py files in that directory
    # Using glob to find patterns like *.py
    files = glob.glob(os.path.join(TARGET_DIR, "**", "*.py"), recursive=True)
    
    # 3. Clean up the list (usually just sending filenames is cleaner for the LLM)
    relpaths = [os.path.relpath(f, TARGET_DIR) for f in files]
    
    # 4. Return as a string
    return "\n".join(relpaths)

@mcp.tool()
def read_file(file_path: str) -> str:
    """
    Read the contents of a Python file in the target directory to generate tests for.
    Args:
        file_path (str): The path of the Python file to read.
    """
    full_path = os.path.abspath(os.path.join(TARGET_DIR, file_path))
    target_root = os.path.abspath(TARGET_DIR)

    if not in_target(target_root, full_path):
        return f"Error: Security Alert! You cannot read {file_path} because it is outside the target directory."

    if not os.path.exists(full_path):
        return f"Error: Given file does not exist on {file_path}."

    with open(full_path, 'r') as file:
        content = file.read()
        return content

@mcp.tool()
def write_file(file_path: str, content: str, overwrite: bool = False) -> str:
    """
    Write content to a Python file in the target directory.
    Args:
        file_name (str): The name of the original Python file.
        content (str): The content to write to the file.
    """

    full_path = os.path.abspath(os.path.join(TARGET_DIR, file_path))
    target_root = os.path.abspath(TARGET_DIR)

    if not in_target(target_root, full_path):
        return f"Error: Security Alert! You cannot write to {file_path} because it is outside the target directory."

    if os.path.exists(full_path) and not overwrite:
        return (f"Error: File '{file_path}' already exists. "
                "If you really want to overwrite it, call this tool again with overwrite=True.")
                
    try:
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        return f"Success: File written to {file_path}"
        
    except Exception as e:
        return f"Error writing file: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport='stdio')
    
