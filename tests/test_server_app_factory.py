#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI app factory test (unit-ish)
- builds the FastAPI app via FastApp(FastAppSettings)
- asserts /help exists and responds 200
- asserts there is an MCP route ending with '/mcp'
"""

import pytest
from unittest.mock import MagicMock, AsyncMock


def _has_fastapi() -> bool:
    try:
        import fastapi  # noqa: F401
        return True
    except Exception:
        return False


@pytest.mark.skipif(not _has_fastapi(), reason="FastAPI not installed")
def test_fastapp_routes_exist():
    from fastapi.testclient import TestClient
    # import server components
    from server import ServerSettings, FastApp, FastAppSettings

    settings = ServerSettings()
    mock_mcp = MagicMock()
    mock_mcp.name = getattr(settings, "name", "docs-server")
    mock_mcp.instructions = "Test server"
    # minimal async attribute some apps expect
    mock_mcp.session_manager = MagicMock()
    mock_mcp.session_manager.run = AsyncMock()
    # streamable http app factory (FastApp will call this)
    mock_mcp.streamable_http_app.return_value = MagicMock()

    app = FastApp(FastAppSettings(settings, mock_mcp)).create_app()

    client = TestClient(app)
    # /help must exist
    r = client.get("/help")
    assert r.status_code == 200

    # find a mounted MCP route (endswith '/mcp')
    mcp_paths = [getattr(route, "path", "") for route in app.routes if getattr(route, "path", "").endswith("/mcp")]
    assert mcp_paths, "No MCP route ending with /mcp was registered"
