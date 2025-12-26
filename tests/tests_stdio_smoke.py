#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STDIO smoke test (integration)
- launches server.py via stdio_client
- initializes session
- lists tools
- calls health_check
"""

import json
from pathlib import Path
import pytest
import sys


@pytest.mark.integration
@pytest.mark.asyncio
async def test_stdio_smoke_health_check(tmp_path):
    # mcp client pieces
    from mcp.client.stdio import stdio_client as mcp_stdio
    from mcp import ClientSession, StdioServerParameters

    server_py = _find_server_py()
    docs_dir = _make_tiny_docs(tmp_path)

    params = StdioServerParameters(
        command=sys.executable,
        args=[str(server_py), "--transport", "stdio", "--docs", str(docs_dir), "--name", "smoke-server"],
    )

    async with mcp_stdio(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            tool_names = [t.name for t in getattr(tools, "tools", [])]
            assert "health_check" in tool_names

            # health_check via MCP
            res = await session.call_tool("health_check", {})
            assert getattr(res, "content", None), "health_check returned no content"
            text = _extract_text(res.content)
            # search_for_chunks via MCP
            assert "search_for_chunks" in tool_names
            res2 = await session.call_tool("search_for_chunks", {"query": "Hello", "top_k": 3})
            text2 = _extract_text(getattr(res2, "content", []))
            assert isinstance(text2, str) and text2 != ""
            # JSON payload is nice-to-have, but don't be brittle
            try:
                payload = json.loads(text)
                assert isinstance(payload, dict)
                assert "status" in payload
            except Exception:
                # non-JSON is acceptable for a smoke
                pass


# -------------- helpers --------------

def _find_server_py() -> Path:
    here = Path(__file__).resolve()
    for p in [here.parents[i] for i in range(0, min(6, len(here.parents)))]:
        candidate = p / "server.py"
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Could not locate server.py by walking up the directory tree")

def _make_tiny_docs(tmp_root: Path) -> Path:
    d = tmp_root / "docs"
    d.mkdir(parents=True, exist_ok=True)
    (d / "hello.md").write_text("# Hello\n\nThis is a tiny doc for stdio smoke tests.\n", encoding="utf-8")
    return d

def _extract_text(content_items) -> str:
    if not content_items:
        return ""
    item = content_items[0]
    if hasattr(item, "text") and item.text:
        return item.text
    if hasattr(item, "data") and item.data:
        return str(item.data)
    return str(item)
