import logging

import os
import time
import shutil
import glob
import subprocess
import re
import json

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("tools-task-1")

PYTHON_PATH = "/usr/bin/python"
TARGET_DIR = os.path.join(os.path.dirname(__file__), "targets")

def _get_secure_path(OBJECT_DIR: str, file_path: str) -> str:
    full_path = os.path.abspath(os.path.join(OBJECT_DIR, file_path))
    
    if not full_path.startswith(OBJECT_DIR):
        raise ValueError(f"Access denied: {file_path} is outside the target directory.")
    
    return full_path


@mcp.tool()
def list_files() -> str:
    """
    List all Python files in the target directory to generate tests for.
    """
    pass

@mcp.tool()
def read_file(file_path: str) -> str:
    """
    Read the contents of a Python file in the target directory to generate tests for.
    Args:
        file_path (str): The path of the Python file to read.
    """
    pass

@mcp.tool()
def write_file(file_path: str, content: str) -> str:
    """
    Write content to a Python file in the target directory.
    Args:
        file_name (str): The name of the original Python file.
        content (str): The content to write to the file.
    """
    pass

if __name__ == "__main__":
    mcp.run(transport='stdio')
    
