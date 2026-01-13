import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from openai import OpenAI
from dotenv import load_dotenv

from openai.types.chat import (
    ChatCompletionUserMessageParam,
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionMessageToolCallParam,
    ChatCompletionToolMessageParam,
    ChatCompletionToolParam,
)

from openai.types.chat.chat_completion_message_tool_call_param import Function
from openai.types.shared_params.function_definition import FunctionDefinition

import json
import argparse

import traceback


load_dotenv()

async def main(server_script_path: str):
    client = MCPClient()

    try:
        await client.connect_to_server(server_script_path)
        await client.workflow_loop("Run pytest on the test files in the targets directory.")
    finally:
        await client.cleanup()


class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.llm = OpenAI()
        self.messages = []

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        server_params = StdioServerParameters(
            command="python",
            args=[server_script_path],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])


    async def cleanup(self):
        await self.exit_stack.aclose()

    async def process_messages(self, messages: list[ChatCompletionMessageParam]):
        """Process a query and return the response"""

        response = await self.session.list_tools()
        available_tools = [ChatCompletionToolParam(
            type="function",
            function=FunctionDefinition(
                name=tool.name,
                description=tool.description if tool.description else "",
                parameters=tool.inputSchema
            )
        ) for tool in response.tools]

        response = self.llm.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=available_tools,
            tool_choice="auto"
        )

        finish_reason = response.choices[0].finish_reason

        if finish_reason == "stop": 
            messages.append(
                ChatCompletionAssistantMessageParam(
                    role="assistant",
                    content=response.choices[0].message.content
                )
            )

        elif finish_reason == "tool_calls":
            tool_calls = response.choices[0].message.tool_calls
            assert tool_calls is not None
            for tool_call in tool_calls:
                print(f"Calling tool: {tool_call.function.name}")
            messages.append(
                ChatCompletionAssistantMessageParam(
                    role="assistant",
                    tool_calls=[
                        ChatCompletionMessageToolCallParam(
                            id=tool_call.id,
                            function=Function(
                                arguments=tool_call.function.arguments,
                                name=tool_call.function.name
                            ),
                            type=tool_call.type,
                        )
                        for tool_call in tool_calls
                    ]
                )
            )
            tasks = [
                asyncio.create_task(self.process_tool_call(tool_call))
                for tool_call in tool_calls
            ]
            messages.extend(await asyncio.gather(*tasks))
            return await self.process_messages(messages)
            
        elif finish_reason == "length":
            raise ValueError(f"[ERROR] Length limit reached ({response.usage.total_tokens} tokens). Please try a shorter query.")

        elif finish_reason == "content_filter":
            raise ValueError("[ERROR] Content filter triggered. Please try a different query.")

        elif finish_reason == "function_call":
            raise ValueError("[ERROR] Deprecated API usage. LLM should use tool_calls instead.")

        else:
            raise ValueError(f"[ERROR] Unknown finish reason: {finish_reason}")

        return messages


    async def process_tool_call(self, tool_call) -> ChatCompletionToolMessageParam:
        assert tool_call.type == "function"

        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)
        print(f"Calling tool: {tool_name} with args: {tool_args}")
        call_tool_result = await self.session.call_tool(tool_name, tool_args)
        if call_tool_result.isError:
            raise ValueError(f"[ERROR] Tool call failed: {call_tool_result.content}")

        results = []
        for result in call_tool_result.content:
            if result.type == "text":
                results.append(result.text)
            else:   # image, resource, etc.
                raise NotImplementedError(f"Unsupported result type: {result.type}")
        
        return ChatCompletionToolMessageParam(
            role="tool",
            content=json.dumps({
                **tool_args,
                tool_name: results
            }),
            tool_call_id=tool_call.id
        )

    async def workflow_loop(self, user_input: str):
        print("Welcome to the MCP Client!")

        self.messages = []

        user_input = user_input

        self.messages.append({"role":"user", "content":user_input})

        try:
            self.messages = await self.process_messages(self.messages)

        except Exception as e:
            print(f"Error processing user input: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MCP Client for connecting to a server.")
    parser.add_argument('server_script_path', help="Path to the server script (.py or .js)", type=str)
    args = parser.parse_args()

    asyncio.run(main(args.server_script_path))

    pass

    