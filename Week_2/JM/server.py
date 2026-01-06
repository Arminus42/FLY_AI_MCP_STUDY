from pathlib import Path
from mcp.server.fastmcp import FastMCP
import asyncio

# 1. Server Initialize
# ---------------------------------------------------------
# [Task 1] FastMCP 서버 인스턴스 초기화
# 힌트: FasMCP 사용
# ---------------------------------------------------------
mcp = ____________________

# Data File Path
DATA_FILE = Path(__file__).parent / "todo.txt"

# --- Helper Functions ---
def _read_todos():
    """파일에서 할 일을 읽어오는 내부 함수"""
    if not DATA_FILE.exists():
        return []
    return [line.strip() for line in DATA_FILE.read_text(encoding="utf-8").splitlines() if line.strip()]

def _save_todos(todos):
    """파일에 할 일을 저장하는 내부 함수"""
    DATA_FILE.write_text("\n".join(todos) + "\n", encoding="utf-8")

# --- Resources ---
# ---------------------------------------------------------
# [Task 2] Resource 등록
# 힌트: 클라이언트가 "todo://list" 라는 주소(URI)로 데이터를 읽어야 함
# ---------------------------------------------------------
@____________________
def get_todo_list() -> str:
    """현재 저장된 모든 할 일 목록을 반환합니다."""
    todos = _read_todos()
    if not todos:
        return "할 일이 없습니다."

    return "\n".join(f"{i+1}. {task}" for i, task in enumerate(todos))

# --- Tools ---
# ---------------------------------------------------------
# [Task 3] Tool 등록
# 힌트: 상태 변경 함수는 Write가 필요하므로 Resource가 아니라 Tool로 등록해야 함
# ---------------------------------------------------------
@____________________
async def add_todo(task: str) -> str:
    """새로운 할 일을 추가합니다.
    
    Args:
        task: 추가할 할 일 내용
    """
    todos = _read_todos()
    todos.append(task)
    _save_todos(todos)
    return f"추가됨: '{task}'"

# ---------------------------------------------------------
# [Task 3] Tool 등록
# 힌트: 상태 변경 함수는 Write가 필요하므로 Resource가 아니라 Tool로 등록해야 함
# ---------------------------------------------------------
@____________________
async def delete_todo(index: int) -> str:
    """번호를 기준으로 할 일을 삭제합니다.
    
    Args:
        index: 삭제할 번호 (1부터 시작)
    """
    todos = _read_todos()
    if 1 <= index <= len(todos):
        removed = todos.pop(index - 1)
        _save_todos(todos)
        return f"삭제됨: '{removed}'"
    
    return f"에러: 잘못된 번호입니다. (입력값: {index})"

# 메인 실행부
if __name__ == "__main__":
    mcp.run()