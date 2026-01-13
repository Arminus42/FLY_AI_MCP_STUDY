import logging

import os
from pickletools import pybytes_or_str
import time
import shutil
import glob
import subprocess
import re
import json
from mcp.server.fastmcp import FastMCP
import pytest
mcp = FastMCP("tools-task-1")

PYTHON_PATH = "/usr/bin/python"
TARGET_DIR = os.path.join(os.path.dirname(__file__), "targets")

@mcp.tool()
def run_pytest() -> str:
    """
    Run pytest on the given Python test file in the target directory.
    """
    files = glob.glob(os.path.join(TARGET_DIR, 'example*/test_*.py'))
    for file in files:
        code = pytest.main([file, '-v', '-rP'])
        logging.info(f"file: {file}, pytest exited with code: {code}")
        
    return f"pytest exited with code: {code}"
    # return None

@mcp.tool()
def measure_coverage(file_path: str) -> str:
    """
    Measure code coverage for the generated test files in the target directory.
    Args:
        file_path (str): The path of the Python file to read.
    """
    return "Coverage measurement not implemented"

if __name__ == "__main__":
    mcp.run(transport='stdio')
    
