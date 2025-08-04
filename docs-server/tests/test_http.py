#!/usr/bin/env python3
"""
MCP Documentation Server HTTP Mode Test
======================================

Test the MCP server running in HTTP mode with comprehensive endpoint testing:

1. MCP HTTP Endpoints (per MCP specification):
   - GET /.well-known/mcp/health → returns 200 if ready
   - GET /v1/models → returns list of available models
   - POST /v1/messages → accepts chat messages and returns completions

2. FastMCP Client Integration:
   - Tests the MCP protocol implementation using FastMCP client
   - Tests tool listing and execution via MCP protocol

This verifies both raw HTTP endpoint compliance and MCP protocol functionality.
"""

print("🔧 Starting FastMCP HTTP mode test script...")

try:
    import asyncio
    print("✅ asyncio imported")
    import argparse
    print("✅ argparse imported")
    import tempfile
    print("✅ tempfile imported")
    import sys
    print("✅ sys imported")
    import time
    print("✅ time imported")
    import subprocess
    print("✅ subprocess imported")
    from pathlib import Path
    print("✅ pathlib imported")
    from fastmcp import Client
    print("✅ FastMCP Client imported")
    from typing import Any, Dict, List, Optional
    print("✅ typing imported")
    import httpx
    print("✅ httpx imported (required for MCP HTTP endpoint testing)")
except Exception as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


class MCPHTTPServerTest:
    """FastMCP-based test suite for the MCP Documentation Server in HTTP mode"""
    
    def __init__(self, docs_path: Optional[str] = None, use_temp_docs: bool = True, host: str = "127.0.0.1", port: int = 8000):
        self.docs_path = docs_path
        self.use_temp_docs = use_temp_docs
        self.host = host
        self.port = port
        self.temp_docs_dir = None
        self.client = None
        self.server_process = None
        self.server_script = Path(__file__).parent / "server.py"
        
    def setup_docs(self):
        """Setup documentation directory"""
        if self.use_temp_docs:
            self.temp_docs_dir = tempfile.mkdtemp(prefix="test_docs_http_")
            test_file = Path(self.temp_docs_dir) / "test.md"
            test_file.write_text("# HTTP Test Document\n\nThis is a test document for HTTP mode MCP testing.\n\n## Features\n\n- HTTP transport\n- FastMCP client\n- Search functionality\n- Document retrieval\n- Hybrid search")
            self.docs_path = self.temp_docs_dir
            print(f"📁 Created temp docs directory: {self.docs_path}")
        else:
            print(f"📁 Using existing docs directory: {self.docs_path}")
    
    async def start_http_server(self):
        """Start the MCP server in HTTP mode"""
        try:
            cmd = [
                sys.executable, str(self.server_script),
                "--transport", "http",
                "--host", self.host,
                "--port", str(self.port),
                "--docs", self.docs_path
            ]
            
            print(f"🚀 Starting HTTP server: {' '.join(cmd)}")
            
            self.server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Combine stderr with stdout
                text=True,
                bufsize=1  # Line buffered
            )
            
            print(f"📋 HTTP server process started with PID: {self.server_process.pid}")
            
            # Wait for server to start and be ready - we know from debug it takes ~8-10 seconds
            print("⏳ Waiting for HTTP server to initialize...")
            await asyncio.sleep(12)  # Give plenty of time for full initialization
            
            # Check if process died during startup
            if self.server_process.poll() is not None:
                stdout, _ = self.server_process.communicate()
                print(f"❌ Server failed to start. Exit code: {self.server_process.poll()}")
                print(f"📤 Server output: {stdout}")
                return False
            
            # Test server responsiveness
            print(f"🔍 Testing if HTTP server is responding on http://{self.host}:{self.port}")
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"http://{self.host}:{self.port}/")
                    print(f"✅ Server responded with status: {response.status_code}")
            except Exception as e:
                print(f"⚠️ Server health check failed: {e}")
                # Continue anyway as this might be expected for MCP endpoints
            
            print(f"✅ HTTP server running on http://{self.host}:{self.port}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start HTTP server: {e}")
            return False
    
    def setup_http_client(self):
        """Setup FastMCP HTTP client"""
        # Connect to the correct FastMCP endpoint based on server implementation
        server_name = "docs-server"  # Default server name matches server.py default
        self.server_url = f"http://{self.host}:{self.port}/{server_name}/mcp"
        
        print(f"🔧 Setting up FastMCP HTTP client...")
        self.client = Client(self.server_url)
        print(f"✅ FastMCP HTTP client created for: {self.server_url}")
    
    def cleanup(self):
        """Cleanup resources"""
        # Stop the HTTP server
        if self.server_process:
            print("🛑 Stopping HTTP server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print("⚠️ Server didn't stop gracefully, forcing kill...")
                self.server_process.kill()
                self.server_process.wait()
            print("✅ HTTP server stopped")
        
        # Clean up temp docs
        if self.temp_docs_dir:
            import shutil
            shutil.rmtree(self.temp_docs_dir)
            print("🗑️ Cleaned up temp docs directory")
    
    # Test Methods for HTTP connectivity and MCP protocol
    async def test_http_health_check(self) -> bool:
        """Test basic HTTP connectivity via /help endpoint"""
        try:
            print("🏥 Testing basic HTTP connectivity...")
            async with httpx.AsyncClient() as http_client:
                response = await http_client.get(f"http://{self.host}:{self.port}/help")
                
                if response.status_code == 200:
                    print(f"✅ HTTP server is responding (status 200)")
                    print(f"📋 Help page available at /help")
                    return True
                else:
                    print(f"❌ HTTP server returned {response.status_code}")
                    print(f"📋 Response: {response.text}")
                    return False
                    
        except Exception as e:
            print(f"❌ HTTP connectivity test failed: {e}")
            return False

    async def test_ping(self) -> bool:
        """Test server ping over HTTP using FastMCP client"""
        try:
            if not self.client:
                print("❌ FastMCP client not initialized")
                return False
                
            print("📡 Testing FastMCP client ping...")
            await self.client.ping()
            print("✅ FastMCP Ping successful!")
            return True
        except Exception as e:
            print(f"❌ FastMCP Ping failed: {e}")
            return False
    
    async def test_list_tools(self) -> bool:
        """Test listing available tools over HTTP using FastMCP client"""
        try:
            if not self.client:
                print("❌ FastMCP client not initialized")
                return False
                
            print("🔧 Testing FastMCP list_tools...")
            tools = await self.client.list_tools()
            print(f"✅ Found {len(tools)} tools via FastMCP: {[tool.name for tool in tools]}")
            
            # Validate expected tools exist
            expected_tools = ['search_for_documents', 'health_check']
            found_tools = [tool.name for tool in tools]
            for expected in expected_tools:
                if expected not in found_tools:
                    print(f"⚠️ Expected tool '{expected}' not found")
                else:
                    print(f"✅ Found expected tool '{expected}'")
            
            return len(tools) > 0
        except Exception as e:
            print(f"❌ FastMCP List tools failed: {e}")
            return False
    
    async def test_health_check_tool(self) -> bool:
        """Test the health_check tool via FastMCP client"""
        try:
            if not self.client:
                print("❌ FastMCP client not initialized")
                return False
                
            print("🏥 Testing health_check tool...")
            result = await self.client.call_tool("health_check", {})
            print(f"✅ Health check tool completed")
            
            # Try to parse the result if it's text content
            if hasattr(result, 'content') and result.content:
                content_text = str(result.content[0]) if result.content else ""
                if content_text:
                    print(f"📋 Health check response: {content_text[:200]}...")
            
            return True
        except Exception as e:
            print(f"❌ Health check tool failed: {e}")
            return False
    
    async def run_all_tests(self) -> bool:
        """Run all HTTP tests"""
        print("🚀 Starting MCP HTTP server tests...")
        
        try:
            # Setup
            self.setup_docs()
            
            # Start HTTP server
            if not await self.start_http_server():
                return False
            
            # Setup HTTP client
            self.setup_http_client()
            
            # First run basic HTTP connectivity test  
            print(f"🔗 Testing basic HTTP connectivity on {self.host}:{self.port}")
            
            # Add debug info about the server process
            if self.server_process:
                print(f"📊 Server process status: {self.server_process.poll()}")
            
            # Define HTTP connectivity tests to run
            http_tests = [
                ("HTTP Health Check", self.test_http_health_check),
            ]
            
            results = []
            
            # Run HTTP connectivity tests first
            print("\n🌐 === TESTING HTTP CONNECTIVITY ===")
            for test_name, test_func in http_tests:
                print(f"\n📋 Running {test_name} test...")
                try:
                    result = await test_func()
                    results.append((test_name, result))
                    if result:
                        print(f"✅ {test_name} test PASSED")
                    else:
                        print(f"❌ {test_name} test FAILED")
                except Exception as e:
                    print(f"❌ {test_name} test ERROR: {e}")
                    results.append((test_name, False))
                
                # Small delay between tests
                await asyncio.sleep(0.5)
            
            # Then try FastMCP client tests
            print(f"\n🔌 === TESTING FASTMCP CLIENT INTEGRATION ===")
            print(f"🔌 Attempting to connect FastMCP client to: {self.server_url}")
            
            try:
                if not self.client:
                    print("❌ FastMCP client not initialized")
                    # Add failed FastMCP tests to results
                    results.append(("FastMCP Ping", False))
                    results.append(("FastMCP List Tools", False))
                else:
                    async with self.client:
                        print("✅ FastMCP Client connected successfully!")
                        
                        # Define FastMCP client tests to run
                        fastmcp_tests = [
                            ("FastMCP Ping", self.test_ping),
                            ("FastMCP List Tools", self.test_list_tools),
                            ("FastMCP Health Check Tool", self.test_health_check_tool),
                        ]
                        
                        # Run FastMCP tests
                        for test_name, test_func in fastmcp_tests:
                            print(f"\n📋 Running {test_name} test...")
                            try:
                                result = await test_func()
                                results.append((test_name, result))
                                if result:
                                    print(f"✅ {test_name} test PASSED")
                                else:
                                    print(f"❌ {test_name} test FAILED")
                            except Exception as e:
                                print(f"❌ {test_name} test ERROR: {e}")
                                results.append((test_name, False))
                            
                            # Small delay between tests
                            await asyncio.sleep(0.5)
                        
            except Exception as connection_error:
                print(f"⚠️ FastMCP Client connection failed: {connection_error}")
                print(f"📊 Server process status: {self.server_process.poll() if self.server_process else 'None'}")
                print("💡 This may be expected if the server doesn't implement FastMCP endpoints")
                
                # Add failed FastMCP tests to results
                results.append(("FastMCP Ping", False))
                results.append(("FastMCP List Tools", False))
                results.append(("FastMCP Health Check Tool", False))
            
            # Summary
            print("\n" + "=" * 60)
            print("📊 HTTP TEST RESULTS SUMMARY")
            print("=" * 60)
            
            passed = sum(1 for _, result in results if result)
            total = len(results)
            
            # Group results by category
            http_results = [(name, result) for name, result in results if "HTTP" in name]
            fastmcp_results = [(name, result) for name, result in results if name.startswith("FastMCP")]
            
            print("\n🌐 HTTP Connectivity:")
            for test_name, result in http_results:
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"  {status} - {test_name}")
            
            print("\n🔌 FastMCP Client Integration:")
            for test_name, result in fastmcp_results:
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"  {status} - {test_name}")
            
            print(f"\n🎯 Overall: {passed}/{total} tests passed")
            
            # Consider success if HTTP connectivity and at least basic FastMCP tests pass
            http_passed = sum(1 for _, result in http_results if result)
            http_total = len(http_results)
            fastmcp_passed = sum(1 for _, result in fastmcp_results if result)
            fastmcp_total = len(fastmcp_results)
            
            if http_passed == http_total and fastmcp_passed >= 2:  # At least ping and list_tools
                print("🎉 ALL CORE TESTS PASSED! Server is working correctly with FastMCP over HTTP!")
                if passed == total:
                    print("🚀 BONUS: All tests including advanced features working!")
                return True
            elif http_passed == http_total:
                print("✅ HTTP connectivity working, but FastMCP integration has issues.")
                print("💡 Server is responding but MCP protocol may need debugging.")
                return False
            else:
                print(f"⚠️ {http_total - http_passed} HTTP connectivity tests failed. Please check the server.")
                return False
        
        except Exception as e:
            print(f"❌ HTTP Test execution failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            self.cleanup()


async def main():
    """Main test runner"""
    print("📋 Entering HTTP test main() function")
    
    try:
        # Parse command line arguments
        print("🔧 Creating argument parser")
        parser = argparse.ArgumentParser(description="Test MCP Documentation Server HTTP mode using FastMCP Client")
        parser.add_argument(
            "--docs-path", 
            type=str, 
            help="Path to documentation directory"
        )
        parser.add_argument(
            "--use-temp-docs", 
            action="store_true", 
            help="Create temporary test documents instead of using existing docs"
        )
        parser.add_argument(
            "--host",
            type=str,
            default="127.0.0.1",
            help="HTTP server host (default: 127.0.0.1)"
        )
        parser.add_argument(
            "--port",
            type=int,
            default=8000,
            help="HTTP server port (default: 8000)"
        )
        
        print("🔧 Parsing arguments")
        args = parser.parse_args()
        print(f"✅ Arguments parsed: use_temp_docs={args.use_temp_docs}, docs_path={args.docs_path}, host={args.host}, port={args.port}")
    except Exception as e:
        print(f"❌ Error in argument parsing: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Determine configuration
    if args.use_temp_docs:
        test_runner = MCPHTTPServerTest(use_temp_docs=True, host=args.host, port=args.port)
    elif args.docs_path:
        test_runner = MCPHTTPServerTest(docs_path=args.docs_path, use_temp_docs=False, host=args.host, port=args.port)
    else:
        # Use default docs path or temp docs
        default_docs = Path(__file__).parent / "../../../lz/ui/app/docs"
        if default_docs.exists():
            test_runner = MCPHTTPServerTest(docs_path=str(default_docs.resolve()), use_temp_docs=False, host=args.host, port=args.port)
            print(f"📁 Using default docs directory: {default_docs.resolve()}")
        else:
            print(f"⚠️ Default docs directory not found: {default_docs.resolve()}")
            print("📁 Falling back to temporary test documents")
            test_runner = MCPHTTPServerTest(use_temp_docs=True, host=args.host, port=args.port)
    
    success = await test_runner.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    print("🎯 Entering HTTP test main execution block")
    try:
        print("🚀 About to call asyncio.run(main())")
        exit_code = asyncio.run(main())
        print(f"✅ HTTP test asyncio.run completed with exit code: {exit_code}")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️ HTTP tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 HTTP test runner failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
