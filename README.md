# aipolabs-mcp: MCP servers powered by [ACI.dev](https://aci.dev)

## Overview

This package provides two Model Context Protocol (MCP) servers for accessing [ACI.dev](https://aci.dev) managed functions (tools):

- `aipolabs-mcp-apps`: An MCP server that provides direct access to functions (tools) from specified apps
- `aipolabs-mcp-unified`: An MCP server that provides two meta functions (tools) (`ACI_SEARCH_FUNCTIONS_WITH_INTENT` and `ACI_EXECUTE_FUNCTION`) to discover and execute **ALL** functions (tools) available on [ACI.dev](https://platform.aci.dev)

## Prerequisites

Before using this package, you need to (for more information please see [tutorial](https://aci.dev/docs)):

1. Set the `AIPOLABS_ACI_API_KEY` environment variable with your [ACI.dev](https://platform.aci.dev) API key
2. Configure apps and set them in `allowed_apps` for your agent on [platform.aci.dev](https://platform.aci.dev/project-settings).
3. Link your app specific accounts under the same `--linked-account-owner-id` you'll later provide to start the MCP servers

## Installation

The package is published to PyPI, so you can run it directly using `uvx`:

```bash
# Install uv if you don't have it already
curl -sSf https://install.pypa.io/get-pip.py | python3 -
pip install uv
```

## Usage

### Apps Server

The apps server provides direct access to functions (tools) under specific apps.
You can specify one or more apps to use with the `--apps` parameter. (For a list of available apps, please visit [ACI.dev](https://platform.aci.dev/apps))

```bash
# Using stdio transport (default)
uvx aipolabs-mcp apps_server --apps "BRAVE_SEARCH, GMAIL" --linked-account-owner-id <LINKED_ACCOUNT_OWNER_ID>

# Using SSE transport with custom port
uvx aipolabs-mcp apps_server --apps "BRAVE_SEARCH, GMAIL" --linked-account-owner-id <LINKED_ACCOUNT_OWNER_ID> --transport sse --port 8000
```

### Unified Server

The unified server provides two meta functions (tools) to discover and execute **ANY** functions (tools) available on [ACI.dev](https://aci.dev), even if they aren't directly listed in the server.

**The functions (tools) are dynamically searched and executed based on your intent/needs. You don't need to worry about having thousands of tools taking up your LLM's context window or having to integrate multiple MCP servers.**

```bash
# During functions (tools) search/discovery, allow discoverability of all functions (tools) available on ACI.dev
uvx aipolabs-mcp unified_server --linked-account-owner-id <LINKED_ACCOUNT_OWNER_ID>

# During functions (tools) search/discovery, limit to only functions (tools) accessible by the requesting agent (identified by AIPOLABS_ACI_API_KEY)
uvx aipolabs-mcp unified_server --linked-account-owner-id <LINKED_ACCOUNT_OWNER_ID> --allowed-apps-only
```

## Understanding the Two Server Types

### Apps Server
The apps server provides direct access to specific app functions/tools you specify with the `--apps` parameter. These tools will appear directly in the tool list when MCP clients (e.g. Claude Desktop, Cursor, etc.) interact with this server.

### Unified Server
The unified server doesn't directly expose app-specific tools. Instead, it provides two meta functions (tools):

1. `ACI_SEARCH_FUNCTIONS_WITH_INTENT`: Discovers functions (tools) based on your intent/needs
2. `ACI_EXECUTE_FUNCTION`: Executes **ANY** function (tool) discovered by the search

This approach allows MCP clients to dynamically discover and use **ANY** function available on [ACI.dev](https://platform.aci.dev) platform without needing to list them all upfront. It can search for the right tool based on your needs and then execute it.

## Configuration

### Usage with Claude Desktop

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "aipolabs-mcp-unified": {
      "command": "uvx",
      "args": ["aipolabs-mcp", "unified_server", "--linked-account-owner-id", "<LINKED_ACCOUNT_OWNER_ID>"]
    }
  }
}
```

For apps-specific access:

```json
{
  "mcpServers": {
    "aipolabs-mcp-apps": {
      "command": "uvx",
      "args": ["aipolabs-mcp", "apps_server", "--apps", "BRAVE_SEARCH,GMAIL", "--linked-account-owner-id", "<LINKED_ACCOUNT_OWNER_ID>"]
    }
  }
}
```

### Usage with Cursor

Add to your Cursor `mcp.json`:

```json
{
    "mcpServers": {
      "aipolabs-mcp-unified": {
        "command": "uvx",
        "args": ["aipolabs-mcp", "unified_server", "--linked-account-owner-id", "<LINKED_ACCOUNT_OWNER_ID>"],
        "env": {
            "AIPOLABS_ACI_API_KEY": "<AIPOLABS_ACI_API_KEY>"
        }
      }
    }
  }
```

For apps-specific access:

```json
{
  "mcpServers": {
    "aipolabs-mcp-apps": {
        "command": "uvx",
        "args": ["aipolabs-mcp", "apps_server", "--apps", "BRAVE_SEARCH, GMAIL", "--linked-account-owner-id", "<LINKED_ACCOUNT_OWNER_ID>"],
        "env": {
            "AIPOLABS_ACI_API_KEY": "<AIPOLABS_ACI_API_KEY>"
        }
    }
  }
}
```

## Debugging

You can use the MCP inspector to debug the server:

```bash
# For unified server
npx @modelcontextprotocol/inspector uvx aipolabs-mcp unified_server --linked-account-owner-id <LINKED_ACCOUNT_OWNER_ID>

# For apps server
npx @modelcontextprotocol/inspector uvx aipolabs-mcp apps_server --apps "BRAVE_SEARCH, GMAIL" --linked-account-owner-id <LINKED_ACCOUNT_OWNER_ID>
```

Running `tail -n 20 -f ~/Library/Logs/Claude/mcp*.log` will show the logs from the server and may help you debug any issues.