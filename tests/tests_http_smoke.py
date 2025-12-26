#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTTP smoke test (integration)
- boots server.py in HTTP mode on an ephemeral port
- waits for /help
- opens an MCP HTTP session and calls health_check
"""

import asyncio
import json
import os
from pathlib import Path
import pytest
import signal
import socket
import subprocess
import sys
import time


@pytest.mark.integration
@pytest.mark.asyncio
async def test_http_smoke_health_check(tmp_path):
    import httpx
    # mcp client pieces
    from mcp.client.streamable_http import streamablehttp_client as mcp_stream
    from mcp import ClientSession

    server_py = _find_server_py()
    docs_dir = _make_tiny_docs(tmp_path)

    host = "127.0.0.1"
    port = _ephemeral_port()
    name = "smoke-server"

    cmd = [
        sys.executable,
        str(server_py),
        "--transport", "http",
        "--host", host,
        "--port", str(port),
        "--docs", str(docs_dir),
        "--name", name,
        "--device", "none",  # keep startup light if supported
    ]

    env = os.environ.copy()
    env.setdefault("PYTHONUNBUFFERED", "1")

    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env
    )
    try:
        # wait for /help
        base = f"http://{host}:{port}"
        assert await _wait_http_up(f"{base}/help"), "HTTP /help never became ready"

        # open MCP HTTP session and call health_check
        mcp_url = f"{base}/{name}/mcp"
        async with mcp_stream(mcp_url) as (read, write, get_session_id):
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
                # be permissive about shape
                try:
                    payload = json.loads(text)
                except Exception:
                    payload = {}
                # if JSON, assert basic shape
                if isinstance(payload, dict) and payload:
                    assert "status" in payload
    finally:
        _terminate(proc)


# ---------------- helpers ----------------

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
    (d / "hello.md").write_text("# Hello\n\nThis is a tiny doc for smoke tests.\n", encoding="utf-8")
    return d

def _ephemeral_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]

async def _wait_http_up(url: str, timeout: float = 60.0) -> bool:
    import httpx
    deadline = time.monotonic() + timeout
    async with httpx.AsyncClient(timeout=5.0) as client:
        while time.monotonic() < deadline:
            try:
                r = await client.get(url)
                if r.status_code == 200:
                    return True
            except Exception:
                pass
            await asyncio.sleep(0.5)
    return False

def _extract_text(content_items) -> str:
    if not content_items:
        return ""
    item = content_items[0]
    if hasattr(item, "text") and item.text:
        return item.text
    if hasattr(item, "data") and item.data:
        return str(item.data)
    return str(item)

def _terminate(proc: subprocess.Popen) -> None:
    if proc.poll() is None:
        try:
            proc.send_signal(signal.SIGINT)
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
        except Exception:
            proc.kill()
