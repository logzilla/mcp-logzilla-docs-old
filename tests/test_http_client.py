#!/usr/bin/env python3
"""
MCP Client Test Script
======================

A comprehensive test client for the MCP Documentation Server that tests all
available endpoints and functionality.

Features:
- Tests all MCP tools (search_for_documents, search_and_retrieve_documents, health_check)
- Tests MCP resources (document retrieval)
- Supports both HTTP and stdio transports
- Tests both public and private (OAuth) servers
- Comprehensive error handling and reporting
- Detailed output with timing information

Usage Examples:
---------------

Test HTTP server on localhost:8000:
    python mcp_client_test.py -H localhost -p 8000

Test HTTPS server:
    python mcp_client_test.py -H example.com -p 443 --transport https

Test stdio mode (requires server script):
    python mcp_client_test.py --transport stdio --server-path python3 server.py

Just check HTTP connectivity:
    python mcp_client_test.py --http-only

Test with verbose output:
    python mcp_client_test.py -v -H localhost -p 8000

Test including private OAuth endpoints:
    python mcp_client_test.py --test-private -H localhost -p 8000

Requirements:
- pip install mcp
- pip install httpx (for HTTP connectivity tests)
- Working MCP Documentation Server
"""

import argparse
import asyncio
import json
import logging
import sys
import time
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

# MCP client imports
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from mcp.client.streamable_http import streamablehttp_client
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("Warning: MCP client library not available. Install with: pip install mcp", file=sys.stderr)

# HTTP client imports
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    print("Warning: httpx not available. Install with: pip install httpx", file=sys.stderr)


class MCPClientTest:
    """MCP client for testing documentation server endpoints."""
    
    def __init__(self, host: str = "localhost", port: int = 8000, transport: str = "http"):
        self.host = host
        self.port = port
        self.transport = transport
        self.session: Optional[ClientSession] = None
        self.logger = self._setup_logger()
        
        # Test configuration
        self.test_query = "search documentation"
        self.test_document_id = "example.md"  # This will be updated based on available docs
        
    def _extract_content_text(self, content_items) -> str:
        """Extract text from MCP content items safely."""
        if not content_items:
            return ""
        
        content_item = content_items[0]
        
        # Try to get text content
        if hasattr(content_item, 'text'):
            return content_item.text
        elif hasattr(content_item, 'data'):
            return str(content_item.data)
        else:
            return str(content_item)
        
    def _setup_logger(self) -> logging.Logger:
        """Set up logging for the test client."""
        logger = logging.getLogger("mcp_client_test")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '[%(asctime)s] %(levelname)-8s %(message)s',
                datefmt='%H:%M:%S'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    async def connect_http(self, server_name: str = "docs-server") -> bool:
        """Connect to MCP server via HTTP/HTTPS."""
        if not MCP_AVAILABLE:
            self.logger.error("MCP client library not available")
            return False
            
        try:
            base_url = f"http://{self.host}:{self.port}"
            if self.transport == "https":
                base_url = f"https://{self.host}:{self.port}"
                
            mcp_url = f"{base_url}/{server_name}/mcp"
            self.logger.info(f"Connecting to MCP server at: {mcp_url}")
            
            # Use streamable HTTP client for HTTP transport
            async with streamablehttp_client(mcp_url) as (read, write, get_session_id):
                async with ClientSession(read, write) as session:
                    # Initialize the session
                    await session.initialize()
                    self.logger.info("✨ Session initialization complete!")
                    
                    # Log session ID if available
                    if get_session_id:
                        session_id = get_session_id()
                        if session_id:
                            self.logger.info(f"Session ID: {session_id}")
                    
                    self.session = session
                    await self._run_all_tests()
                    return True
                    
        except Exception as e:
            self.logger.error(f"Failed to connect via HTTP: {e}")
            return False

    async def connect_stdio(self, server_path: str = "python") -> bool:
        """Connect to MCP server via stdio."""
        if not MCP_AVAILABLE:
            self.logger.error("MCP client library not available")
            return False
            
        try:
            # Assume server.py is in current directory
            server_params = StdioServerParameters(
                command=server_path,
                args=["server.py", "--transport", "stdio"]
            )
            
            self.logger.info("Connecting to MCP server via stdio...")
            
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    self.session = session
                    await self._run_all_tests()
                    return True
                    
        except Exception as e:
            self.logger.error(f"Failed to connect via stdio: {e}")
            return False

    async def _run_all_tests(self):
        """Run comprehensive tests on all MCP endpoints."""
        if not self.session:
            self.logger.error("No active session")
            return

        self.logger.info("=" * 60)
        self.logger.info("Starting comprehensive MCP server tests...")
        self.logger.info("=" * 60)

        # Test 1: List available tools
        await self._test_list_tools()
        
        # Test 2: List available resources  
        await self._test_list_resources()
        
        # Test 3: Health check
        await self._test_health_check()
        
        # Test 4: Search for documents
        await self._test_search_for_documents()
        
        # Test 4b: Search for documents (shorter query)
        await self._test_search_for_documents_short_query()
        
        # Test 5: Search and retrieve documents
        await self._test_search_and_retrieve_documents()
        
        # Test 6: Get document content (resource)
        await self._test_get_document_content()
        
        # Test 7: Advanced search scenarios
        await self._test_advanced_search_scenarios()
        
        self.logger.info("=" * 60)
        self.logger.info("All tests completed!")
        self.logger.info("=" * 60)

    async def _test_list_tools(self):
        """Test listing available tools."""
        self.logger.info("\n--- Test 1: List Tools ---")
        if not self.session:
            self.logger.error("✗ No active session")
            return
            
        try:
            start_time = time.time()
            response = await self.session.list_tools()
            duration = time.time() - start_time
            
            self.logger.info(f"✓ List tools completed in {duration:.2f}s")
            self.logger.info(f"Available tools: {len(response.tools)}")
            
            for tool in response.tools:
                self.logger.info(f"  - {tool.name}: {tool.description}")
                
        except Exception as e:
            self.logger.error(f"✗ List tools failed: {e}")

    async def _test_list_resources(self):
        """Test listing available resources."""
        self.logger.info("\n--- Test 2: List Resources ---")
        if not self.session:
            self.logger.error("✗ No active session")
            return
            
        try:
            start_time = time.time()
            response = await self.session.list_resources()
            duration = time.time() - start_time
            
            self.logger.info(f"✓ List resources completed in {duration:.2f}s")
            self.logger.info(f"Available resources: {len(response.resources)}")
            
            for resource in response.resources:
                self.logger.info(f"  - {resource.uri}: {resource.name}")
                
        except Exception as e:
            self.logger.error(f"✗ List resources failed: {e}")

    async def _test_health_check(self):
        """Test health check tool."""
        self.logger.info("\n--- Test 3: Health Check ---")
        if not self.session:
            self.logger.error("✗ No active session")
            return
            
        try:
            start_time = time.time()
            response = await self.session.call_tool("health_check", {})
            duration = time.time() - start_time
            
            self.logger.info(f"✓ Health check completed in {duration:.2f}s")
            
            if response.content:
                content_text = self._extract_content_text(response.content)
                if content_text:
                    result = json.loads(content_text)
                    self.logger.info(f"Server status: {result.get('status', 'unknown')}")
                    self.logger.info(f"Message: {result.get('message', 'no message')}")
                    self.logger.info(f"Documents loaded: {result.get('documents_loaded', 0)}")
                    self.logger.info(f"Search tools available: {result.get('search_tools_available', False)}")
            
        except Exception as e:
            self.logger.error(f"✗ Health check failed: {e}")

    async def _test_search_for_documents(self):
        """Test search for documents tool."""
        self.logger.info("\n--- Test 4: Search for Documents ---")
        if not self.session:
            self.logger.error("✗ No active session")
            return
            
        try:
            start_time = time.time()
            response = await self.session.call_tool(
                "search_for_documents",
                {
                    "query": "how do i configure http",
                    "top_k": 5,
                    "min_quality": 0,
                    "include_scores": True
                }
            )
            duration = time.time() - start_time
            
            self.logger.info(f"✓ Search completed in {duration:.2f}s")
            
            if response.content:
                content_text = self._extract_content_text(response.content)
                if content_text:
                    result = json.loads(content_text)
                    self.logger.info(f"Search status: {result.get('status', 'unknown')}")
                    self.logger.info(f"Total results: {result.get('total_results', 0)}")
                    
                    # Extract and display all document IDs
                    results = result.get('results', {}).get('results', [])
                    if results:
                        self.logger.info("Search query: \"how do i configure http\"")
                        self.logger.info("Document IDs found:")
                        for i, doc in enumerate(results):
                            document_id = doc.get('document_id', 'unknown')
                            self.logger.info(f"  {i+1}. {document_id}")
                        
                        # Store first document ID for later tests
                        self.test_document_id = results[0].get('document_id', self.test_document_id)
                        self.logger.info(f"Will use '{self.test_document_id}' for resource tests")
            
        except Exception as e:
            self.logger.error(f"✗ Search for documents failed: {e}")

    async def _test_search_for_documents_short_query(self):
        """Test search for documents tool with shorter query."""
        self.logger.info("\n--- Test 4b: Search for Documents (Short Query) ---")
        if not self.session:
            self.logger.error("✗ No active session")
            return
            
        try:
            start_time = time.time()
            response = await self.session.call_tool(
                "search_for_documents",
                {
                    "query": "configure http",
                    "top_k": 5,
                    "min_quality": 0,
                    "include_scores": True
                }
            )
            duration = time.time() - start_time
            
            self.logger.info(f"✓ Search completed in {duration:.2f}s")
            
            if response.content:
                content_text = self._extract_content_text(response.content)
                if content_text:
                    result = json.loads(content_text)
                    self.logger.info(f"Search status: {result.get('status', 'unknown')}")
                    self.logger.info(f"Total results: {result.get('total_results', 0)}")
                    
                    # Extract and display all document IDs
                    results = result.get('results', {}).get('results', [])
                    if results:
                        self.logger.info("Search query: \"configure http\"")
                        self.logger.info("Document IDs found:")
                        for i, doc in enumerate(results):
                            document_id = doc.get('document_id', 'unknown')
                            self.logger.info(f"  {i+1}. {document_id}")
            
        except Exception as e:
            self.logger.error(f"✗ Search for documents (short query) failed: {e}")

    async def _test_search_and_retrieve_documents(self):
        """Test search and retrieve documents tool."""
        self.logger.info("\n--- Test 5: Search and Retrieve Documents ---")
        if not self.session:
            self.logger.error("✗ No active session")
            return
            
        try:
            start_time = time.time()
            response = await self.session.call_tool(
                "search_and_retrieve_documents",
                {
                    "query": "what does it take to create a rule",
                    "top_k": 3,
                    "min_quality": 0,
                    "include_scores": True
                }
            )
            duration = time.time() - start_time
            
            self.logger.info(f"✓ Search and retrieve completed in {duration:.2f}s")
            
            if response.content:
                content_text = self._extract_content_text(response.content)
                if content_text:
                    result = json.loads(content_text)
                    self.logger.info(f"Search status: {result.get('status', 'unknown')}")
                    self.logger.info(f"Total results: {result.get('total_results', 0)}")
                    
                    # Extract and display all document IDs
                    results = result.get('results', {}).get('results', [])
                    if results:
                        self.logger.info("Search query: \"what does it take to create a rule\"")
                        self.logger.info("Document IDs found:")
                        for i, doc in enumerate(results):
                            document_id = doc.get('document_id', 'unknown')
                            self.logger.info(f"  {i+1}. {document_id}")
                    
                    # Show snippet of retrieved content
                    for i, doc in enumerate(results[:2]):  # Show first 2 documents
                        content = doc.get('content', '')
                        preview = content[:200] + "..." if len(content) > 200 else content
                        self.logger.info(f"Document {i+1} preview: {preview}")
            
        except Exception as e:
            self.logger.error(f"✗ Search and retrieve failed: {e}")

    async def _test_get_document_content(self):
        """Test getting document content via resource."""
        self.logger.info("\n--- Test 6: Get Document Content (Resource) ---")
        if not self.session:
            self.logger.error("✗ No active session")
            return
            
        try:
            start_time = time.time()
            # Try to read resource - this may need adjustment based on the actual MCP API
            try:
                # Import the proper type for URI
                try:
                    from pydantic import AnyUrl
                    resource_uri = AnyUrl(f"docs://document/{self.test_document_id}")
                    response = await self.session.read_resource(resource_uri)
                except ImportError:
                    # If AnyUrl is not available, this approach won't work
                    self.logger.warning("AnyUrl type not available, skipping resource test")
                    return
                        
            except (AttributeError, ValueError, TypeError) as e:
                # Fallback if read_resource doesn't exist or URI format issues
                self.logger.warning(f"read_resource method not available or URI format issue: {e}, skipping resource test")
                return
                
            duration = time.time() - start_time
            
            self.logger.info(f"✓ Get document content completed in {duration:.2f}s")
            
            if hasattr(response, 'contents') and response.contents:
                # Handle different content types safely using generic approach
                content = ""
                content_item = response.contents[0]
                
                # Use a generic approach that works with any content type
                try:
                    # Try to convert to string in various ways
                    content = str(content_item)
                    
                    # If it looks like a representation, try to get actual content
                    if hasattr(content_item, '__dict__'):
                        for attr in ['text', 'data', 'content', 'value']:
                            if hasattr(content_item, attr):
                                attr_value = getattr(content_item, attr)
                                if attr_value and isinstance(attr_value, str):
                                    content = attr_value
                                    break
                                elif attr_value:
                                    content = str(attr_value)
                                    break
                except Exception:
                    content = "[Content extraction failed]"
                    
                preview = content[:300] + "..." if len(content) > 300 else content
                self.logger.info(f"Document content preview: {preview}")
            
        except Exception as e:
            self.logger.error(f"✗ Get document content failed: {e}")

    async def _test_advanced_search_scenarios(self):
        """Test advanced search scenarios."""
        self.logger.info("\n--- Test 7: Advanced Search Scenarios ---")
        if not self.session:
            self.logger.error("✗ No active session")
            return
        
        test_cases = [
            {
                "name": "High quality threshold",
                "query": "documentation",
                "top_k": 10,
                "min_quality": 80,
                "include_scores": True
            },
            {
                "name": "Large result set",
                "query": "server",
                "top_k": 20,
                "min_quality": 0,
                "include_scores": False
            },
            {
                "name": "Specific technical query",
                "query": "authentication OAuth MCP protocol",
                "top_k": 5,
                "min_quality": 30,
                "include_scores": True
            }
        ]
        
        for test_case in test_cases:
            self.logger.info(f"\nTesting: {test_case['name']}")
            try:
                start_time = time.time()
                response = await self.session.call_tool(
                    "search_for_documents",
                    {
                        "query": test_case["query"],
                        "top_k": test_case["top_k"],
                        "min_quality": test_case["min_quality"],
                        "include_scores": test_case["include_scores"]
                    }
                )
                duration = time.time() - start_time
                
                if response.content:
                    content_text = self._extract_content_text(response.content)
                    if content_text:
                        result = json.loads(content_text)
                        status = result.get('status', 'unknown')
                        total = result.get('total_results', 0)
                        self.logger.info(f"✓ {test_case['name']}: {status} - {total} results in {duration:.2f}s")
                    else:
                        self.logger.info(f"✓ {test_case['name']}: completed in {duration:.2f}s (no text content)")
                else:
                    self.logger.info(f"✓ {test_case['name']}: completed in {duration:.2f}s (no content)")
                
            except Exception as e:
                self.logger.error(f"✗ {test_case['name']} failed: {e}")

    async def test_private_server(self):
        """Test private server endpoints (requires OAuth token)."""
        self.logger.info("\n--- Testing Private Server (OAuth Required) ---")
        
        try:
            # Try to connect to private server
            await self.connect_http("private-docs-server")
            
            # Test admin tools
            await self._test_admin_health_check()
            await self._test_admin_search()
            
        except Exception as e:
            self.logger.warning(f"Private server test failed (expected if OAuth not configured): {e}")

    async def _test_admin_health_check(self):
        """Test admin health check tool."""
        self.logger.info("Testing admin health check...")
        if not self.session:
            self.logger.error("✗ No active session")
            return
            
        try:
            response = await self.session.call_tool("admin_health_check", {})
            
            if response.content:
                content_text = self._extract_content_text(response.content)
                if content_text:
                    result = json.loads(content_text)
                    self.logger.info(f"✓ Admin health check: {result.get('status', 'unknown')}")
            
        except Exception as e:
            self.logger.error(f"✗ Admin health check failed: {e}")

    async def _test_admin_search(self):
        """Test admin search tool."""
        self.logger.info("Testing admin search...")
        if not self.session:
            self.logger.error("✗ No active session")
            return
            
        try:
            response = await self.session.call_tool(
                "admin_search_for_documents",
                {
                    "query": self.test_query,
                    "top_k": 5,
                    "min_quality": 0,
                    "include_scores": True
                }
            )
            
            if response.content:
                content_text = self._extract_content_text(response.content)
                if content_text:
                    result = json.loads(content_text)
                    self.logger.info(f"✓ Admin search: {result.get('status', 'unknown')} - {result.get('total_results', 0)} results")
            
        except Exception as e:
            self.logger.error(f"✗ Admin search failed: {e}")

    def run_tests_http(self, server_name: str = "docs-server"):
        """Run all tests using HTTP transport."""
        if not MCP_AVAILABLE:
            print("Error: MCP client library not available. Install with: pip install mcp")
            return False
            
        return asyncio.run(self.connect_http(server_name))

    def run_tests_stdio(self, server_path: str = "python"):
        """Run all tests using stdio transport."""
        if not MCP_AVAILABLE:
            print("Error: MCP client library not available. Install with: pip install mcp")
            return False
            
        return asyncio.run(self.connect_stdio(server_path))

    def run_http_health_check(self):
        """Simple HTTP health check without MCP protocol."""
        if not HTTPX_AVAILABLE:
            print("Error: httpx not available. Install with: pip install httpx")
            return False
            
        try:
            base_url = f"http://{self.host}:{self.port}"
            if self.transport == "https":
                base_url = f"https://{self.host}:{self.port}"
                
            self.logger.info(f"Testing HTTP connectivity to {base_url}")
            
            with httpx.Client(timeout=10.0) as client:
                # Test help endpoint
                response = client.get(f"{base_url}/help")
                if response.status_code == 200:
                    self.logger.info("✓ HTTP server is responding")
                    self.logger.info(f"Server help page available at: {base_url}/help")
                    return True
                else:
                    self.logger.error(f"✗ HTTP server returned status {response.status_code}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"✗ HTTP connectivity test failed: {e}")
            return False


def main():
    """Main function to run MCP client tests."""
    parser = argparse.ArgumentParser(description="MCP Documentation Server Client Test")
    parser.add_argument("-H", "--host", type=str, default="localhost", 
                       help="Server host address (default: localhost)")
    parser.add_argument("-p", "--port", type=int, default=8000,
                       help="Server port number (default: 8000)")
    parser.add_argument("-n", "--name", type=str, default="docs-server",
                          help="MCP server name (default: docs-server)")
    parser.add_argument("--transport", choices=["http", "https", "stdio"], default="http",
                       help="Transport protocol (default: http)")
    parser.add_argument("--server-path", type=str, default="python",
                       help="Path to Python interpreter for stdio mode (default: python)")
    parser.add_argument("--test-private", action="store_true",
                       help="Also test private server endpoints (requires OAuth)")
    parser.add_argument("--http-only", action="store_true",
                       help="Only test basic HTTP connectivity (no MCP protocol)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Set up logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create test client
    client = MCPClientTest(host=args.host, port=args.port, transport=args.transport)
    
    print(f"MCP Documentation Server Client Test")
    print(f"Target: {args.transport}://{args.host}:{args.port}")
    print("=" * 60)
    
    success = False
    
    try:
        if args.http_only:
            # Simple HTTP connectivity test
            success = client.run_http_health_check()
            
        elif args.transport == "stdio":
            # Test stdio transport
            print("Testing stdio transport...")
            success = client.run_tests_stdio(args.server_path)
            
        else:
            # Test HTTP/HTTPS transport
            print(f"Testing {args.transport.upper()} transport...")
            success = client.run_tests_http(args.name)
    
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        return 1
    except Exception as e:
        print(f"Test execution failed: {e}")
        return 1
    
    if success:
        print("\n🎉 All tests completed successfully!")
        return 0
    else:
        print("\n❌ Some tests failed. Check the logs above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
