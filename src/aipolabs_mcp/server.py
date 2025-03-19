import anyio
import json
import os
import mcp.types as types
from mcp.server.lowlevel import Server
from aipolabs import ACI
from aipolabs.types.functions import FunctionDefinitionFormat
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from mcp.server.stdio import stdio_server
import uvicorn
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

aci = ACI()

server = Server(
    "aipolabs-mcp",
    version="0.1.0"
)

APPS = []
LINKED_ACCOUNT_OWNER_ID = ""

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
        linked_account_owner_id=LINKED_ACCOUNT_OWNER_ID
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


def _set_up(apps: list[str], linked_account_owner_id: str):
    """
    Set up global variables
    """
    global APPS, LINKED_ACCOUNT_OWNER_ID

    APPS = apps
    LINKED_ACCOUNT_OWNER_ID = linked_account_owner_id



def serve(apps: list[str], linked_account_owner_id: str, transport: str, port: int) -> int:
    logger.info("Starting MCP server...")
    
    _set_up(apps=apps, linked_account_owner_id=linked_account_owner_id)
    logger.info(f"APPS: {APPS}")
    logger.info(f"LINKED_ACCOUNT_OWNER_ID: {LINKED_ACCOUNT_OWNER_ID}")

    if transport == "sse":
        sse = SseServerTransport("/messages/")
        async def handle_sse(request):
            async with sse.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await server.run(
                    streams[0], streams[1], server.create_initialization_options()
                )

        starlette_app = Starlette(
            debug=True,
            routes=[
                Route("/sse", endpoint=handle_sse),
                Mount("/messages/", app=sse.handle_post_message),
            ],
        )

        uvicorn.run(starlette_app, host="0.0.0.0", port=port)
    else:
        async def arun():
            async with stdio_server() as streams:
                await server.run(
                    streams[0], streams[1], server.create_initialization_options()
                )

        anyio.run(arun)

    return 0
