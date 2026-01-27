import os
import sys
import subprocess
import shutil
import datetime
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP("tools-task-3")

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TARGETS_ROOT = os.path.join(BASE_DIR, "targets")
SBST_SCRIPT = os.path.join(BASE_DIR, "sbst.py")

# Create the timestamped results directory
TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
RESULTS_DIR = os.path.join(BASE_DIR, f"task3_results_{TIMESTAMP}")
os.makedirs(RESULTS_DIR, exist_ok=True)

@mcp.tool()
def run_sbst(example_name: str) -> str:
    """
    Runs the SBST script (sbst.py) on a specified example.
    
    Args:
        example_name (str): The name of the example (e.g., 'example1'). 
    """
    # 1. Resolve path for nested structure: targets/example1/example1.py
    # Remove .py if included in argument to be safe
    base_name = example_name.replace(".py", "")
    target_path = os.path.join(TARGETS_ROOT, base_name, f"{base_name}.py")

    # 2. Validation
    if not os.path.exists(target_path):
        return f"Error: Target file not found at {target_path}"
    if not os.path.exists(SBST_SCRIPT):
        return f"Error: sbst.py not found at {SBST_SCRIPT}"

    try:
        # 3. Execute sbst.py
        # sbst.py generates 'test_<name>.py' in the SAME directory as the target
        result = subprocess.run(
            [sys.executable, SBST_SCRIPT, target_path],
            capture_output=True,
            text=True,
            timeout=120  # Timeout for SBST execution
        )
        
        if result.returncode != 0:
            return f"SBST Execution Failed for {base_name}:\n{result.stderr}"

        # 4. Locate and Move the generated file
        generated_filename = f"test_{base_name}.py"
        source_generated = os.path.join(TARGETS_ROOT, base_name, generated_filename)
        dest_generated = os.path.join(RESULTS_DIR, generated_filename)

        if os.path.exists(source_generated):
            shutil.move(source_generated, dest_generated)
            return f"Success: Generated {generated_filename} and moved to {RESULTS_DIR}."
        else:
            return f"Error: SBST ran, but output file {generated_filename} was not found at {source_generated}.\nOutput: {result.stdout}"

    except subprocess.TimeoutExpired:
        return f"Error: SBST execution timed out for {base_name}."
    except Exception as e:
        return f"Error running SBST: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport='stdio')