"""MCP Infrastructure Factory for Navaveij."""

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from loguru import logger
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from shared.settings import settings


class MCPClientFactory:
    """Factory for managing MCP Client sessions with automatic lifecycle management."""

    @staticmethod
    @asynccontextmanager
    async def get_client() -> AsyncGenerator[ClientSession, None]:
        """Yield a context-managed MCP session.

        Currently implements stdio transport based on environment configuration.
        """
        server_params = StdioServerParameters(
            command=settings.mcp_server_command,
            args=settings.mcp_server_args,
            env={**os.environ, "PYTHONPATH": f"{os.getcwd()}:{os.path.join(os.getcwd(), 'backend')}"},
        )

        logger.debug("Starting MCP stdio client session")
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                logger.debug("Initializing MCP session")
                await session.initialize()
                yield session
