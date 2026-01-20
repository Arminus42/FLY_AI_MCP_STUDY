import logging

import os
import time
import shutil
import glob
import subprocess
import re
import json

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("tools-task-2")


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TARGET_DIR = os.path.join(BASE_DIR, "targets")

# 서버 실행 시점의 타임스탬프 고정
TIMESTAMP = time.strftime("%Y%m%d%H%M%S")
RESULTS_DIR = os.path.join(TARGET_DIR, f"task2_results_{TIMESTAMP}")
BEST_DIR = os.path.join(BASE_DIR, "best_coverages")

@mcp.tool()
def list_files() -> str:
    files = [f for f in os.listdir(TARGET_DIR) if f.endswith(".py") and not f.startswith("test_") and os.path.isfile(os.path.join(TARGET_DIR, f))]
    return "\n".join(files)

@mcp.tool()
def read_file(file_path: str) -> str:
    # 파일명만 왔을 경우를 대비해 targets 내부 탐색
    full_path = os.path.join(TARGET_DIR, os.path.basename(file_path))
    if not os.path.exists(full_path):
        return f"Error: {file_path} not found in targets."
    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()

@mcp.tool()
def save_test_file(file_name: str, content: str, folder_name: str):
    # folder_name 인자를 사용하여 일관된 폴더에 저장
    target_folder = os.path.join(TARGET_DIR, folder_name)
    os.makedirs(target_folder, exist_ok=True)
    full_path = os.path.join(target_folder, file_name)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Saved to {full_path}"

@mcp.tool()
def run_pytest_and_coverage(test_file_path: str, target_file_name: str) -> str:
    try:
        module_name = target_file_name.replace('.py', '')
        # RESULTS_DIR 경로에서 테스트 파일 탐색
        abs_test_path = os.path.join(RESULTS_DIR, os.path.basename(test_file_path))
        
        env = os.environ.copy()
        env["PYTHONPATH"] = TARGET_DIR + os.pathsep + env.get("PYTHONPATH", "")

        cmd = ["python3", "-m", "pytest", f"--cov={module_name}", "--cov-report=term-missing", abs_test_path]
        
        # 반드시 targets 폴더를 작업 디렉토리(cwd)로 설정
        result = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=TARGET_DIR)
        
        output = result.stdout + result.stderr
        match = re.search(rf"{module_name}\.py\s+\d+\s+\d+\s+(\d+)%", output)
        coverage_percent = int(match.group(1)) if match else 0
        
        return json.dumps({"coverage": coverage_percent, "report": output})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def finalize_results(coverage_data: str):
    try:
        data = json.loads(coverage_data)
        os.makedirs(BEST_DIR, exist_ok=True)
        for target_name in data.keys():
            src = os.path.join(RESULTS_DIR, f"test_{target_name}.py")
            dst = os.path.join(BEST_DIR, f"test_{target_name}.py")
            if os.path.exists(src): shutil.copy2(src, dst)
        
        summary_path = os.path.join(BASE_DIR, "best_coverages.json")
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return "Finalization complete."
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport='stdio')
