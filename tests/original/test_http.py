#!/usr/bin/env python3
"""
MCP HTTP Transport Test
=======================

Comprehensive tests for the MCP documentation server's HTTP transport:

1. HTTP endpoint validation (help page, server mount, MCP endpoint)
2. Complete MCP functionality testing:
   - Session initialization and tool listing
   - health_check tool testing  
   - search_for_documents tool testing
   - search_and_retrieve_documents tool testing
   - Resource reading using document IDs from search results
   - Resource template listing

Based on the working pattern from simple-mcp-server examples.
Fixes task lifecycle issues to prevent "Task was destroyed but it is pending" warnings.
"""

import asyncio
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional, Dict, Any

import httpx

# ────────────────────────────────────────────────────────────────────────────
# Configuration
# ────────────────────────────────────────────────────────────────────────────

HOST = os.getenv("FASTMCP_TEST_HOST", "127.0.0.1")
PORT = int(os.getenv("FASTMCP_TEST_PORT", "8008"))
SERVER_NAME = os.getenv("FASTMCP_SERVER_NAME", "docs-server")

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
SERVER_SCRIPT = REPO_ROOT / "server.py"
DOCS_DIR = REPO_ROOT / "logzilla-docs"
PY_EXE = sys.executable

STARTUP_GRACE = 30  # seconds maximum to wait for the HTTP server to come up
HTTP_TIMEOUT = 5.0  # seconds for individual HTTP requests
CLIENT_TIMEOUT = 30  # seconds for MCP calls
SEARCH_INIT_GRACE = 45  # seconds to wait for search engines to initialize

# ────────────────────────────────────────────────────────────────────────────
# Helper utilities
# ────────────────────────────────────────────────────────────────────────────

def _print_prefixed(prefix: str, line: str) -> None:
    """Print server output with a prefix so it is distinguishable."""
    sys.stdout.write(f"{prefix} | {line}\n")
    sys.stdout.flush()


async def _stream_process_output(proc: subprocess.Popen, prefix: str) -> None:
    """Continuously stream a subprocess' combined stdout/stderr."""
    if proc.stdout is None:
        return
    loop = asyncio.get_running_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, proc.stdout)  # type: ignore[arg-type]
    async for raw in reader:
        _print_prefixed(prefix, raw.decode(errors="replace").rstrip())


async def _wait_for_server_ready(host: str, port: int, timeout: float = STARTUP_GRACE) -> bool:
    """Wait for the HTTP server to be ready by checking the /help endpoint."""
    deadline = time.monotonic() + timeout
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        while time.monotonic() < deadline:
            try:
                # Check if the server's help page is available
                resp = await client.get(f"http://{host}:{port}/help")
                if resp.status_code == 200:
                    print("✓ Server HTTP interface is ready")
                    return True
            except (httpx.RequestError, httpx.HTTPError):
                pass
            await asyncio.sleep(1)
    return False


# ────────────────────────────────────────────────────────────────────────────
# Alternative test using MCP's streamablehttp_client
# ────────────────────────────────────────────────────────────────────────────

async def test_comprehensive_mcp_client(server_url: str) -> bool:
    """Comprehensive test using MCP's streamablehttp_client."""
    try:
        from mcp.client.streamable_http import streamablehttp_client
        from mcp import ClientSession
        import json
        
        print(f"\n🔌 Testing with MCP streamablehttp_client at {server_url}")
        
        # Wait for search engines to be ready first
        await asyncio.sleep(10)  # Give search engines time to initialize
        
        async with streamablehttp_client(server_url) as (
            read_stream,
            write_stream,
            get_session_id,
        ):
            print("🎯 Initializing MCP session...")
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                print("✅ Session initialization complete!")
                
                if get_session_id:
                    session_id = get_session_id()
                    if session_id:
                        print(f"Session ID: {session_id}")
                
                # List tools
                tools = await session.list_tools()
                print("\n🛠️  Available Tools")
                tool_names = []
                for tool in tools.tools:
                    print(f"   • {tool.name}: {tool.description}")
                    tool_names.append(tool.name)
                
                # Test 1: health_check tool
                if "health_check" in tool_names:
                    print("\n❤️‍🩹 Testing health_check tool...")
                    result = await session.call_tool("health_check", {})
                    if result.content:
                        health_data = json.loads(result.content[0].text)
                        print(f"   ✓ Server status: {health_data.get('status', 'unknown')}")
                        print(f"   ✓ Documents loaded: {health_data.get('documents_loaded', 0)}")
                        print(f"   ✓ Search tools available: {health_data.get('search_tools_available', False)}")
                    else:
                        print("   ✗ No health data returned")
                        return False
                
                # Test 2: search_for_documents tool
                document_id = None
                if "search_for_documents" in tool_names:
                    print("\n🔍 Testing search_for_documents tool...")
                    result = await session.call_tool(
                        "search_for_documents",
                        {"query": "http syslogng", "top_k": 3, "include_scores": True}
                    )
                    if result.content:
                        search_data = json.loads(result.content[0].text)
                        if search_data.get("status") == "success":
                            results = search_data.get("results", {}).get("results", [])
                            print(f"   ✓ Found {len(results)} search results")
                            if results:
                                document_id = results[0]["document_id"]  # Store for resource test
                                print(f"   ✓ Top result: {document_id} (score: {results[0]['score']:.2f})")
                            else:
                                print("   ✗ No search results returned")
                                return False
                        else:
                            print(f"   ✗ Search failed: {search_data}")
                            return False
                    else:
                        print("   ✗ No search data returned")
                        return False
                
                # Test 3: search_and_retrieve_documents tool
                if "search_and_retrieve_documents" in tool_names:
                    print("\n📄 Testing search_and_retrieve_documents tool...")
                    result = await session.call_tool(
                        "search_and_retrieve_documents",
                        {"query": "http syslogng", "top_k": 2}
                    )
                    if result.content:
                        retrieve_data = json.loads(result.content[0].text)
                        if retrieve_data.get("status") == "success":
                            # The tool returns results with embedded content
                            documents = retrieve_data.get("results", {}).get("results", [])
                            print(f"   ✓ Retrieved {len(documents)} documents with content")
                            if documents:
                                doc = documents[0]
                                if 'content' in doc and doc['content']:
                                    print(f"   ✓ First document: {doc.get('document_id', 'unknown')} ({len(doc['content'])} chars)")
                                else:
                                    print("   ✗ First document is missing content")
                                    return False
                            else:
                                print("   ✗ No documents retrieved")
                                return False
                        else:
                            print(f"   ✗ Search and retrieve failed: {retrieve_data}")
                            return False
                    else:
                        print("   ✗ No retrieve data returned")
                        return False
                
                # Test 4: Resource reading using document ID from search
                if document_id:
                    print(f"\n📖 Testing resource reading for document: {document_id}")
                    try:
                        resource_uri = f"docs://document/{document_id}"
                        result = await session.read_resource(resource_uri)
                        if result.contents:
                            content = result.contents[0]
                            if hasattr(content, 'text') and content.text:
                                print(f"   ✓ Retrieved document content ({len(content.text)} chars)")
                                print(f"   ✓ Content preview: {content.text[:100]}...")
                            else:
                                print("   ✗ Resource content is empty")
                                return False
                        else:
                            print("   ✗ No resource content returned")
                            return False
                    except Exception as e:
                        print(f"   ✗ Resource reading failed: {e}")
                        return False
                else:
                    print("\n📖 Skipping resource test (no document ID from search)")
                
                # Test 5: List resources
                print("\n📚 Testing resource listing...")
                try:
                    resources = await session.list_resources()
                    if resources.resources:
                        print(f"   ✓ Found {len(resources.resources)} resource templates")
                        for resource in resources.resources[:3]:  # Show first 3
                            print(f"   • {resource.name}: {resource.description}")
                    else:
                        print("   ℹ No resource templates available")
                except Exception as e:
                    print(f"   ✗ Resource listing failed: {e}")
                    return False
                
                print("\n✅ All MCP tests completed successfully!")
                return True
                
    except Exception as e:
        print(f"❌ MCP client test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


# ────────────────────────────────────────────────────────────────────────────
# Test runner class
# ────────────────────────────────────────────────────────────────────────────

class FastMCPHTTPTest:
    """End-to-end tester for the HTTP transport."""

    def __init__(self, host: str, port: int, server_name: str) -> None:
        self.host = host
        self.port = port
        self.server_name = server_name
        # The actual MCP endpoint URL based on the sample pattern
        self.mcp_url = f"http://{host}:{port}/{server_name}/mcp"
        self.base_url = f"http://{host}:{port}"
        self.server_proc: Optional[subprocess.Popen] = None
        self.stream_task: Optional[asyncio.Task] = None

    # ──────────────────────────────────────────────── lifecycle ────

    async def start_server(self) -> None:
        """Spawn the documentation server in HTTP mode."""
        cmd = [
            PY_EXE,
            str(SERVER_SCRIPT),
            "--transport",
            "http",
            "--host",
            self.host,
            "--port",
            str(self.port),
            "--docs",
            str(DOCS_DIR),
            "--name",
            self.server_name,
            "--device",
            "none",  # disable vector engine for faster start-up
        ]
        env = os.environ.copy()
        # Ensure PYTHONUNBUFFERED so we see output right away.
        env["PYTHONUNBUFFERED"] = "1"

        print(f"🚀 Launching server: {' '.join(cmd)}")
        self.server_proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=env,
        )
        assert self.server_proc.stdout is not None  # for mypy
        self.stream_task = asyncio.create_task(_stream_process_output(self.server_proc, "SERVER"))

        # Wait for HTTP server to be ready
        ready = await _wait_for_server_ready(self.host, self.port)
        if not ready:
            raise RuntimeError("Server did not start HTTP interface in time")
        
        print(f"✓ Server started")
        print(f"  Base URL: {self.base_url}")
        print(f"  MCP URL: {self.mcp_url}")

    async def stop_server(self) -> None:
        if self.server_proc and self.server_proc.poll() is None:
            print("🛑 Terminating server process …")
            self.server_proc.send_signal(signal.SIGINT)
            try:
                await asyncio.wait_for(asyncio.to_thread(self.server_proc.wait), timeout=10)
            except asyncio.TimeoutError:
                self.server_proc.kill()
        
        # Cancel the streaming task to avoid "Task was destroyed but it is pending" warnings
        if self.stream_task and not self.stream_task.done():
            self.stream_task.cancel()
            try:
                await self.stream_task
            except asyncio.CancelledError:
                pass  # Expected when cancelling
        
        print("✓ Server stopped.")

    # ───────────────────────────────────────────────── tests ────

    async def test_mcp_streamable_client(self) -> bool:
        """Test using MCP's streamablehttp_client with comprehensive tool and resource testing."""
        return await test_comprehensive_mcp_client(self.mcp_url)

    async def test_http_endpoints(self) -> bool:
        """Test that the expected HTTP endpoints exist."""
        print("\n🌐 Testing HTTP endpoints …")
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            endpoints = [
                ("/help", "Help page", 200),
                (f"/{self.server_name}", "Server mount point", [307, 200]),  # Redirect or OK
            ]
            
            all_ok = True
            for endpoint, description, expected_codes in endpoints:
                try:
                    resp = await client.get(f"{self.base_url}{endpoint}")
                    expected_list = expected_codes if isinstance(expected_codes, list) else [expected_codes]
                    print(f"  • {description} ({endpoint}): {resp.status_code}")
                    if resp.status_code not in expected_list:
                        all_ok = False
                except Exception as e:
                    print(f"  • {description} ({endpoint}): Error - {e}")
                    all_ok = False
                    
        return all_ok

    async def run(self) -> bool:
        try:
            await self.start_server()
            
            # Give server a moment to fully initialize
            await asyncio.sleep(2)
            
            tests = [
                ("http-endpoints", self.test_http_endpoints),
                ("mcp-streamable", self.test_mcp_streamable_client),
            ]
            
            results = []
            for name, fn in tests:
                try:
                    passed = await fn()
                except Exception as exc:
                    print(f"💥 {name} raised: {exc}")
                    import traceback
                    traceback.print_exc()
                    passed = False
                results.append((name, passed))
            
            # Summary
            passed_count = sum(p for _, p in results)
            print("\n📊 SUMMARY")
            for name, p in results:
                print(f"  {'✓' if p else '✗'} {name}")
            print(f"━ {passed_count}/{len(results)} tests passed.")
            
            return passed_count == len(tests)  # Pass if all tests succeed
            
        finally:
            await self.stop_server()


# ────────────────────────────────────────────────────────────────────────────
# Entrypoint
# ────────────────────────────────────────────────────────────────────────────

async def _main() -> int:
    tester = FastMCPHTTPTest(HOST, PORT, SERVER_NAME)
    try:
        all_ok = await tester.run()
        return 0 if all_ok else 1
    except Exception as exc:
        print(f"🛑 Test runner failed: {exc}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(_main()))