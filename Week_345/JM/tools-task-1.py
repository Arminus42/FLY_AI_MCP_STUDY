import logging

import os
import time
import shutil
import glob
import subprocess
import re
import json

# MCP 서버 초기화
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("tools-task-1")

PYTHON_PATH = "/usr/bin/python"
TARGET_DIR = os.path.join(os.path.dirname(__file__), "targets")

@mcp.tool()
def list_files() -> str:
    """
    Tool: 테스트를 생성할 대상 디렉토리의 모든 Python 파일 목록 조회
    """
    try:
        if not os.path.exists(TARGET_DIR):
            return f"오류: 대상 디렉토리를 찾을 수 없습니다: {TARGET_DIR}"
        
        # 모든 하위 디렉토리에서 .py 파일 검색
        files = []
        for root, _, filenames in os.walk(TARGET_DIR):
            for filename in filenames:
                if filename.endswith('.py'):
                    rel_path = os.path.relpath(os.path.join(root, filename), TARGET_DIR)
                    files.append(rel_path)
        
        if not files:
            return f"대상 디렉토리에 Python 파일이 없습니다: {TARGET_DIR}"
        
        return "대상 디렉토리의 Python 파일:\n" + "\n".join(files)
    
    except Exception as e:
        return f"파일 목록 조회 오류: {str(e)}"


@mcp.tool()
def read_file(file_path: str) -> str:
    """
    Tool: 대상 디렉토리의 Python 파일 내용 읽기
    
    보안 가드레일: 경로 정규화, TARGET_DIR 외부 접근 차단, .py 파일만 허용
    """
    try:
        # 경로 정규화 및 TARGET_DIR과 결합
        normalized = os.path.normpath(file_path).lstrip(os.sep).lstrip('/')
        full_path = os.path.abspath(os.path.join(TARGET_DIR, normalized))
        target_abs = os.path.abspath(TARGET_DIR)
        
        # 보안 검증
        if not full_path.startswith(target_abs):
            return f"보안 오류: {TARGET_DIR} 외부 파일 접근이 차단되었습니다"
        
        if not os.path.exists(full_path):
            return f"오류: 파일을 찾을 수 없습니다: {file_path}"
        
        if not full_path.endswith('.py'):
            return f"오류: Python 파일이 아닙니다: {file_path}"
        
        # 파일 읽기
        with open(full_path, 'r', encoding='utf-8') as f:
            return f"{file_path} 파일 내용:\n\n{f.read()}"
    
    except Exception as e:
        return f"파일 읽기 오류: {str(e)}"


@mcp.tool()
def write_file(file_path: str, content: str) -> str:
    """
    Tool: 테스트 파일을 results 디렉토리에 저장
    
    보안 가드레일: 파일명만 추출, test_ 접두사/py 확장자 강제, results_dir 외부 쓰기 차단
    """
    try:
        # results 디렉토리 생성
        timestamp = time.strftime("%Y%m%d%H%M%S")
        results_dir = os.path.join(os.path.dirname(__file__), f"results_{timestamp}")
        os.makedirs(results_dir, exist_ok=True)
        
        # 파일명 정규화 (경로 제거, test_ 접두사/py 확장자 강제)
        filename = os.path.basename(file_path)
        if not filename.endswith('.py'):
            filename += '.py'
        if not filename.startswith('test_'):
            filename = f"test_{filename.replace('.py', '')}.py"
        
        # 최종 경로 생성 및 보안 검증
        full_path = os.path.abspath(os.path.join(results_dir, filename))
        results_abs = os.path.abspath(results_dir)
        
        if not full_path.startswith(results_abs):
            return f"보안 오류: {results_dir} 외부 파일 쓰기가 차단되었습니다"
        
        # 파일 쓰기
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"테스트 파일 저장 완료: {full_path}"
    
    except Exception as e:
        return f"파일 쓰기 오류: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport='stdio')