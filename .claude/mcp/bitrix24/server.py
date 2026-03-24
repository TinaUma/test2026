"""Bitrix24 Scrum MCP Server for frai framework.

Provides tools to manage Scrum epics, tasks, sprints, and backlog in Bitrix24.
Includes bidirectional sync between frai task DB and Bitrix24 Scrum board.

Usage in .mcp.json:
{
    "bitrix24": {
        "command": "python",
        "args": ["path/to/.claude/mcp/bitrix24/server.py", "--project", "/path/to/project"]
    }
}

Environment:
    BITRIX24_WEBHOOK_URL      — Bitrix24 webhook URL
    BITRIX24_SCRUM_GROUP_ID   — Scrum group ID (default: 297)
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys


def main() -> None:
    parser = argparse.ArgumentParser(description="Bitrix24 Scrum MCP Server")
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

    server = Server("bitrix24")

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
