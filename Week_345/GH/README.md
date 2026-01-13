# CS454 Assignment 5: MCP Python Testing Automation Agent

The aim of this assignment is to implement MCP tools and client for automation of testing for a subset of Python. To achieve this, you first need to make the agent read the target `.py` file, and then make it generate inputs for functions in the file in the format of pytest unit test cases. The agent should also automatically run `pytest` and measure statement coverage.

## Requirements

1. Run `pip install -r requirements.txt` in the project
2. Run `export OPENAI_API_KEY=<Your OpenAI API Key>`

## Target Subset of Python

The target subset of Python includes some of the target subsets from [Assignment #1](https://github.com/coinse/cs454-sbst?tab=readme-ov-file#target-subset-of-python) as well as several simple Python programs. Look for details in `targets/`.

## Task 1: Implement MCP Server for Test File Management

In this task, you will implement a basic MCP server that can call 3 simple tools. The template client code `mcp-client-task-1.py` will be provided.

First, implement the necessary tool functions for the task, in `tools-task-1.py`. Your tool should include the following:

- `list_files() -> str`: List all Python files in the target directory `TARGET_DIR` to generate tests for.
- `read_file(file_path: str) -> str`: Read the contents of a Python file in the target directory to generate tests for.
- `write_file(file_path: str, content: str) -> str`: Write content to a Python file in the target directory.
  ⚠️ **Important**: Includes a guardrail to prevent writing to a random directory

Run the MCP using `python mcp-client-task-1.py tools-task-1.py <prompt>`.

Your solution should write the test file of a given example in another directory, with the naming convention `results_<YYYYMMDDHHMMS>`. It should be able to handle the following prompt:

`List the files in /targets, read example#.py, and generate a test file for example#.py.`

which will be provided as an argument, with integers from 1 through 7 for `#`. The same prompt will be used to give a score for task 1.

**Tip**: You don't have to use the outlined arguments for the functions above; You can also try to create a config file for each of the examples, and make each tool refer to the config file for `file_path`.

For example,
```
read_file():
  file_path = CONFIG["file_path"]
...
```
would also be allowed.

## Task 2: Coverage-driven Test Generation

In this task, you will implement a MCP server that can run `pytest`, measure coverage of the test file, and generate an improved test file that reaches higher coverage. You are free to implement any heuristic, for example, your MCP server might iterate through a fixed number of tries and halt if there are no coverage changes for 3 tries.

Either copy or create a new file named `mcp-client-task-2.py` and `tools-task-2.py`. You can freely add more MCP server functions in `tools-task-2.py`, but you might want to start with these functions:

- `run_pytest(test_file_path: str) -> str`: Run pytest on the given Python test file in the target directory.
- `measure_coverage(test_file_path: str) -> str`: Measure code coverage for the generated test files in the target directory.

But again, you can freely add more functions if necessary, for example `get_uncovered_lines`. Furthermore, you can also edit `mcp-client-task-2.py` for higher efficiency.

Run the MCP server through:
```
$ python mcp-client-task-2.py tools-task-2.py
```

### Requirements

- Your MCP server should create a test file for all of the examples under `/targets` and save it into `task2_results_<YYYYMMDDHHMMSS>`.
- Each test file should follow the naming convention `test_example#.py`. For example, for `example1.py`, the test file name should be `test_example1.py`. 
- Also, each test file should import the functions directly from the `example1.py`. For example, it should start with `import example1`, NOT `import targets.example1` or `import example1.example1`.
- Submit the best test file with the highest coverage in `best_coverages/` folder. Also, include a `json` file that outlines the coverage reached by each test file, with the format that shows the line coverage percentage (without % sign):
```
{'example1': 45, 'example2': 50, ... }
```
- The grading will be based on (1) whether your MCP server can generate tests based on coverage and (2) the coverage reached by your best results.

## Task 3: Implementing SBST

In this task, you will implement a MCP server that can run SBST, which you have implemented in Assignment 1. Copy and paste your `sbst.py` file from Assignment 1.

Create two files, `mcp-client-task-3.py` and `tools-task-3.py`.

Run the MCP server through:

```
$ python mcp-client-task-3.py tools-task-3.py
```

### Requirements

- Your MCP server should be able to handle your `sbst.py`. Implement a function tool in `mcp-client-task-3.py` named `run_sbst`.
- Similar to Task 2, your MCP server should create a test file for all of the examples under `/targets` and save it into `task3_results_<YYYYMMDDHHMMSS>`.
- Additionally, save the trajectory of tool calls as a txt file, named `trajectory_example#.txt` in `/trajectory`.
- ⚠️ **Important**: Task 3 will only be tested on `example1.py`, `example2.py`, and `example3.py`, only the target files from Assignment 1.

## Report

Write, and commit a simple report detailing your implementations, and include it as a PDF file in the repository. In particular, try to discuss the following point:

- How did you implement guardrails?
- Simple state diagram (no need to be complex) of how your MCP server runs
- What did you feel using an MCP server for generating test cases for a code?
- Additionally, please leave a feedback about Assignment #5 in general.
