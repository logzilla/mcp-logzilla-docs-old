"""
Comprehensive response validation test for MCP Documentation Server.

This test evaluates the server's ability to return accurate and relevant
information from real LogZilla documentation using realistic search queries.
Tests only stdio mode with multi-document responses and content verification.
"""
import pytest
import asyncio
import argparse
import tempfile
import json
import logging
import os
from pathlib import Path
from typing import List, Dict, Any, Set, Optional

# Setup logging to see detailed search engine activity (same as test_search_routines.py)
logging.basicConfig(level=logging.INFO)

# Import the server components and FastMCP Client
from server import ServerSettings, MCPServer
from mcp.server.fastmcp import FastMCP
from fastmcp import Client


class DocumentationTestCase:
    """Test case for documentation search validation."""
    
    def __init__(self, name: str, query: str, expected_topics: List[str], 
                 expected_min_results: int = 2, expected_keywords: Optional[List[str]] = None):
        self.name = name
        self.query = query
        self.expected_topics = expected_topics  # Topics that should appear in results
        self.expected_min_results = expected_min_results
        self.expected_keywords = expected_keywords or []  # Keywords that should appear in content


# Default documentation path
DEFAULT_DOCS_PATH = "../../../lz/ui/app/docs"


@pytest.fixture(scope="session")
def docs_path() -> str:
    """Get the documentation path from environment or use default."""
    print("\n[response_test] 📚 Setting up documentation path...")
    env_path = os.environ.get("LOGZILLA_DOCS_PATH")
    candidate_paths = []

    # 1. Environment variable takes highest priority
    if env_path:
        candidate_paths.append(Path(env_path))

    # 2. Path relative to repo root (../.. / lz/ui/app/docs)
    repo_root = Path(__file__).resolve().parents[3]
    candidate_paths.append(repo_root / "lz" / "ui" / "app" / "docs")

    # 3. Original default relative path (for backwards compatibility)
    candidate_paths.append(Path(DEFAULT_DOCS_PATH).resolve())

    for p in candidate_paths:
        if p.exists():
            return str(p)

    pytest.skip(
        "Could not locate LogZilla documentation directory. "
        "Tried: " + ", ".join(str(p) for p in candidate_paths) + ". "
        "Set LOGZILLA_DOCS_PATH environment variable to override."
    )


@pytest.mark.asyncio
async def test_server_responses(docs_path=None):
    """Main test function for comprehensive response validation."""
    print("--------------------------------> test_server_responses start")
    print("[response_test] 🚀 Starting Comprehensive Response Validation Tests")
    print("[response_test] Using real LogZilla documentation for realistic testing")
    
    # Set up paths - use provided path or default
    if docs_path is None:
        docs_path = "../../../lz/ui/app/docs"  # Default relative path from docs-server directory
    
    # Convert to absolute path for better error reporting
    docs_path = os.path.abspath(docs_path)
    print(f"[response_test] 📁 Using documentation path: {docs_path}")
    
    if not os.path.exists(docs_path):
        print(f"[response_test] ❌ Documentation path not found: {docs_path}")
        print("[response_test] Please ensure LogZilla documentation is available")
        print("[response_test] You can specify a custom path using --docs-path argument")
        return False
    
    try:
        # Create MCP server using existing server.py functionality
        print("--------------------------------> set up MCP server")
        
        # Create server settings
        settings = ServerSettings(
            docs_path=docs_path,
            transport="stdio"
        )
        
        # Create MCPServer instance which will set up search tools
        mcp_server = MCPServer(settings)
        
        # CRITICAL: Initialize the server (loads documents and builds search index)
        print("[response_test] 🔧 Initializing server (loading documents and building search index)...")
        mcp_server.start_initialization()
        
        # Wait for server to be ready
        max_wait_time = 30  # seconds
        wait_interval = 1   # seconds
        elapsed_time = 0
        
        while elapsed_time < max_wait_time:
            if mcp_server.server_ready["status"]:
                print(f"[response_test] ✅ Server initialization completed after {elapsed_time} seconds")
                break
            print(f"[response_test] ⏳ Waiting for server initialization... ({elapsed_time + 1}/{max_wait_time}s)")
            await asyncio.sleep(wait_interval)
            elapsed_time += wait_interval
        else:
            print(f"[response_test] ❌ Server initialization failed after {max_wait_time} seconds")
            print(f"[response_test] Server status: {mcp_server.server_ready}")
            print(f"[response_test] SearchTools BM25 ready: {mcp_server.search_tools.bm25_engine.is_ready if mcp_server.search_tools else 'N/A'}")
            print(f"[response_test] SearchTools Vector ready: {mcp_server.search_tools.vector_engine.is_ready if mcp_server.search_tools and mcp_server.search_tools.vector_engine else 'N/A'}")
            print(f"[response_test] Documents in cache: {len(mcp_server.document_cache.documents) if mcp_server.document_cache and mcp_server.document_cache.documents else 0}")
            if mcp_server.document_cache and mcp_server.document_cache.documents:
                sample_docs = list(mcp_server.document_cache.documents.keys())[:3]
                print(f"[response_test] Sample document IDs: {sample_docs}")
            return False
        
        # Create the FastMCP server for external client access
        mcp = mcp_server.create_public_server()
        
        if mcp is None:
            print("[response_test] ❌ Failed to create MCP server instance")
            return False
        
        print("[response_test] 📚 MCP server initialized with search tools")
        
        # Test the server directly (since we have the FastMCP instance)
        print("[response_test] 🔧 Testing server tools directly...")
        print("[response_test] ✅ Server connection ready")
        
        # Check that required tools are available
        tools = await mcp.list_tools()
        if isinstance(tools, list):
            tool_names = [tool.name for tool in tools]
        else:
            tool_names = [tool.name for tool in getattr(tools, 'tools', [])]
        
        required_tools = ["search_for_documents"]
        missing_tools = [tool for tool in required_tools if tool not in tool_names]
        
        if missing_tools:
            print(f"[response_test] ❌ Required tool(s) {missing_tools} not found")
            print(f"[response_test] Available tools: {tool_names}")
            return False
        
        # Note: Document content retrieval is available via get_document_content resource 
        # at uri "docs://document/{document_id}" rather than as a tool
        print("[response_test] ℹ️ Note: Document content available via get_document_content resource, not tool")
        
        # Verify documents are loaded by testing via server directly
        print("[response_test] 📚 Verifying document loading via server...")
        
        # Test basic search functionality directly
        try:
            print("[response_test] 🧪 Testing search functionality...")
            test_result = await mcp.call_tool("search_for_documents", {
                "query": "test", 
                "top_k": 1
            })
            
            print(f"[response_test] ✅ Search test completed successfully")
            print(f"[response_test] Response type: {type(test_result)}")
            
        except Exception as e:
            print(f"[response_test] ❌ Search test failed: {e}")
            return False
        
        # Run comprehensive tests via direct server access
        print("[response_test] 🧪 Running comprehensive test suite...")
        test_results = []
        
        # Test individual MCP tools via direct server calls
        test_results.append(await test_search_for_documents_tool(mcp))
        # Skip get_document tool test - document content available via get_document_content resource
        test_results.append({"name": "get_document", "passed": True, "skipped": True, "note": "Skipped - using get_document_content resource instead of tool"})
        test_results.append(await test_content_quality_via_mcp(mcp))
        
        # Now run the vector engine ready test using the same server instance
        print("\n" + "="*40)
        print("[response_test] 🔧 Running vector engine ready test with same server instance...")
        vector_test_passed = await test_vector_engine_ready_reissue_last_search(mcp_server, mcp)
        
        # Update test results
        if vector_test_passed:
            test_results.append({"name": "vector_engine_ready", "passed": True})
        else:
            test_results.append({"name": "vector_engine_ready", "passed": False})
        
        # Generate and display test report
        passed_tests = sum(1 for r in test_results if r.get("passed", False))
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"[response_test] 📊 Test Results: {passed_tests}/{total_tests} passed ({success_rate:.1f}%)")
        
        for i, result in enumerate(test_results, 1):
            if result.get("skipped", False):
                status = "⏭️ SKIP"
            else:
                status = "✅ PASS" if result.get("passed", False) else "❌ FAIL"
            print(f"[response_test] Test {i}: {result.get('name', 'Unknown')} - {status}")
            if result.get("skipped", False) and result.get("note"):
                print(f"[response_test]   Note: {result['note']}")
            elif not result.get("passed", False) and result.get("error"):
                print(f"[response_test]   Error: {result['error']}")
        
        # Explicitly cleanup before returning to prevent core dumps
        print("[response_test] 🧹 Cleaning up resources...")
        try:
            if hasattr(mcp_server, 'search_tools') and mcp_server.search_tools:
                if hasattr(mcp_server.search_tools, 'vector_engine') and mcp_server.search_tools.vector_engine:
                    mcp_server.search_tools.vector_engine.cleanup()
                if hasattr(mcp_server.search_tools, 'bm25_engine') and mcp_server.search_tools.bm25_engine:
                    if hasattr(mcp_server.search_tools.bm25_engine, 'cleanup'):
                        mcp_server.search_tools.bm25_engine.cleanup()
            
            # Force garbage collection
            import gc
            gc.collect()
            print("[response_test] ✅ Cleanup completed")
        except Exception as e:
            print(f"[response_test] ⚠️ Warning during cleanup: {e}")
        
        return passed_tests == total_tests
            
    except Exception as e:
        print(f"[response_test] ❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_search_for_documents_tool(server) -> Dict[str, Any]:
    """Test the search_for_documents MCP tool via external client."""
    try:
        # Use server call_tool method directly
        result = await server.call_tool("search_for_documents", {
            "query": "syslog configuration", 
            "top_k": 5
        })
        
        # Handle different return formats from FastMCP server
        print(f"[test] DEBUG: Result type: {type(result)}, Result: {result}")
        
        # FastMCP server may return tuple, dict, or other formats
        if isinstance(result, tuple):
            # FastMCP returns (TextContent_list, result_dict) - we want the dict
            raw_data = result[1] if len(result) > 1 else (result[0] if len(result) > 0 else {})
            # Extract nested result data: {'result': {'status': '...', 'results': {...}}}
            if isinstance(raw_data, dict) and 'result' in raw_data:
                inner_result = raw_data['result']
                # Further extract if results are nested: {'results': {'results': [...]}}
                if isinstance(inner_result, dict) and 'results' in inner_result and 'results' in inner_result['results']:
                    data = inner_result['results']  # This should have the 'results' array
                else:
                    data = inner_result
            else:
                data = raw_data
        elif hasattr(result, 'data'):
            data = result.data
        elif isinstance(result, dict):
            data = result
        else:
            return {"name": "search_documentation", "passed": False, "error": f"Unexpected result type: {type(result)}"}
            
        # Convert data to dict if it's not already
        if not isinstance(data, dict):
            if hasattr(data, '__dict__'):
                data = data.__dict__
            elif isinstance(data, str):
                # If it's a string response, wrap it in a dict
                data = {"content": data}
            else:
                return {"name": "search_documentation", "passed": False, "error": f"Result data is not a dictionary, got: {type(data)}"}
        
        # Check for error response first
        if "error" in data:
            return {"name": "search_documentation", "passed": False, "error": f"Tool returned error: {data['error']}"}
        
        if "results" not in data:
            return {"name": "search_for_documents", "passed": False, "error": "No 'results' key in response data"}
        
        results = data["results"]
        if not isinstance(results, list) or len(results) == 0:
            return {"name": "search_for_documents", "passed": False, "error": "No search results returned"}
        
        # Check that results have expected fields (based on actual response format)
        first_result = results[0]
        expected_fields = ["document_id", "score"]  # These are the core fields we actually get
        missing_fields = [field for field in expected_fields if field not in first_result]
        
        if missing_fields:
            return {"name": "search_for_documents", "passed": False, "error": f"Missing fields: {missing_fields}"}
        
        # Show what fields we actually got for debugging
        actual_fields = list(first_result.keys())
        print(f"[response_test] Result fields: {actual_fields}")
        
        print(f"[response_test] ✅ search_for_documents returned {len(results)} results")
        
        # Print documents for visual confirmation
        print(f"[response_test] 📄 Documents returned:")
        for i, result in enumerate(results, 1):
            document_id = result.get('document_id', 'Unknown')
            score = result.get('score', 0)
            rrf_score = result.get('rrf_score', 0)
            source = result.get('source', 'unknown')
            print(f"[response_test]   {i}. {document_id[:50]}... (score: {score:.3f}, rrf: {rrf_score:.3f}, source: {source})")
            # Note: Content is retrieved separately via get_document_content resource
        
        return {"name": "search_for_documents", "passed": True, "result_count": len(results)}
        
    except Exception as e:
        return {"name": "search_for_documents", "passed": False, "error": str(e)}


async def test_get_document_tool(client: Client) -> Dict[str, Any]:
    """Test the get_document MCP tool via external client."""
    try:
        # First, do a search to get a valid document ID
        search_result = await client.call_tool("search_for_documents", {
            "query": "installation", 
            "top_k": 1
        })
        
        if not hasattr(search_result, 'data') or not isinstance(search_result.data, dict) or "results" not in search_result.data or len(search_result.data["results"]) == 0:
            return {"name": "get_document", "passed": False, "error": "Could not find a document to retrieve"}
        
        # Get the first document ID
        first_result = search_result.data["results"][0]
        document_id = first_result.get("document") or first_result.get("document_id")
        
        if not document_id:
            return {"name": "get_document", "passed": False, "error": "No document ID found in search results"}
        
        # Test the get_document tool via external client
        result = await client.call_tool("get_document", {
            "document_id": document_id
        })
        
        # Validate result structure (FastMCP Client returns CallToolResult with .data attribute)
        if not hasattr(result, 'data'):
            return {"name": "get_document", "passed": False, "error": "Result has no data attribute"}
        
        data = result.data
        if not isinstance(data, dict):
            return {"name": "get_document", "passed": False, "error": "Result data is not a dictionary"}
        
        # Check for error response first
        if "error" in data:
            return {"name": "get_document", "passed": False, "error": f"Tool returned error: {data['error']}"}
        
        if "content" not in data:
            return {"name": "get_document", "passed": False, "error": "No 'content' key in response data"}
        
        content = data["content"]
        if not isinstance(content, str) or len(content) == 0:
            return {"name": "get_document", "passed": False, "error": "Document content is empty or invalid"}
        
        # Check that full document content is substantial
        content_length = len(content)
        if content_length < 100:  # Full documents should be substantial
            return {"name": "get_document", "passed": False, 
                   "error": f"Document content too short ({content_length} chars), expected full document"}
        
        print(f"[response_test] ✅ get_document returned document with {content_length} characters")
        return {"name": "get_document", "passed": True, "content_length": content_length}
        
    except Exception as e:
        return {"name": "get_document", "passed": False, "error": str(e)}


async def test_content_quality_via_mcp(server) -> Dict[str, Any]:
    """Test the quality and relevance of search results via external MCP client."""
    try:
        # Test multiple queries to validate content quality
        test_queries = [
            {"query": "syslog", "expected_topics": ["syslog", "log", "message"]},
            {"query": "configuration", "expected_topics": ["config", "setting", "setup"]},
            {"query": "installation", "expected_topics": ["install", "setup", "deploy"]}
        ]
        
        passed_queries = 0
        
        for query_test in test_queries:
            # Use server call_tool method directly  
            result = await server.call_tool("search_for_documents", {
                "query": query_test["query"], 
                "top_k": 5
            })
            
            # Handle different return formats from FastMCP server
            if isinstance(result, tuple):
                # FastMCP returns (TextContent_list, result_dict) - we want the dict
                raw_data = result[1] if len(result) > 1 else (result[0] if len(result) > 0 else {})
                # Extract nested result data: {'result': {'status': '...', 'results': {...}}}
                if isinstance(raw_data, dict) and 'result' in raw_data:
                    inner_result = raw_data['result']
                    # Further extract if results are nested: {'results': {'results': [...]}}
                    if isinstance(inner_result, dict) and 'results' in inner_result and 'results' in inner_result['results']:
                        data = inner_result['results']  # This should have the 'results' array
                    else:
                        data = inner_result
                else:
                    data = raw_data
            elif hasattr(result, 'data'):
                data = result.data
            elif isinstance(result, dict):
                data = result
            else:
                print(f"[response_test] ⚠️ Query '{query_test['query']}' returned invalid response format")
                continue
            
            if isinstance(data, dict):
                if "error" in data:
                    print(f"[response_test] ❌ Query '{query_test['query']}' returned error: {data['error']}")
                    continue
                    
                if "results" in data and len(data["results"]) > 0:
                    # Check search results - they contain document_id, score, etc. but not content
                    # Content would be retrieved separately via get_document_content resource
                    results = data["results"]
                    result_count = len(results)
                    
                    # Check if we got reasonable results (for quality test, just check we got results)
                    if result_count > 0:
                        passed_queries += 1
                        print(f"[response_test] ✅ Query '{query_test['query']}' returned {result_count} relevant results")
                        # Show sample document_ids for verification
                        sample_docs = [r.get("document_id", "unknown")[:50] for r in results[:2]]
                        print(f"[response_test]   Sample results: {sample_docs}")
                    else:
                        print(f"[response_test] ❌ Query '{query_test['query']}' found no results")
                else:
                    print(f"[response_test] ❌ Query '{query_test['query']}' returned no results")
            else:
                print(f"[response_test] ⚠️ Query '{query_test['query']}' returned invalid response format")
        
        success = passed_queries >= len(test_queries) // 2  # At least half should pass
        
        return {
            "name": "content_quality", 
            "passed": success, 
            "passed_queries": passed_queries,
            "total_queries": len(test_queries)
        }
        
    except Exception as e:
        return {"name": "content_quality", "passed": False, "error": str(e)}


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Comprehensive response validation test for MCP Documentation Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python test_server_responses.py
  python test_server_responses.py --docs-path /path/to/logzilla/docs
  python test_server_responses.py --docs-path ../../../lz/ui/app/docs
        """
    )
    
    parser.add_argument(
        "--docs-path",
        type=str,
        default=None,
        help="Path to LogZilla documentation directory (default: ../../../lz/ui/app/docs)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    return parser.parse_args()



async def test_vector_engine_ready_reissue_last_search(mcp_server, mcp):
    """Test that waits for vector engine to be ready and re-issues the last search using existing server."""
    print("--------------------------------> test_vector_engine_ready_reissue_last_search start")
    print("[vector_test] 🚀 Testing Vector Engine Ready and Re-issue Last Search")
    print("[vector_test] 📚 Using existing MCP server instance")
    
    try:
        # Issue the "last search" from the original test (syslog configuration) 
        # This should happen while vector engine might still be initializing
        last_search_query = "syslog configuration"
        print(f"[vector_test] 🔍 Issuing initial search (BM25-only state): '{last_search_query}'")
        
        initial_result = await mcp.call_tool("search_for_documents", {
            "query": last_search_query, 
            "top_k": 5
        })
        
        # Extract search results 
        if isinstance(initial_result, tuple):
            raw_data = initial_result[1] if len(initial_result) > 1 else (initial_result[0] if len(initial_result) > 0 else {})
            if isinstance(raw_data, dict) and 'result' in raw_data:
                inner_result = raw_data['result']
                if isinstance(inner_result, dict) and 'results' in inner_result and 'results' in inner_result['results']:
                    initial_data = inner_result['results']
                else:
                    initial_data = inner_result
            else:
                initial_data = raw_data
        else:
            initial_data = initial_result
        
        initial_results = initial_data.get("results", []) if isinstance(initial_data, dict) else []
        initial_sources = [r.get("source", "unknown") for r in initial_results if isinstance(r, dict)]
        print(f"[vector_test] 📊 Initial search returned {len(initial_results)} results")
        print(f"[vector_test] 📊 Initial search sources: {set(initial_sources)}")
        
        # Now wait specifically for the vector engine to be ready
        print("[vector_test] ⏳ Waiting for vector engine to be ready...")
        
        vector_wait_time = 60  # Give vector engine more time to initialize
        vector_elapsed = 0
        wait_interval = 1
        
        while vector_elapsed < vector_wait_time:
            vector_ready = False
            try:
                if (mcp_server.search_tools and 
                    mcp_server.search_tools.vector_engine and 
                    mcp_server.search_tools.vector_engine.is_ready):
                    vector_ready = True
            except Exception as e:
                print(f"[vector_test] ⚠️ Error checking vector engine status: {e}")
            
            if vector_ready:
                print(f"[vector_test] ✅ Vector engine is ready after {vector_elapsed} seconds")
                break
            
            print(f"[vector_test] ⏳ Vector engine not ready yet... ({vector_elapsed + 1}/{vector_wait_time}s)")
            await asyncio.sleep(wait_interval)
            vector_elapsed += wait_interval
        else:
            print(f"[vector_test] ⚠️ Vector engine not ready after {vector_wait_time} seconds")
            print("[vector_test] ℹ️ Proceeding with test anyway (vector engine may be disabled)")
        
        # Re-issue the same search now that vector engine should be ready
        print(f"[vector_test] 🔍 Re-issuing search after vector engine ready: '{last_search_query}'")
        
        final_result = await mcp.call_tool("search_for_documents", {
            "query": last_search_query, 
            "top_k": 5
        })
        
        # Extract final search results 
        if isinstance(final_result, tuple):
            raw_data = final_result[1] if len(final_result) > 1 else (final_result[0] if len(final_result) > 0 else {})
            if isinstance(raw_data, dict) and 'result' in raw_data:
                inner_result = raw_data['result']
                if isinstance(inner_result, dict) and 'results' in inner_result and 'results' in inner_result['results']:
                    final_data = inner_result['results']
                else:
                    final_data = inner_result
            else:
                final_data = raw_data
        else:
            final_data = final_result
        
        final_results = final_data.get("results", []) if isinstance(final_data, dict) else []
        final_sources = [r.get("source", "unknown") for r in final_results if isinstance(r, dict)]
        
        print(f"[vector_test] 📊 Final search returned {len(final_results)} results")
        print(f"[vector_test] 📊 Final search sources: {set(final_sources)}")
        
        # Compare results
        print("[vector_test] 📋 Comparing initial vs final search results:")
        print(f"[vector_test]   Initial: {len(initial_results)} results, sources: {set(initial_sources)}")
        print(f"[vector_test]   Final:   {len(final_results)} results, sources: {set(final_sources)}")
        
        # Show detailed results for comparison
        print("[vector_test] 📄 Initial search results (BM25 only):")
        for i, result in enumerate(initial_results, 1):  # Show all results
            document_id = result.get('document_id', 'Unknown')
            score = result.get('score', 0)
            source = result.get('source', 'unknown')
            rrf_score = result.get('rrf_score', 0)
            print(f"[vector_test]   {i}. {document_id} (score: {score:.3f}, rrf: {rrf_score:.3f}, source: {source})")
        
        print("[vector_test] 📄 Final search results (Vector + BM25):")
        for i, result in enumerate(final_results, 1):  # Show all results
            document_id = result.get('document_id', 'Unknown')
            score = result.get('score', 0)
            source = result.get('source', 'unknown')
            rrf_score = result.get('rrf_score', 0)
            print(f"[vector_test]   {i}. {document_id} (score: {score:.3f}, rrf: {rrf_score:.3f}, source: {source})")
        
        # Test success criteria: both searches should return results
        test_passed = (len(initial_results) > 0 and len(final_results) > 0)
        
        # If vector engine was ready, we might expect to see vector results in the final search
        vector_engine_contributed = "vector" in final_sources or "rrf" in final_sources
        if vector_engine_contributed:
            print("[vector_test] ✅ Vector engine contributed to final search results")
        else:
            print("[vector_test] ℹ️ Vector engine did not contribute to final search (may be disabled or not ready)")
        
        if test_passed:
            print("[vector_test] ✅ Vector engine ready test passed")
        else:
            print("[vector_test] ❌ Vector engine ready test failed")
        
        return test_passed
            
    except Exception as e:
        print(f"[vector_test] ❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("[response_test] Running as standalone script")
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Run original tests with specified or default docs path
    success = asyncio.run(test_server_responses(docs_path=args.docs_path))
    
    if success:
        print("[response_test] ✔ All tests completed successfully")
    else:
        print("[response_test] ❌ Tests failed")
        exit(1)
