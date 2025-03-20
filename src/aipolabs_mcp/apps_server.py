import json
import logging

import anyio
import mcp.types as types
from aipolabs import ACI
from aipolabs.types.functions import FunctionDefinitionFormat
from mcp.server.lowlevel import Server

from .common import runners

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

aci = ACI()
server = Server("aipolabs-mcp-apps")

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

    if transport == "sse":
        anyio.run(runners.run_sse_async, server, "0.0.0.0", port)
    else:
        anyio.run(runners.run_stdio_async, server)
