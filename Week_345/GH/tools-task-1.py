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


# LLM에게 테스트 대상이 되는 python 파일 목록을 알려주는 용도
@mcp.tool()
def list_files() -> str:
    files = [] # .py 파일 이름만 저장할 빈 리스트 생성
    
    for name in os.listdir(TARGET_DIR):

        full_path = os.path.join(TARGET_DIR, name)
        # 검사를 위해 임시로 경로를 생성
        
        if os.path.isfile(full_path) and name.endswith(".py"):
        # full_path가 파일인지, name이 .py로 끝나는지 확인
            files.append(name)
            
    return "\n".join(files)


# LLM이 요청한 파일 이름을 받아서 /targets 안에 있는 그 파일을 연 뒤에 전체 내용을 문자열로 반환
@mcp.tool()
def read_file(file_path: str) -> str:
    full_path = os.path.join(TARGET_DIR, file_path)
    # TARGET_DIR과 file_path을 합쳐 실제 파일 경로로 만들기
    
    if not os.path.isfile(full_path):
    # 위에서 만든 full_path 경로에 파일이 실제로 존재하는지 확인
        raise FileNotFoundError(f"{file_path} not found in targets")
    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()



@mcp.tool()
def write_file(file_path: str, content: str) -> str:
    # 1. 현재 시각으로 결과 디렉토리에 이름 생성
    timestamp = time.strftime("%Y%m%d%H%M%S")
    results_dir = os.path.join(os.path.dirname(__file__), f"resulrs_{timestamp}")
    
    # 2. 결과 디렉토리 생성(이미 있다면 그대로 사용)
    os.makedirs(results_dir, exist_ok=True)
    
    # 3. 결과 디렉토리와 파일 이름 합쳐 전체 경로 생성
    full_path = os.path.abspath(os.path.join(results_dir, file_path))
    
    # 4. 보안 검증: 결과 디렉토리 내부에만 쓰기 허용
    results_dir_abs = os.path.abspath(results_dir)
    if not full_path.startswith(results_dir_abs):
        raise ValueError("Invalid file path: writing outside results directory is not allowed")
    
    # 5. 파일 쓰기
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    # 6. 성공 메시지 반환
    return f"File written to {full_path}"
    
    
    
    
if __name__ == "__main__":
    mcp.run(transport='stdio')