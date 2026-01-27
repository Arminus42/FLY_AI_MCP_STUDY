import logging

import os
import time
import shutil
import glob
import subprocess
import re
import json
import sbst  # sbst.py must be in the same directory

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("tools-task-3")

PYTHON_PATH = "/usr/bin/python"
TARGET_DIR = os.path.join(os.path.dirname(__file__), "targets")
TRAJ_DIR = os.path.join(os.path.dirname(__file__), "trajectory")

ALLOWED = {"example1.py": 1, "example2.py": 2, "example3.py": 3}

def _timestamp() -> str:
    return time.strftime("%Y%m%d%H%M%S", time.localtime())


# sbst를 실행하고 결과물 저장
# 클라이언트가 mcp 프로토콜로 run_sbst 도구 호출 가능해짐
@mcp.tool()
def run_sbst(target: str) -> str:
    """
    Task 3 tool:
    - Accepts only example1.py/example2.py/example3.py
    - Writes generated tests to ./targets/task3_results_<YYYYMMDDHHMMSS>/
    - Writes tool-call trajectory to ./trajectory/trajectory_example#.txt
    Returns a summary string.
    """
    if target not in ALLOWED:
        raise ValueError("Only example1.py, example2.py, example3.py are allowed.")

    # 대상 파일 경로 확인
    target_path = os.path.join(TARGET_DIR, target)
    if not os.path.exists(target_path):
        raise FileNotFoundError(f"Target file not found: {target_path}")

    # 결과물 저장 
    ts = _timestamp()
    out_dir = os.path.join(TARGET_DIR, f"task3_results_{ts}")
    os.makedirs(out_dir, exist_ok=True)

    # 호출 기록 저장 (trajectory)
    os.makedirs(TRAJ_DIR, exist_ok=True)
    ex_num = ALLOWED[target]
    traj_path = os.path.join(TRAJ_DIR, f"trajectory_example{ex_num}.txt")

    # sbst 실행 ======================
    start = time.time()
    test_path = None
    err = None

    try:
        test_path = sbst.run_sbst(target_path, out_dir)
    except Exception as e:
        err = repr(e)

    elapsed = time.time() - start

    with open(traj_path, "a", encoding="utf-8") as f:
        f.write(f"[CALL] ts={ts}\n")
        f.write(f" target={target}\n")
        f.write(f" out_dir={out_dir}\n")
        f.write(f" elapsed_sec={elapsed:.6f}\n")
        if err:
            f.write(" status=ERROR\n")
            f.write(f" error={err}\n")
        else:
            f.write(" status=OK\n")
            f.write(f" generated_test={test_path}\n")
        f.write("\n")

    if err:
        raise RuntimeError(err)

    return f"OK: {test_path}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
