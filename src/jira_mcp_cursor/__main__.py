"""Entry point for Jira MCP Server."""

import asyncio
from .server import run


if __name__ == "__main__":
    asyncio.run(run())
