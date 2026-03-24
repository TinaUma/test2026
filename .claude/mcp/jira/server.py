"""Jira MCP Server for frai framework.

Provides tools to manage Jira issues, transitions, worklogs, and comments.
Includes bidirectional sync between frai task DB and Jira.

Usage in .mcp.json:
{
    "jira": {
        "command": "python",
        "args": ["path/to/.claude/mcp/jira/server.py", "--project", "/path/to/project"],
        "env": {
            "JIRA_URL": "https://jira.example.com",
            "JIRA_TOKEN": "<PAT>"
        }
    }
}

Environment:
    JIRA_URL       — Jira base URL
    JIRA_TOKEN     — PAT token (Bearer auth, Jira Server/DC)
    JIRA_USER      — Username for Basic auth (Jira Cloud)
    JIRA_PASSWORD  — API token for Basic auth (Jira Cloud)
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys


def main() -> None:
    parser = argparse.ArgumentParser(description="Jira MCP Server")
    parser.add_argument("--project", required=True, help="Project root directory")
    args = parser.parse_args()

    project_dir = os.path.abspath(args.project)

    # Import MCP
    try:
        from mcp.server import Server
        from mcp.server.stdio import stdio_server
        from mcp.types import TextContent, Tool
    except ImportError:
        print("Error: mcp package not installed. Run: pip install mcp", file=sys.stderr)
        sys.exit(1)

    # Add this directory to path for local imports
    mcp_dir = os.path.dirname(os.path.abspath(__file__))
    if mcp_dir not in sys.path:
        sys.path.insert(0, mcp_dir)

    from tools import TOOLS
    from handlers import handle_tool

    server = Server("jira")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name=t["name"],
                description=t.get("description", ""),
                inputSchema=t.get("inputSchema", {"type": "object", "properties": {}}),
            )
            for t in TOOLS
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        result = handle_tool(project_dir, name, arguments or {})
        return [TextContent(type="text", text=result)]

    async def _run() -> None:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(),
            )

    asyncio.run(_run())


if __name__ == "__main__":
    main()
