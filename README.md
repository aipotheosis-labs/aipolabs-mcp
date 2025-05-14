# MCP servers powered by [ACI.dev](https://aci.dev)

> [!IMPORTANT]
> This README only covers basic development guide. For full documentation and tutorials on ACI.dev MCP servers please visit [aci.dev docs](https://aci.dev/docs/mcp-servers/introduction).

## Table of Contents

- [Overview](#overview)
- [Quick Installation](#quick-installation)
- [Run MCP Servers Locally](#run-mcp-servers-locally)
- [Integration with MCP Clients](#integration-with-mcp-clients)
- [Docker](#docker)
- [Debugging](#debugging)

## Overview

This package provides two Model Context Protocol (MCP) servers for accessing [ACI.dev](https://aci.dev) managed functions (tools):

- `aci-mcp-apps`: An MCP server that provides direct access to functions (tools) from specified apps
   <img src="./assets/apps-mcp-server-diagram.svg" alt="Apps Server"/>
- `aci-mcp-unified`: An MCP server that provides two meta functions (tools) (`ACI_SEARCH_FUNCTIONS` and `ACI_EXECUTE_FUNCTION`) to discover and execute **ALL** functions (tools) available on [ACI.dev](https://platform.aci.dev)
   <img src="./assets/unified-mcp-server-diagram.svg" alt="Unified Server">

> [!IMPORTANT]
> For detailed explanation and tutorials on the two MCP servers please visit [aci.dev docs](https://aci.dev/docs/mcp-servers/introduction).

## Quick Installation

We provide an easy installation script that sets up MCP servers for different environments (Cursor, Claude desktop, etc.):

```bash
# Clone the repository
git clone https://github.com/aipotheosis-labs/aci-mcp.git
cd aci-mcp

# Run the installation script
./install.sh
```

The script will:
1. Check for Python 3.10+ installation
2. Install required dependencies
3. Create configuration directory at `~/.aci-mcp/`
4. Set up environment-specific scripts

After installation:
1. Edit `~/.aci-mcp/config` to add your:
   - ACI API key
   - Linked account owner ID
   - Server type preference (unified or apps)
   - Apps list (if using apps server)
2. Run the appropriate setup script:
   - For Cursor: `~/.aci-mcp/setup-cursor.sh`
   - For Claude desktop: `~/.aci-mcp/setup-claude.sh`

## Run MCP Servers Locally

The package is published to PyPI, so you can run it directly using `uvx`:

```bash
# Install uv if you don't have it already
curl -sSf https://install.pypa.io/get-pip.py | python3 -
pip install uv
```

```bash
$ uvx aci-mcp --help
Usage: aci-mcp [OPTIONS] COMMAND [ARGS]...

  Main entry point for the package.

Options:
  --help  Show this message and exit.

Commands:
  apps-server     Start the apps-specific MCP server to access tools...
  unified-server  Start the unified MCP server with unlimited tool access.
```

## Integration with MCP Clients

See the [Unified MCP Server](https://www.aci.dev/docs/mcp-servers/unified-server#integration-with-mcp-clients) and [Apps MCP Server](https://www.aci.dev/docs/mcp-servers/apps-server#integration-with-mcp-clients) sections for more information on how to configure the MCP servers with different MCP clients.


## Docker

```bash
# Build the image
docker build -t aci-mcp .

# Run the unified server
docker run --rm -i -e ACI_API_KEY=<ACI_API_KEY> aci-mcp unified-server --linked-account-owner-id <LINKED_ACCOUNT_OWNER_ID>

# Run the apps server
docker run --rm -i -e ACI_API_KEY=<ACI_API_KEY> aci-mcp apps-server --apps <APP1,APP2,...> --linked-account-owner-id <LINKED_ACCOUNT_OWNER_ID>
```

## Debugging

You can use the MCP inspector to debug the server:

```bash
# For unified server
npx @modelcontextprotocol/inspector uvx aci-mcp unified-server --linked-account-owner-id <LINKED_ACCOUNT_OWNER_ID>

# For apps server
npx @modelcontextprotocol/inspector uvx aci-mcp apps-server --apps "BRAVE_SEARCH,GMAIL" --linked-account-owner-id <LINKED_ACCOUNT_OWNER_ID>
```

Running `tail -n 20 -f ~/Library/Logs/Claude/mcp*.log` will show the logs from the server and may help you debug any issues.
