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
    
    Returns:
        Python 파일 목록 문자열 또는 오류 메시지
    """
    try:
        # 대상 디렉토리 존재 여부 확인
        if not os.path.exists(TARGET_DIR):
            return f"오류: 대상 디렉토리를 찾을 수 없습니다: {TARGET_DIR}"
        
        # os.walk()로 모든 하위 디렉토리 탐색하여 .py 파일 수집
        # os.walk()는 (root, dirs, files) 튜플을 반환
        files = []
        for root, dirs, filenames in os.walk(TARGET_DIR):
            for filename in filenames:
                if filename.endswith('.py'):
                    # 절대 경로 생성
                    full_path = os.path.join(root, filename)
                    # TARGET_DIR 기준 상대 경로로 변환 (예: example1/example1.py)
                    rel_path = os.path.relpath(full_path, TARGET_DIR)
                    files.append(rel_path)
        
        # 파일이 없는 경우 처리
        if not files:
            return f"대상 디렉토리에 Python 파일이 없습니다: {TARGET_DIR}"
        
        return "대상 디렉토리의 Python 파일:\n" + "\n".join(files)
    
    except Exception as e:
        return f"파일 목록 조회 오류: {str(e)}"


@mcp.tool()
def read_file(file_path: str) -> str:
    """
    Tool: 대상 디렉토리의 Python 파일 내용 읽기
    
    보안 가드레일:
    - 경로 정규화로 디렉토리 traversal 공격 방지 (../../etc/passwd 같은 공격)
    - TARGET_DIR 외부 파일 접근 차단
    - Python 파일만 읽기 허용
    
    Args:
        file_path: 읽을 Python 파일 경로 (예: 'example1/example1.py')
    
    Returns:
        파일 내용 또는 오류 메시지
    """
    try:
        # 보안 1: 경로 정규화
        # os.path.normpath()는 '..'와 '.' 같은 요소를 해석하여 정규화
        normalized_path = os.path.normpath(file_path)
        # 선행 슬래시 제거 (절대 경로를 상대 경로로 변환)
        normalized_path = normalized_path.lstrip(os.sep).lstrip('/')
        
        # TARGET_DIR과 결합하여 전체 경로 생성
        full_path = os.path.join(TARGET_DIR, normalized_path)
        
        # 보안 2: TARGET_DIR 외부 접근 차단
        # 절대 경로로 변환하여 비교
        abs_path = os.path.abspath(full_path)
        abs_target_dir = os.path.abspath(TARGET_DIR)
        
        # 절대 경로가 TARGET_DIR로 시작하는지 확인
        if not abs_path.startswith(abs_target_dir):
            return f"보안 오류: {TARGET_DIR} 외부 파일 접근이 차단되었습니다"
        
        # 파일 존재 여부 확인
        if not os.path.exists(abs_path):
            return f"오류: 파일을 찾을 수 없습니다: {file_path}"
        
        # 보안 3: Python 파일만 허용
        if not abs_path.endswith('.py'):
            return f"오류: Python 파일이 아닙니다: {file_path}"
        
        # 파일 읽기 (UTF-8 인코딩 사용)
        with open(abs_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return f"{file_path} 파일 내용:\n\n{content}"
    
    except Exception as e:
        return f"파일 읽기 오류: {str(e)}"


@mcp.tool()
def write_file(file_path: str, content: str) -> str:
    """
    Tool: 테스트 파일을 results 디렉토리에 저장
    
    보안 가드레일:
    - 파일명만 추출하여 디렉토리 경로 조작 방지
    - test_ 접두사 강제
    - .py 확장자 강제
    - results_dir 외부 쓰기 차단
    
    Args:
        file_path: 테스트 파일 이름 (예: 'test_example1.py')
        content: 테스트 파일 내용
    
    Returns:
        성공 메시지 또는 오류 메시지
    """
    try:
        # 타임스탬프 기반 results 디렉토리 생성
        # 형식: results_YYYYMMDDHHMMSS
        timestamp = time.strftime("%Y%m%d%H%M%S")
        results_dir = os.path.join(os.path.dirname(__file__), f"results_{timestamp}")
        
        # 디렉토리가 없으면 생성 (exist_ok=True로 이미 존재해도 오류 없음)
        os.makedirs(results_dir, exist_ok=True)
        
        # 보안 1: 파일명만 추출 (경로 제거)
        # os.path.basename()은 경로의 마지막 부분만 추출
        # 예: 'example1/test_example1.py' -> 'test_example1.py'
        filename = os.path.basename(file_path)
        
        # 보안 2: .py 확장자 강제
        if not filename.endswith('.py'):
            filename += '.py'
        
        # 보안 3: test_ 접두사 강제
        if not filename.startswith('test_'):
            # .py 제거하고 test_ 접두사 추가
            base_name = filename.replace('.py', '')
            filename = f'test_{base_name}.py'
        
        # 최종 경로 생성
        full_path = os.path.join(results_dir, filename)
        
        # 보안 4: results_dir 외부 쓰기 차단
        abs_path = os.path.abspath(full_path)
        abs_results_dir = os.path.abspath(results_dir)
        
        if not abs_path.startswith(abs_results_dir):
            return f"보안 오류: {results_dir} 외부 파일 쓰기가 차단되었습니다"
        
        # 파일 쓰기 (UTF-8 인코딩 사용)
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"테스트 파일 저장 완료: {full_path}"
    
    except Exception as e:
        return f"파일 쓰기 오류: {str(e)}"


if __name__ == "__main__":
    # STDIO 트랜스포트로 MCP 서버 실행
    # 표준 입출력을 통해 클라이언트와 통신
    mcp.run(transport='stdio')