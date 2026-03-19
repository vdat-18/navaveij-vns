import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from loguru import logger
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from shared.settings import settings


class MCPClientFactory:
    """Manages MCP Client sessions lifecycle."""

    @staticmethod
    @asynccontextmanager
    async def get_client() -> AsyncGenerator[ClientSession, None]:
        """Provides stdio_client session."""
        params = StdioServerParameters(
            command=settings.mcp_server_command,
            args=settings.mcp_server_args,
            env={**os.environ, "PYTHONPATH": f"{os.getcwd()}:{os.path.join(os.getcwd(), 'backend')}"},
        )
        logger.debug("Starting MCP stdio client")
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                yield session
