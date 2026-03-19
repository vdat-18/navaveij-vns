"""Tests for the MCP Client Factory."""

from unittest.mock import AsyncMock, patch

import pytest

from src.services.mcp_client import MCPClientFactory


@pytest.mark.asyncio
async def test_mcp_factory_lifecycle():
    """Verify that MCPClientFactory correctly manages the session lifecycle."""
    mock_stdio_client = AsyncMock()
    mock_session = AsyncMock()

    # Setup mocks for context manager
    mock_stdio_client.__aenter__.return_value = (AsyncMock(), AsyncMock())
    mock_session.__aenter__.return_value = mock_session
    mock_session.initialize = AsyncMock()

    with (
        patch("src.services.mcp_client.stdio_client", return_value=mock_stdio_client),
        patch("src.services.mcp_client.ClientSession", return_value=mock_session),
    ):
        async with MCPClientFactory.get_client() as session:
            assert session == mock_session
            # Verify entered
            mock_stdio_client.__aenter__.assert_called_once()
            mock_session.__aenter__.assert_called_once()

        # Verify exited
        mock_session.__aexit__.assert_called_once()
        mock_stdio_client.__aexit__.assert_called_once()
