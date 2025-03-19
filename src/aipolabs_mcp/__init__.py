import click
from .server import serve
import asyncio


@click.command()
@click.option(
    "--apps",
    required=True,
    type=str,
    help="comma separated list of apps of which to use the functions",
)
@click.option(
    "--linked-account-owner-id",
    required=True,
    type=str,
    help="the owner id of the linked account to use for the tool calls",
)
@click.option("--port", default=8000, help="Port to listen on for SSE")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport type",
)
def main(apps: str, linked_account_owner_id: str, transport: str, port: int) -> int:
    """Main entry point for the package."""
    apps = [app.strip() for app in apps.split(",")]
    if not apps:
        raise click.UsageError("At least one app is required")
    return asyncio.run(serve(apps, linked_account_owner_id, transport, port))
