import asyncio
import sys
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

    async def connect_to_server(self, server_script_path: str):
        """서버 프로세스 실행 및 연결"""
        print(f"🔄 서버 실행 중: {server_script_path}...")
        
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        command = sys.executable if is_python else "node"
        
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        # ---------------------------------------------------------
        # [Task 4] Initialize
        # 힌트: 서버와 기능을 확인하는 메서드
        # ---------------------------------------------------------
        await self.session.initialize()

        
        # Server Connection Check
        tools = await self.session.list_tools()
        print(f"✅ 서버 연결 성공! 감지된 도구: {[t.name for t in tools.tools]}")

    async def run_interactive_loop(self):
        """LLM 대신 사용자 입력을 받아 도구를 직접 호출하는 루프"""
        while True:
            print("\n" + "="*40)
            print("   [MCP Tutorial - TODO]")
            print("="*40)

            # Show Current TODO-List
            try:
                # ---------------------------------------------------------
                # [Task 5] Resource Read
                # 힌트: 리소스 읽기로 "todo://list" 읽기
                # ---------------------------------------------------------
                resource = await self.session.read_resource("todo://list")
                print("\n[현재 할 일 목록]")
                print(resource.contents[0].text)
            except Exception as e:
                print(f"⚠️ 목록 로드 실패: {e}")

            print("-" * 40)
            print("1. 할 일 추가 (add_todo)")
            print("2. 할 일 삭제 (delete_todo)")
            print("q. 종료")

            # Choose Function
            choice = input("선택 > ").strip().lower()
            try:
                if choice == '1':
                    task = input("추가할 내용: ").strip()
                    if task:
                        # Tool Call
                        print("⏳ 서버 요청 중...")
                        # ---------------------------------------------------------
                        # [Task 6] Tool Call
                        # 힌트: "add_todo" 호출 / 인자: arguments={"task": task}
                        # ---------------------------------------------------------
                        result = await self.session.call_tool("add_todo", {"task": task})
                        print(f"✅ 결과: {result.content[0].text}")

                elif choice == '2':
                    idx = input("삭제할 번호: ").strip()
                    if idx.isdigit():
                        # Tool Call
                        print("⏳ 서버 요청 중...")
                        # ---------------------------------------------------------
                        # [Task 6] Tool Call
                        # 힌트: "delete_todo" 호출 / 인자: arguments={"index": int(idx)}
                        # ---------------------------------------------------------
                        result = await self.session.call_tool("delete_todo", {"index": int(idx)})
                        print(f"🗑️ 결과: {result.content[0].text}")
                    else:
                        print("❌ 숫자를 입력해주세요.")

                elif choice in ['q', 'quit', 'exit', 'stop']:
                    print("👋 프로그램을 종료합니다.")
                    break
                
                else:
                    print("❌ 잘못된 입력입니다.")

            except Exception as e:
                print(f"❌ 도구 실행 중 오류 발생: {e}")

    async def cleanup(self):
        await self.exit_stack.aclose()

async def main():
    if len(sys.argv) < 2:
        print("사용법: python client.py server.py")
        sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.run_interactive_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())