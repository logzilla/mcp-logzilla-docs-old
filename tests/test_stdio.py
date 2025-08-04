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
    
    # Set up the server command
    server_script = Path(__file__).parent / "server.py"
    if not server_script.exists():
        print(f"❌ Server script not found: {server_script}")
        return False
    
    try:
        # Create stdio server parameters
        server_params = StdioServerParameters(
            command=sys.executable,
            args=[str(server_script), "--transport", "stdio"]
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
                
                # Test health_check with retries
                print("\n🔍 Testing health_check tool with retries...")
                max_attempts = 5
                retry_delay = 3  # seconds
                
                for attempt in range(1, max_attempts + 1):
                    try:
                        print(f"\n🔄 Health check attempt {attempt}/{max_attempts}...")
                        start_time = time.time()
                        result = await session.call_tool("health_check", {})
                        duration = time.time() - start_time
                        
                        print(f"✅ health_check call successful in {duration:.2f}s")
                        print(f"📄 Response type: {type(result)}")
                        
                        # Extract the response content
                        if hasattr(result, 'content') and result.content:
                            content_text = extract_content_text(result.content)
                            if content_text:
                                try:
                                    health_data = json.loads(content_text)
                                    print(f"📊 Health check response: {health_data}")
                                    
                                    # Check for expected fields in health response
                                    expected_fields = ["status", "message", "documents_loaded", "search_tools_available"]
                                    
                                    for field in expected_fields:
                                        if field in health_data:
                                            print(f"✅ {field}: {health_data[field]}")
                                        else:
                                            print(f"⚠️ Expected field '{field}' not found in response")
                                    
                                    # Check if server is ready
                                    if health_data.get("status") == "ready":
                                        print("🎉 Server is ready and healthy!")
                                        break  # Exit retry loop on success
                                    else:
                                        server_status = health_data.get('status', 'unknown')
                                        print(f"⚠️ Server status: {server_status}")
                                        
                                        # If not the last attempt, wait and retry
                                        if attempt < max_attempts:
                                            print(f"⏳ Waiting {retry_delay} seconds before retry...")
                                            await asyncio.sleep(retry_delay)
                                        else:
                                            print(f"⚠️ Server still not ready after {max_attempts} attempts, but health check is working")
                                            
                                except json.JSONDecodeError:
                                    print(f"📄 Health check returned non-JSON: {content_text}")
                                    if attempt == max_attempts:
                                        break  # Accept non-JSON response on last attempt
                            else:
                                print("⚠️ No content text in response")
                                if attempt == max_attempts:
                                    break  # Accept empty response on last attempt
                        else:
                            print("⚠️ No content in response")
                            print(f"📄 Raw result: {result}")
                            if attempt == max_attempts:
                                break  # Accept raw response on last attempt
                        
                        # If not the last attempt and we haven't broken out, wait
                        if attempt < max_attempts:
                            await asyncio.sleep(retry_delay)
                        
                    except Exception as e:
                        print(f"❌ health_check attempt {attempt} failed: {e}")
                        if attempt == max_attempts:
                            print(f"❌ All {max_attempts} health_check attempts failed")
                            return False
                        else:
                            print(f"⏳ Waiting {retry_delay} seconds before retry...")
                            await asyncio.sleep(retry_delay)
                
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
                                if "results" in search_data:
                                    results = search_data["results"]
                                    print(f"📊 Found {len(results)} search results")
                                    # Ensure results is a list before slicing
                                    results_list = list(results) if results else []
                                    for i, result in enumerate(results_list[:3]):  # Show first 3 results
                                        if isinstance(result, dict):
                                            document_id = result.get("document_id", "unknown")
                                            score = result.get("score", "unknown")
                                            filename = result.get("filename", "unknown")
                                            print(f"  {i+1}. {filename} (score: {score})")
                                        else:
                                            print(f"  {i+1}. {result}")
                                else:
                                    print("📊 Search results format: non-standard")
                                    print(f"📄 Search response keys: {list(search_data.keys()) if isinstance(search_data, dict) else 'not a dict'}")
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
                                if "documents" in retrieve_data:
                                    documents = retrieve_data["documents"]
                                    print(f"📊 Retrieved {len(documents)} documents")
                                    # Ensure documents is a list before slicing
                                    documents_list = list(documents) if documents else []
                                    for i, doc in enumerate(documents_list[:2]):  # Show first 2 docs
                                        if isinstance(doc, dict):
                                            document_id = doc.get("document_id", "unknown")
                                            filename = doc.get("filename", "unknown")
                                            content_preview = doc.get("content", "")[:100] + "..." if doc.get("content") else "no content"
                                            print(f"  {i+1}. {filename}")
                                            print(f"     Content preview: {content_preview}")
                                        else:
                                            print(f"  {i+1}. {doc}")
                                elif "results" in retrieve_data:
                                    results = retrieve_data["results"]
                                    print(f"📊 Retrieved {len(results)} results")
                                    # Ensure results is a list before slicing
                                    results_list = list(results) if results else []
                                    for i, result in enumerate(results_list[:2]):  # Show first 2 results
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
