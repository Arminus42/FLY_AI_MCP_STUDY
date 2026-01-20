import os
import glob
import json
import logging
import datetime
import subprocess
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from mcp.server.fastmcp import FastMCP

# --- LOGGING CONFIGURATION ---
# We configure logging to write to stderr so it doesn't break the MCP JSON-RPC on stdout.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [SERVER] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

mcp = FastMCP("tools-task-2")

# Robust absolute paths
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
TARGET_DIR = os.path.join(PROJECT_ROOT, "targets")

# --- Helper: Sanitize LLM Output ---
def _sanitize_test_code(code: str) -> str:
    """
    Strips top-level imports and whitespace from LLM output.
    This ensures we only append the test function, not duplicate headers.
    """
    lines = code.split('\n')
    filtered = []
    for line in lines:
        if re.match(r'^(import|from)\s+', line):
            continue
        if line.startswith('if __name__'):
            continue
        filtered.append(line)
    return '\n'.join(filtered).strip()

def _test_file_header(module_name: str) -> str:
    return f"""import os
import sys
import pytest

# Dynamic path setup
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
TARGETS_DIR = os.path.join(PROJECT_ROOT, "targets")

if TARGETS_DIR not in sys.path:
    sys.path.insert(0, TARGETS_DIR)

from {module_name} import *
"""

def _assemble_test_file(module_name: str, test_snippets: List[str]) -> str:
    return _test_file_header(module_name) + "\n\n" + "\n\n".join(test_snippets) + "\n"

def _pick_cov_target_key(cov_data: dict, module_name: str) -> Optional[str]:
    files = cov_data.get("files", {})
    for filename in files.keys():
        if filename.endswith(f"{module_name}.py"):
            return filename
    return None

def _run_coverage_check(
    test_file_abs: str,
    module_name: str,
    module_dir_abs: str,
    cov_json_abs: str,
    timeout_s: int = 12,
) -> Tuple[bool, int, List[int], str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = module_dir_abs + os.pathsep + env.get("PYTHONPATH", "")

    os.makedirs(os.path.dirname(cov_json_abs), exist_ok=True)
    if os.path.exists(cov_json_abs):
        try: os.remove(cov_json_abs)
        except OSError: pass

    cmd = [
        "pytest",
        test_file_abs,
        f"--cov={module_name}",
        f"--cov-report=json:{cov_json_abs}",
        "-q",
    ]

    try:
        res = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
    except subprocess.TimeoutExpired:
        return False, 0, [], "Timeout running pytest."

    out = (res.stdout or "") + "\n" + (res.stderr or "")

    if "unrecognized arguments: --cov" in out:
        error_msg = "CRITICAL ERROR: 'pytest-cov' is not installed."
        logger.error(error_msg)
        return False, 0, [], error_msg

    if not os.path.exists(cov_json_abs):
        return False, 0, [], f"Coverage report failed to generate.\nOutput:\n{out}"

    try:
        with open(cov_json_abs, "r", encoding="utf-8") as f:
            cov_data = json.load(f)
    except Exception as e:
        return False, 0, [], f"JSON Error: {e}\n{out}"

    target_key = _pick_cov_target_key(cov_data, module_name)
    if not target_key:
        return False, 0, [], f"Module '{module_name}' not found in coverage report.\n{out}"

    file_data = cov_data["files"][target_key]
    percent = int(file_data["summary"]["percent_covered"])
    missing = list(file_data.get("missing_lines", []))

    return True, percent, missing, out

def _read_module_source(module_file_abs: str) -> List[str]:
    with open(module_file_abs, "r", encoding="utf-8") as f:
        return f.read().splitlines()

def _format_uncovered_context(
    module_lines: List[str],
    missing_lines: List[int],
    context: int = 2,
    max_blocks: int = 12,
) -> str:
    if not missing_lines: return "No missing lines."
    missing_sorted = sorted(set([ln for ln in missing_lines if isinstance(ln, int) and ln > 0]))
    
    blocks = []
    used = 0
    groups = []
    cur = [missing_sorted[0]]
    for ln in missing_sorted[1:]:
        if ln <= cur[-1] + 3: cur.append(ln)
        else:
            groups.append(cur)
            cur = [ln]
    groups.append(cur)

    for g in groups:
        if used >= max_blocks: break
        start = max(1, g[0] - context)
        end = min(len(module_lines), g[-1] + context)
        snippet = []
        for ln in range(start, end + 1):
            mark = ">>" if ln in set(g) else "  "
            if 0 <= ln - 1 < len(module_lines):
                snippet.append(f"{mark} {ln:4d}: {module_lines[ln - 1]}")
        blocks.append("\n".join(snippet))
        used += 1
    return "\n\n".join(blocks)

@dataclass
class TaskInfo:
    module_name: str
    module_file_rel: str
    module_file_abs: str
    module_dir_abs: str

@dataclass
class GlobalState:
    queue: List[str] = field(default_factory=list)
    tasks: Dict[str, TaskInfo] = field(default_factory=dict)
    current: Optional[TaskInfo] = None
    accepted_snippets: List[str] = field(default_factory=list)
    coverage_pct: int = 0
    missing_lines: List[int] = field(default_factory=list)
    results_dir: Optional[str] = None
    best_dir: str = field(default_factory=lambda: os.path.join(PROJECT_ROOT, "best_coverages"))
    coverages: Dict[str, int] = field(default_factory=dict)

STATE = GlobalState()

def _ensure_dirs():
    os.makedirs(STATE.best_dir, exist_ok=True)
    if STATE.results_dir: os.makedirs(STATE.results_dir, exist_ok=True)
def _write_coverages_json():
    os.makedirs(STATE.best_dir, exist_ok=True)
    with open(os.path.join(STATE.best_dir, "coverages.json"), "w") as f:
        json.dump(STATE.coverages, f, indent=2)

# --- MCP TOOLS WITH LOGGING ---

@mcp.tool()
def init_queue() -> str:
    logger.info("Function 'init_queue' called.")
    global STATE
    STATE = GlobalState()
    if not os.path.isdir(TARGET_DIR): 
        logger.error(f"Target dir {TARGET_DIR} not found.")
        return f"Error: {TARGET_DIR} not found."

    module_files = sorted(glob.glob(os.path.join(TARGET_DIR, "example*.py")))
    if not module_files:
        module_files = sorted(glob.glob(os.path.join(TARGET_DIR, "example*", "example*.py")))
    if not module_files: 
        logger.error("No example*.py files found.")
        return "Error: No example*.py files found."

    tasks = {}
    for path in module_files:
        base = os.path.basename(path)
        module_name = os.path.splitext(base)[0]
        tasks[module_name] = TaskInfo(
            module_name=module_name,
            module_file_rel=os.path.relpath(path, TARGET_DIR),
            module_file_abs=os.path.abspath(path),
            module_dir_abs=os.path.dirname(os.path.abspath(path))
        )

    STATE.tasks = tasks
    STATE.queue = sorted(tasks.keys(), key=lambda s: (len(s), s))
    STATE.results_dir = os.path.join(PROJECT_ROOT, f"task2_results_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
    _ensure_dirs()
    _write_coverages_json()

    logger.info(f"Queue initialized with {len(STATE.queue)} modules: {STATE.queue}")
    return json.dumps({"status": "initialized", "count": len(STATE.queue), "modules": STATE.queue})

@mcp.tool()
def next_task() -> str:
    logger.info("Function 'next_task' called.")
    if not STATE.queue: 
        logger.info("Queue is empty. Returning QUEUE_EMPTY.")
        return "QUEUE_EMPTY"
    
    module = STATE.queue.pop(0)
    task = STATE.tasks[module]
    STATE.current = task
    STATE.accepted_snippets = []
    STATE.coverage_pct = 0
    STATE.missing_lines = []
    _ensure_dirs()

    logger.info(f"Starting Task: {module}")

    # Initial smoke test
    smoke = f"""def test_smoke_import():
    assert hasattr({task.module_name}, "__doc__") or True"""
    STATE.accepted_snippets = [smoke]

    test_abs = os.path.join(STATE.results_dir, f"test_{task.module_name}.py")
    with open(test_abs, "w") as f: f.write(_assemble_test_file(task.module_name, STATE.accepted_snippets))
    
    ok, pct, missing, out = _run_coverage_check(
        test_abs, task.module_name, task.module_dir_abs, 
        os.path.join(STATE.results_dir, "_cov", f"{task.module_name}.json")
    )
    if ok:
        STATE.coverage_pct = pct
        STATE.missing_lines = missing
        logger.info(f"Initial smoke test passed. Coverage: {pct}%")
    else:
        logger.warning(f"Initial smoke test failed. Output: {out[:100]}...")

    with open(task.module_file_abs, "r") as f: code = f.read()
    return f"Target: {task.module_name}\nCoverage: {STATE.coverage_pct}%\nCode:\n{code}"

@mcp.tool()
def get_current_status() -> str:
    logger.info("Function 'get_current_status' called.")
    if not STATE.current:
        remaining_count = len(STATE.queue)
        status_msg = f"IDLE. {remaining_count} items remaining."
        logger.info(f"Returning status: {status_msg}")
        
        if remaining_count > 0:
            return json.dumps({
                "status": "IDLE", 
                "message": f"No active task. {remaining_count} items remaining in queue.",
                "next_action": "Call 'next_task' to proceed."
            })
        else:
            return json.dumps({
                "status": "COMPLETED", 
                "message": "All tasks in queue are finished."
            })

    logger.info(f"Active Task: {STATE.current.module_name}, Cov: {STATE.coverage_pct}%")
    return json.dumps({
        "status": "ACTIVE",
        "module": STATE.current.module_name, 
        "coverage": STATE.coverage_pct, 
        "missing_lines": STATE.missing_lines
    })

@mcp.tool()
def get_uncovered_context(context: int = 2) -> str:
    logger.info(f"Function 'get_uncovered_context' called with context={context}")
    if not STATE.current: return "Error: No active task."
    
    lines = _read_module_source(STATE.current.module_file_abs)
    result = _format_uncovered_context(lines, STATE.missing_lines, context=context)
    
    # 
    # (Conceptual diagram: we log the size of the result instead)
    logger.info(f"Returning {len(result)} chars of context context.")
    return result

@mcp.tool()
def submit_test_case(test_code: str) -> str:
    logger.info("Function 'submit_test_case' called.")
    if not STATE.current: return "Error: No active task."
    
    # Log snippet of submitted code for debugging
    code_preview = test_code.strip().split('\n')[0]
    logger.info(f"Received code: {code_preview}...")

    if "def test_" not in test_code: 
        logger.warning("Submission rejected: No 'def test_' found.")
        return "REJECTED: Must contain 'def test_...'"

    task = STATE.current
    clean_code = _sanitize_test_code(test_code)
    candidate = STATE.accepted_snippets + [clean_code]
    test_abs = os.path.join(STATE.results_dir, f"test_{task.module_name}.py")
    
    with open(test_abs, "w") as f: f.write(_assemble_test_file(task.module_name, candidate))

    ok, pct, missing, out = _run_coverage_check(
        test_abs, task.module_name, task.module_dir_abs, 
        os.path.join(STATE.results_dir, "_cov", f"{task.module_name}.json")
    )

    if not ok:
        logger.warning(f"Test Failed. Reverting. Output: {out[:100]}...")
        with open(test_abs, "w") as f: f.write(_assemble_test_file(task.module_name, STATE.accepted_snippets))
        return f"REJECTED: Test failed.\n{out}"

    logger.info(f"Test Accepted! Coverage improved to {pct}%")
    STATE.accepted_snippets.append(clean_code)
    STATE.coverage_pct = pct
    STATE.missing_lines = missing
    
    with open(os.path.join(STATE.best_dir, f"test_{task.module_name}.py"), "w") as f:
        f.write(_assemble_test_file(task.module_name, STATE.accepted_snippets))

    return f"ACCEPTED. Coverage: {pct}%"

@mcp.tool()
def finalize_task() -> str:
    logger.info("Function 'finalize_task' called.")
    if not STATE.current: return "Error: No active task to finalize."
    
    module_name = STATE.current.module_name
    pct = STATE.coverage_pct
    
    STATE.coverages[module_name] = pct
    _write_coverages_json()
    
    STATE.current = None
    remaining = len(STATE.queue)
    
    logger.info(f"Finalized '{module_name}' with {pct}%. Remaining in queue: {remaining}")
    return f"Task '{module_name}' finalized with {pct}% coverage. {remaining} modules remaining in queue. Please call 'next_task'."

if __name__ == "__main__":
    mcp.run(transport="stdio")