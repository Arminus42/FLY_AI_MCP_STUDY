import logging

import os
from pickletools import pybytes_or_str
import glob
import subprocess
import json
from mcp.server.fastmcp import FastMCP
from collections import defaultdict
import coverage
import subprocess
import sys

mcp = FastMCP("tools-task-2")

PYTHON_PATH = sys.executable
CURRENT_ENV_PATHS = os.pathsep.join(sys.path)
TARGET_DIR = os.path.join(os.path.dirname(__file__), "targets")

dict_cov = defaultdict()

def get_missing_info(cov, file_path: str) -> str:
    """
    Get missing information from a test python file in the target directory.
    Args:
        file_path (str): The path of the test python file to get missing information from.
    """
    analysis = cov.analysis2(file_path)
    missing_line_number = analysis[-2]
    missing_info = ""
    if missing_line_number:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            missing_detail = [lines[i-1].strip() for i in missing_line_number]
        missing_info = "\n".join(missing_detail)
    return analysis, missing_info

@mcp.tool()
def modify_file(file_path: str, content: str) -> str:
    """
    Modify content of a test python file in the target directory.
    Args:
        file_path (str): The path of the test python file to modify.
        content (str): The content to write to the file.
    """

    if not file_path.startswith(TARGET_DIR):
        return f"Error: Access denied. You can only write files within {TARGET_DIR}"
    try:
        with open(file_path, "w") as f:
            f.write(content)
            return f"Successfully wrote content to {file_path}"

    except Exception as e:
        return f"Error writing file: {e}"

@mcp.tool()
def list_files() -> str:
    """
    List all Python files in the target directory to generate tests for.
    """
    files = glob.glob(os.path.join(TARGET_DIR, 'example3/test_example*.py'))
    if not files:
        return "No Python files found in the target directory."
    return "\n".join(files)

@mcp.tool()
def run_pytest(file_path: str) -> str:
    """
    Run pytest on the given Python test file in the target directory.
    args:
        file_path (str): The path of the Python file to run pytest on.
    """
    logging.info(f"Running pytest on: {file_path}")
    # 1. 파일의 절대 경로를 구합니다 (안전성을 위해)
    abs_file_path = os.path.abspath(file_path)
    if not os.path.exists(abs_file_path):
        return f"Error: File not found at {abs_file_path}"
    # 2. 실행할 기준 디렉토리를 구합니다 (테스트 파일이 있는 폴더)
    dir_path = os.path.dirname(abs_file_path)

    cov_file = os.path.join(dir_path, ".coverage")
    if os.path.exists(cov_file):
        try:
            os.remove(cov_file)
        except Exception as e:
            logging.warning(f"Could not remove old .coverage file: {e}")

    cmd = [sys.executable, "-m", "coverage", "run", "--branch", "--source=.",  "-m", "pytest", abs_file_path]

    try:
        result = subprocess.run(
            cmd,
            cwd=dir_path,
            capture_output=True,
            text=True,
            check=False
        )
        
        # 3. 상세 결과 조립
        output = []
        output.append(f"Pytest exited with code: {result.returncode}")
        if result.returncode != 0:
            output.append("WARNING: Pytest failed. Coverage file might not be generated or updated.")

        if result.stdout:
            output.append(f"--- Standard Output ---\n{result.stdout}")
        
        if result.stderr:
            # 특히 returncode 2나 4일 때 이 부분이 중요합니다.
            output.append(f"--- Standard Error (Issues found) ---\n{result.stderr}")
        output_string = "\n".join(output)
        logging.info(f"pytest result: {result.returncode}, {output_string}")
        return output_string

    except Exception as e:
        logging.info(f"Exception: {str(e)}")
        return f"An error occurred while running pytest: {str(e)}"

@mcp.tool()
def measure_coverage(file_path: str) -> str:
    """
    Measure code coverage for the generated ".coverage" file in the target directory.
    Args:
        file_path (str): The path of the ".coverage" file in the target directory, including must "/.coverage".
    """
    if file_path.split('/')[-1] != '.coverage':
        file_path = os.path.join(os.path.dirname(file_path), '.coverage')

    file_name = file_path.split('/')[-2]
    # cov = coverage.Coverage(data_file=file_path, include='test_example*.py')
    try: 
        cov = coverage.Coverage(data_file=file_path)
        cov.load()
        score = cov.report()
        logging.info(f"befor: {dict_cov}, {score}")
        if file_name in dict_cov:
            if dict_cov[file_name][0] >= score:
                dict_cov[file_name][1] += 1
            else:
                dict_cov[file_name] = [score, 0]
            
        else:
            dict_cov[file_name] = [score, 0]
        logging.info(f"after: {dict_cov}")

        target_source_path = os.path.join(os.path.dirname(file_path), f"{file_name}.py")
        target_analysis, target_missing_info = get_missing_info(cov, target_source_path)
        
        test_source_path = os.path.join(os.path.dirname(file_path), f"test_{file_name}.py")
        test_analysis, test_missing_info = get_missing_info(cov, test_source_path)
        
        output_string = (f"Current Coverage for {target_source_path}: {score}%\n"
                f"Retries: {dict_cov[file_name][1]}\n"
                f"Target Missing Lines: {target_analysis[-1]}\n"
                f"Target Unexecuted Code Snippets:\n{target_missing_info}"
                f"Test Missing Lines: {test_analysis[-1]}\n"
                f"Test Unexecuted Code Snippets:\n{test_missing_info}")
        logging.info(output_string)

        # return (f"Current Coverage for {target_source_path}: {score}%\n"
        #         f"Retries: {dict_cov[file_name][1]}\n"
        #         f"Missing Lines: {analysis[-1]}\n"
        #         f"Unexecuted Code Snippets:\n{missing_info}")
        
        return output_string
    except Exception as e:
        return f"An error occurred while measuring coverage: {str(e)}"
@mcp.tool()
def write_json_file() -> str:
    """
    Write dict_cov to a json file in the target directory.
    """
    
    # timestamp = time.strftime("%Y%m%d%H%M%S")
    save_dir = os.path.join(TARGET_DIR, 'result')
    os.makedirs(save_dir, exist_ok=True)

    try:
        dict_cov_json = json.dumps(dict_cov)
        with open(os.path.join(save_dir, "best_coverage.json"), "w") as f:
            f.write(dict_cov_json)
        return f"Successfully wrote content to {os.path.join(save_dir, 'best_coverage.json')}"

    except Exception as e:
        return f"Error writing file: {e}"

if __name__ == "__main__":
    mcp.run(transport='stdio')
