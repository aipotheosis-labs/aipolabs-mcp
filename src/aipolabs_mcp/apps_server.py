import json
import logging
import os

import anyio
import mcp.types as types
import uvicorn
from aipolabs import ACI
from aipolabs.types.functions import FunctionDefinitionFormat
from mcp.server.lowlevel import Server
from mcp.server.sse import SseServerTransport
from mcp.server.stdio import stdio_server
from starlette.applications import Starlette
from starlette.routing import Mount, Route

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

aci = ACI()

server = Server("aipolabs-mcp", version="0.1.0")

APPS = []
LINKED_ACCOUNT_OWNER_ID = ""


def _set_up(apps: list[str], linked_account_owner_id: str):
    """
    Set up global variables
    """
    global APPS, LINKED_ACCOUNT_OWNER_ID

    APPS = apps
    LINKED_ACCOUNT_OWNER_ID = linked_account_owner_id


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    """

    logger.error(f"AIPOLABS_ACI_API_KEY: {os.environ.get('AIPOLABS_ACI_API_KEY')}")

    functions = aci.functions.search(
        app_names=APPS,
        allowed_apps_only=False,
        format=FunctionDefinitionFormat.ANTHROPIC,
    )

    return [
        types.Tool(
            name=function["name"],
            description=function["description"],
            inputSchema=function["input_schema"],
        )
        for function in functions
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    """

    execution_result = aci.functions.execute(
        function_name=name,
        function_arguments=arguments,
        linked_account_owner_id=LINKED_ACCOUNT_OWNER_ID,
    )

    if execution_result.success:
        return [
            types.TextContent(
                type="text",
                text=json.dumps(execution_result.data),
            )
        ]
    else:
        return [
            types.TextContent(
                type="text",
                text=f"Failed to execute tool, error: {execution_result.error}",
            )
        ]


def start(apps: list[str], linked_account_owner_id: str, transport: str, port: int) -> None:
    logger.info("Starting MCP server...")

    _set_up(apps=apps, linked_account_owner_id=linked_account_owner_id)
    logger.info(f"APPS: {APPS}")
    logger.info(f"LINKED_ACCOUNT_OWNER_ID: {LINKED_ACCOUNT_OWNER_ID}")

    if transport == "sse":
        anyio.run(run_sse_async, "0.0.0.0", port)
    else:
        anyio.run(run_stdio_async)


async def run_stdio_async():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


async def run_sse_async(host: str, port: int):
    sse = SseServerTransport("/messages/")

    async def handle_sse(request):
        async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
            await server.run(streams[0], streams[1], server.create_initialization_options())

    starlette_app = Starlette(
        debug=True,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )

    config = uvicorn.Config(
        starlette_app,
        host=host,
        port=port,
        log_level="debug",
    )
    uvicorn_server = uvicorn.Server(config)
    await uvicorn_server.serve()
