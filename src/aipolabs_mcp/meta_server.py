import json
import logging

import anyio
import mcp.types as types
import uvicorn
from aipolabs import ACI
from aipolabs.meta_functions import ACIExecuteFunction, ACISearchFunctionsWithIntent
from aipolabs.types.functions import FunctionDefinitionFormat
from mcp.server.lowlevel import Server
from mcp.server.sse import SseServerTransport
from mcp.server.stdio import stdio_server
from starlette.applications import Starlette
from starlette.routing import Mount, Route

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

aci = ACI()
server = Server("aipolabs-mcp-meta")

ALLOWED_APPS_ONLY = False
LINKED_ACCOUNT_OWNER_ID = ""


def _set_up(allowed_apps_only: bool, linked_account_owner_id: str):
    """
    Set up global variables
    """
    global ALLOWED_APPS_ONLY, LINKED_ACCOUNT_OWNER_ID

    ALLOWED_APPS_ONLY = allowed_apps_only
    LINKED_ACCOUNT_OWNER_ID = linked_account_owner_id


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    """
    # The ACISearchFunctionsWithIntent.SCHEMA and ACIExecuteFunction.SCHEMA are in openai format,
    # so we need to convert them to anthropic format.
    return [
        types.Tool(
            name=ACISearchFunctionsWithIntent.NAME,
            description=ACISearchFunctionsWithIntent.SCHEMA["function"]["description"],
            inputSchema=ACISearchFunctionsWithIntent.SCHEMA["function"]["parameters"],
        ),
        types.Tool(
            name=ACIExecuteFunction.NAME,
            description=ACIExecuteFunction.SCHEMA["function"]["description"],
            inputSchema=ACIExecuteFunction.SCHEMA["function"]["parameters"],
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    """
    if arguments is None:
        arguments = {}

    try:
        result = aci.handle_function_call(
            name,
            arguments,
            linked_account_owner_id=LINKED_ACCOUNT_OWNER_ID,
            allowed_apps_only=ALLOWED_APPS_ONLY,
            format=FunctionDefinitionFormat.ANTHROPIC,
        )
        return [
            types.TextContent(
                type="text",
                text=json.dumps(result),
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Failed to execute tool, error: {e}",
            )
        ]


def start(allowed_apps_only: bool, linked_account_owner_id: str, transport: str, port: int) -> None:
    logger.info("Starting MCP server...")

    _set_up(allowed_apps_only=allowed_apps_only, linked_account_owner_id=linked_account_owner_id)

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
