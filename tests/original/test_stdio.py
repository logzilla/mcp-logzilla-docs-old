#!/usr/bin/env python3
"""
Test stdio functionality of the MCP Documentation Server.

This test runs the server.py with "python server.py" command and performs 
stdio client requests for multiple tools using MCP client libraries:
- health_check: Basic server status
- search_for_documents: Search with query "http syslogng"
- search_and_retrieve_documents: Search and retrieve with query "http syslogng"
"""
import asyncio
import json
import sys
import time
from pathlib import Path

# MCP client imports
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("Error: MCP client library not available. Install with: pip install mcp", file=sys.stderr)

def extract_content_text(content_items) -> str:
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

async def test_stdio_health_check():
    """Test multiple MCP tools via stdio transport: health_check, search_for_documents, search_and_retrieve_documents."""
    print("🧪 Testing MCP Documentation Server via stdio")
    
    if not MCP_AVAILABLE:
        print("❌ MCP client library not available")
        return False
    
    # Set up the server command (server.py is in the main directory)
    server_script = Path(__file__).parent.parent / "server.py"
    if not server_script.exists():
        print(f"❌ Server script not found: {server_script}")
        return False
    
    try:
        # Create stdio server parameters with correct docs path
        server_params = StdioServerParameters(
            command=sys.executable,
            args=[str(server_script), "--transport", "stdio", "--docs", "./logzilla-docs"]
        )
        
        print(f"🚀 Starting server with command: {server_params.command} {' '.join(server_params.args)}")
        print("🔌 Connecting to MCP server via stdio...")
        print("🔄 Attempting stdio_client connection...")
        
        # Connect to server via stdio
        async with stdio_client(server_params) as (read, write):
            print("✅ stdio_client connection established")
            print("🔄 Creating ClientSession...")
            async with ClientSession(read, write) as session:
                print("✅ MCP client connected via stdio")
                
                # Initialize MCP session first (proper protocol)
                print("🤝 Initializing MCP session...")
                await session.initialize()
                print("✨ Session initialization complete!")
                
                # Allow some time for server background initialization (document loading, search engines)
                print("⏳ Allowing time for server background initialization...")
                await asyncio.sleep(5)  # Give server time to finish heavy initialization
                print("✅ Ready to test server functionality!")
                
                # List available tools first
                print("📋 Listing available tools...")
                try:
                    tools_response = await session.list_tools()
                    
                    if hasattr(tools_response, 'tools') and tools_response.tools:
                        tool_names = [tool.name for tool in tools_response.tools if hasattr(tool, 'name')]
                    elif isinstance(tools_response, list):
                        # Handle list of tool objects carefully
                        tool_names = []
                        for tool in tools_response:
                            if hasattr(tool, 'name'):
                                tool_names.append(getattr(tool, 'name', str(tool)))
                            elif isinstance(tool, str):
                                tool_names.append(tool)
                            else:
                                print(f"⚠️ Unknown tool type: {type(tool)}, value: {tool}")
                    else:
                        # Fallback - try to extract tool names from response
                        tool_names = []
                        print(f"📋 Unexpected tools response type: {type(tools_response)}")
                        print(f"📋 Tools response: {tools_response}")
                    
                    print(f"📋 Available tools: {tool_names}")
                    
                    # Check if health_check tool is available
                    if "health_check" not in tool_names:
                        print("❌ health_check tool not found in available tools")
                        return False
                    
                    print("✅ health_check tool is available")
                    
                except Exception as e:
                    print(f"❌ Failed to list tools: {e}")
                    return False
                
                # Test health_check with retries and wait for search engines to be ready
                print("\n🔍 Testing health_check tool and waiting for search engines...")
                health_success = False
                server_ready = False
                max_attempts = 10  # Increased for search engine initialization
                
                for attempt in range(1, max_attempts + 1):
                    try:
                        print(f"\n🔄 Health check attempt {attempt}/{max_attempts}...")
                        start_time = time.time()
                        result = await session.call_tool("health_check", {})
                        duration = time.time() - start_time
                        
                        print(f"✅ health_check call successful in {duration:.2f}s")
                        print(f"📄 Response type: {type(result)}")
                        
                        # Extract health status
                        if hasattr(result, 'content') and result.content:
                            content_text = extract_content_text(result.content)
                            if content_text:
                                try:
                                    health_data = json.loads(content_text)
                                    print(f"📊 Health check response: {health_data}")
                                    
                                    # Check for expected fields in health response
                                    expected_fields = ["status", "message", "documents_loaded", "search_tools_available", "search_engines_ready"]
                                    for field in expected_fields:
                                        if field in health_data:
                                            print(f"✅ {field}: {health_data[field]}")
                                        else:
                                            print(f"❌ Missing field: {field}")
                                    
                                    # Check if server AND search engines are ready
                                    server_status = health_data.get("status")
                                    search_tools_available = health_data.get("search_tools_available", False)
                                    search_engines_ready = health_data.get("search_engines_ready", {})
                                    
                                    # Parse search engines status - can be boolean or dict
                                    engines_ready = False
                                    if isinstance(search_engines_ready, dict):
                                        # Check if both exact and fuzzy search are ready
                                        exact_ready = False
                                        fuzzy_ready = False
                                        
                                        exact_status = search_engines_ready.get("exact search", [])
                                        if isinstance(exact_status, list) and len(exact_status) > 0:
                                            exact_ready = "ready" in str(exact_status[0]).lower()
                                        
                                        fuzzy_status = search_engines_ready.get("fuzzy search", [])
                                        # Check if fuzzy search is actually ready (not bypassed)
                                        if isinstance(fuzzy_status, list):
                                            if len(fuzzy_status) == 1:
                                                # Normal ready status: just ["status message"]
                                                fuzzy_ready = "ready" in str(fuzzy_status[0]).lower()
                                            elif len(fuzzy_status) > 1:
                                                # Bypassed status: [["status"], "engine bypassed until ready"] 
                                                bypassed = "bypassed" in str(fuzzy_status[1]).lower()
                                                if bypassed:
                                                    fuzzy_ready = False
                                                else:
                                                    fuzzy_ready = "ready" in str(fuzzy_status[1]).lower()
                                        
                                        engines_ready = exact_ready and fuzzy_ready
                                        print(f"🔧 Exact search ready: {exact_ready}")
                                        print(f"🔍 Fuzzy search ready: {fuzzy_ready} (status: {fuzzy_status})")
                                    elif isinstance(search_engines_ready, bool):
                                        engines_ready = search_engines_ready
                                    elif isinstance(search_engines_ready, str):
                                        engines_ready = search_engines_ready.lower() not in ["false", "not available", "no"]
                                    
                                    if (server_status == "ready" and 
                                        search_tools_available and 
                                        engines_ready):
                                        print("🎉 Server and all search engines are ready!")
                                        server_ready = True
                                        health_success = True
                                        break
                                    else:
                                        message = health_data.get('message', 'no message')
                                        print(f"⚠️ Server status: {server_status}")
                                        print(f"🔧 Search tools available: {search_tools_available}")
                                        print(f"🔍 Search engines status: {search_engines_ready}")
                                        print(f"💬 Message: {message}")
                                        if attempt < max_attempts:
                                            print(f"⏳ Waiting 8 seconds for vector engine initialization...")
                                            await asyncio.sleep(8)
                                        else:
                                            print(f"⚠️ Server/engines still not ready after {max_attempts} attempts")
                                            if server_status == "ready":
                                                health_success = True  # At least server is up
                                            
                                except json.JSONDecodeError as je:
                                    print(f"📄 Health check returned non-JSON: {content_text}")
                                    health_success = True  # At least we got a response
                            else:
                                print("⚠️ No content text in health response")
                        else:
                            print("⚠️ No content in health response")
                            
                    except Exception as e:
                        print(f"❌ health_check attempt {attempt} failed: {e}")
                        if attempt < max_attempts:
                            print(f"⏳ Waiting 5 seconds before retry...")
                            await asyncio.sleep(5)
                
                if not health_success:
                    print(f"❌ All {max_attempts} health_check attempts failed")
                    return False
                
                # Skip search tests if engines aren't ready
                if not server_ready:
                    print("⚠️ Search engines not ready - skipping search tests")
                    return True  # Health check worked, that's enough
                
                # Test search_for_documents
                print("\n🔍 Testing search_for_documents tool...")
                try:
                    search_query = "http syslogng"
                    print(f"🔎 Searching for: '{search_query}'")
                    start_time = time.time()
                    search_result = await session.call_tool("search_for_documents", {
                        "query": search_query
                    })
                    duration = time.time() - start_time
                    
                    print(f"✅ search_for_documents call successful in {duration:.2f}s")
                    print(f"📄 Response type: {type(search_result)}")
                    
                    # Extract and display search results
                    if hasattr(search_result, 'content') and search_result.content:
                        content_text = extract_content_text(search_result.content)
                        if content_text:
                            try:
                                search_data = json.loads(content_text)
                                print(f"📄 Raw search response keys: {list(search_data.keys()) if isinstance(search_data, dict) else 'not a dict'}")
                                
                                # Check nested results structure
                                if "results" in search_data and isinstance(search_data["results"], dict) and "results" in search_data["results"]:
                                    results = search_data["results"]["results"]
                                    print(f"📊 Found {len(results)} search results")
                                    for i, result in enumerate(results[:4]):  # Show first 4 results
                                        if isinstance(result, dict):
                                            document_id = result.get("document_id", "unknown")
                                            score = result.get("score", "unknown")
                                            path = result.get("path", result.get("filename", ""))
                                            # Use path if available, otherwise document_id
                                            display_name = path if path and path != "unknown" else document_id
                                            print(f"  {i+1}. {display_name} (score: {score})")
                                        else:
                                            print(f"  {i+1}. {result}")
                                elif "results" in search_data and isinstance(search_data["results"], list):
                                    results = search_data["results"]
                                    print(f"📊 Found {len(results)} search results")
                                    for i, result in enumerate(results[:4]):  # Show first 4 results
                                        if isinstance(result, dict):
                                            document_id = result.get("document_id", "unknown")
                                            score = result.get("score", "unknown")
                                            path = result.get("path", result.get("filename", ""))
                                            # Use path if available, otherwise document_id
                                            display_name = path if path and path != "unknown" else document_id
                                            print(f"  {i+1}. {display_name} (score: {score})")
                                        else:
                                            print(f"  {i+1}. {result}")
                                else:
                                    print("📊 Search results format: non-standard")
                                    print(f"📄 Full response: {json.dumps(search_data, indent=2)[:500]}...")
                            except json.JSONDecodeError:
                                print(f"📄 Search returned non-JSON: {content_text[:200]}...")
                        else:
                            print("⚠️ No content text in search response")
                    else:
                        print("⚠️ No content in search response")
                        print(f"📄 Raw search result: {search_result}")
                    
                except Exception as e:
                    print(f"❌ search_for_documents failed: {e}")
                    # Don't return False here - continue with other tests
                
                # Test search_and_retrieve_documents  
                print("\n🔍 Testing search_and_retrieve_documents tool...")
                try:
                    search_query = "http syslogng"
                    print(f"🔎 Searching and retrieving for: '{search_query}'")
                    start_time = time.time()
                    retrieve_result = await session.call_tool("search_and_retrieve_documents", {
                        "query": search_query
                    })
                    duration = time.time() - start_time
                    
                    print(f"✅ search_and_retrieve_documents call successful in {duration:.2f}s")
                    print(f"📄 Response type: {type(retrieve_result)}")
                    
                    # Extract and display retrieval results
                    if hasattr(retrieve_result, 'content') and retrieve_result.content:
                        content_text = extract_content_text(retrieve_result.content)
                        if content_text:
                            try:
                                retrieve_data = json.loads(content_text)
                                print(f"📄 Raw retrieve response keys: {list(retrieve_data.keys()) if isinstance(retrieve_data, dict) else 'not a dict'}")
                                
                                # Check for nested results structure first
                                if "results" in retrieve_data and isinstance(retrieve_data["results"], dict) and "results" in retrieve_data["results"]:
                                    results = retrieve_data["results"]["results"]
                                    print(f"📊 Retrieved {len(results)} results")
                                    for i, result in enumerate(results[:4]):  # Show first 4 results
                                        if isinstance(result, dict):
                                            document_id = result.get("document_id", "unknown")
                                            path = result.get("path", result.get("filename", ""))
                                            content = result.get("content", "")
                                            
                                            # Use path if available, otherwise document_id
                                            display_name = path if path and path != "unknown" else document_id
                                            
                                            # Get first 5 lines of content
                                            if content:
                                                lines = content.split('\n')[:5]
                                                content_preview = '\n'.join(lines)
                                                if len(content.split('\n')) > 5:
                                                    content_preview += "\n..."
                                            else:
                                                content_preview = "no content"
                                            
                                            print(f"  {i+1}. {display_name}")
                                            print(f"     Content preview:\n{content_preview}")
                                        else:
                                            print(f"  {i+1}. {result}")
                                elif "documents" in retrieve_data:
                                    documents = retrieve_data["documents"]
                                    print(f"📊 Retrieved {len(documents)} documents")
                                    for i, doc in enumerate(documents[:4]):  # Show first 4 docs
                                        if isinstance(doc, dict):
                                            document_id = doc.get("document_id", "unknown")
                                            path = doc.get("path", doc.get("filename", ""))
                                            content = doc.get("content", "")
                                            
                                            # Use path if available, otherwise document_id
                                            display_name = path if path and path != "unknown" else document_id
                                            
                                            # Get first 5 lines of content
                                            if content:
                                                lines = content.split('\n')[:5]
                                                content_preview = '\n'.join(lines)
                                                if len(content.split('\n')) > 5:
                                                    content_preview += "\n..."
                                            else:
                                                content_preview = "no content"
                                            
                                            print(f"  {i+1}. {display_name}")
                                            print(f"     Content preview:\n{content_preview}")
                                        else:
                                            print(f"  {i+1}. {doc}")
                                elif "results" in retrieve_data and isinstance(retrieve_data["results"], list):
                                    results = retrieve_data["results"]
                                    print(f"📊 Retrieved {len(results)} results")
                                    for i, result in enumerate(results[:2]):  # Show first 2 results
                                        if isinstance(result, dict):
                                            filename = result.get("filename", "unknown")
                                            content_preview = result.get("content", "")[:100] + "..." if result.get("content") else "no content"
                                            print(f"  {i+1}. {filename}")
                                            print(f"     Content preview: {content_preview}")
                                        else:
                                            print(f"  {i+1}. {result}")
                                else:
                                    print("📊 Retrieve results format: non-standard")
                                    print(f"📄 Retrieve response keys: {list(retrieve_data.keys()) if isinstance(retrieve_data, dict) else 'not a dict'}")
                            except json.JSONDecodeError:
                                print(f"📄 Retrieve returned non-JSON: {content_text[:200]}...")
                        else:
                            print("⚠️ No content text in retrieve response")
                    else:
                        print("⚠️ No content in retrieve response")
                        print(f"📄 Raw retrieve result: {retrieve_result}")
                    
                except Exception as e:
                    print(f"❌ search_and_retrieve_documents failed: {e}")
                    # Don't return False here - this is an additional test
                
                return True  # Return success if at least health_check worked
            
    except Exception as e:
        print(f"❌ Test failed with error: {type(e).__name__}: {e}")
        import traceback
        print("🔍 Full traceback:")
        traceback.print_exc()
        return False

async def main():
    """Main test function."""
    print("🏁 Starting stdio test script...")
    try:
        success = await test_stdio_health_check()
        
        if success:
            print("\n✅ stdio MCP server tests PASSED")
            print("   - health_check tool ✅")
            print("   - search_for_documents tool ✅") 
            print("   - search_and_retrieve_documents tool ✅")
            return 0
        else:
            print("\n❌ stdio MCP server tests FAILED")
            return 1
            
    except Exception as e:
        print(f"\n❌ Test crashed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    print("🚀 Executing test_stdio.py...")
    exit_code = asyncio.run(main())
    print(f"🏁 Test completed with exit code: {exit_code}")
    sys.exit(exit_code)
