# MCP servers powered by [ACI.dev](https://aci.dev)

**_For full documentation and tutorials on MCP servers please visit [aci.dev docs](https://aci.dev/docs/mcp-servers/introduction)._**

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
  - [Apps Server](#apps-server)
  - [Unified Server](#unified-server)
- [Understanding the Two Server Types](#understanding-the-two-server-types)
  - [Apps Server](#apps-server-1)
  - [Unified Server](#unified-server-1)
- [Configuration](#configuration)
  - [Usage with Claude Desktop](#usage-with-claude-desktop)
  - [Usage with Cursor](#usage-with-cursor)
- [FAQ](#faq)
- [Debugging](#debugging)


## Overview

**_For full documentation and tutorials on MCP servers please visit [aci.dev docs](https://aci.dev/docs/mcp-servers/introduction)._**

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
uvx aipolabs-mcp apps-server --apps "BRAVE_SEARCH,GMAIL" --linked-account-owner-id <LINKED_ACCOUNT_OWNER_ID>

# Using SSE transport with custom port
uvx aipolabs-mcp apps-server --apps "BRAVE_SEARCH,GMAIL" --linked-account-owner-id <LINKED_ACCOUNT_OWNER_ID> --transport sse --port 8000
```

### Unified Server

The unified server provides two meta functions (tools) to discover and execute **ANY** functions (tools) available on [ACI.dev](https://aci.dev), even if they aren't directly listed in the server.

**The functions (tools) are dynamically searched and executed based on your intent/needs. You don't need to worry about having thousands of tools taking up your LLM's context window or having to integrate multiple MCP servers.**

```bash
# During functions (tools) search/discovery, allow discoverability of all functions (tools) available on ACI.dev
uvx aipolabs-mcp unified-server --linked-account-owner-id <LINKED_ACCOUNT_OWNER_ID>

# During functions (tools) search/discovery, limit to only functions (tools) accessible by the requesting agent (identified by AIPOLABS_ACI_API_KEY)
uvx aipolabs-mcp unified-server --linked-account-owner-id <LINKED_ACCOUNT_OWNER_ID> --allowed-apps-only
```

## Understanding the Two Server Types
**_For full documentation and tutorials on MCP servers please visit [aci.dev docs](https://aci.dev/docs/mcp-servers/introduction)._**

### Apps Server
The apps server provides direct access to specific app functions/tools you specify with the `--apps` parameter. These tools will appear directly in the tool list when MCP clients (e.g. Claude Desktop, Cursor, etc.) interact with this server.

### Unified Server
The unified server doesn't directly expose app-specific tools. Instead, it provides two meta functions (tools):

1. `ACI_SEARCH_FUNCTIONS_WITH_INTENT`: Discovers functions (tools) based on your intent/needs
2. `ACI_EXECUTE_FUNCTION`: Executes **ANY** function (tool) discovered by the search

This approach allows MCP clients to dynamically discover and use **ANY** function available on [ACI.dev](https://platform.aci.dev) platform without needing to list them all upfront. It can search for the right tool based on your needs and then execute it.

## Configuration
**_For full documentation and tutorials on MCP servers please visit [aci.dev docs](https://aci.dev/docs/mcp-servers/introduction)._**

### Usage with Claude Desktop

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "aipolabs-mcp-unified": {
      "command": "uvx",
      "args": ["aipolabs-mcp", "unified-server", "--linked-account-owner-id", "<LINKED_ACCOUNT_OWNER_ID>"]
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
      "args": ["aipolabs-mcp", "apps-server", "--apps", "BRAVE_SEARCH,GMAIL", "--linked-account-owner-id", "<LINKED_ACCOUNT_OWNER_ID>"]
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
        "args": ["aipolabs-mcp", "unified-server", "--linked-account-owner-id", "<LINKED_ACCOUNT_OWNER_ID>"],
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
        "args": ["aipolabs-mcp", "apps-server", "--apps", "BRAVE_SEARCH,GMAIL", "--linked-account-owner-id", "<LINKED_ACCOUNT_OWNER_ID>"],
        "env": {
            "AIPOLABS_ACI_API_KEY": "<AIPOLABS_ACI_API_KEY>"
        }
    }
  }
}
```

## FAQ

- **How do I get the `AIPOLABS_ACI_API_KEY`?**

    The `AIPOLABS_ACI_API_KEY` is the API key for your [ACI.dev](https://platform.aci.dev) project. You can find it in the [ACI.dev](https://platform.aci.dev/project-settings) project settings.

- **How to configure Apps and allow access to them?**

    You can configure apps and allow access to them in the [ACI.dev](https://platform.aci.dev/project-settings) project settings.

- **How do I get the `LINKED_ACCOUNT_OWNER_ID`?**

    The `LINKED_ACCOUNT_OWNER_ID` is the ID of the account that you want to use to access the functions. You can find it in the [ACI.dev](https://platform.aci.dev/project-settings) project settings.

- **What is the benefit of using the unified server over the apps server?**

    Most of the current MCP servers are limited to a specific set of functions (tools), usually from a single app. If you need to use functions from multiple apps, you'll need to integrate multiple MCP servers. But even if you are ok with the managing overhead of integrating multiple MCP servers, your LLM tool calling performance might suffer because all the tools are loaded into the LLM's context window at once.

    The unified server, however, allows you to discover and execute **ANY** function available on [ACI.dev](https://platform.aci.dev) dynamically without worrying about having thousands of tools taking up your LLM's context window or having to integrate multiple MCP servers. 

- **How to specify a list of apps to use with the apps server?**

    You can specify a comma-separated list of apps to use with the apps server using the `--apps` parameter. Try NOT to have spaces between the app names.

- **Can I just use functions (tools) from one app?**

    Yes, you can just use functions (tools) from one app by specifying the (one) app name with the `--apps` parameter.

## Debugging

You can use the MCP inspector to debug the server:

```bash
# For unified server
npx @modelcontextprotocol/inspector uvx aipolabs-mcp unified-server --linked-account-owner-id <LINKED_ACCOUNT_OWNER_ID>

# For apps server
npx @modelcontextprotocol/inspector uvx aipolabs-mcp apps-server --apps "BRAVE_SEARCH,GMAIL" --linked-account-owner-id <LINKED_ACCOUNT_OWNER_ID>
```

Running `tail -n 20 -f ~/Library/Logs/Claude/mcp*.log` will show the logs from the server and may help you debug any issues.
