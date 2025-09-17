# tests/test_server_app_factory_real.py
"""
Real implementation tests for FastAPI app factory using actual libraries.
"""
import pytest
from unittest.mock import AsyncMock
from test_config import get_model_name, get_device, SAMPLE_DOCUMENTS

# Skip tests if FastAPI is not available
fastapi = pytest.importorskip("fastapi", reason="FastAPI not installed")
httpx = pytest.importorskip("httpx", reason="httpx required for testing")

def create_test_index_for_app(test_output_dir, test_model_name, test_device):
    """Create a real test index for app testing."""
    import index_builder_faiss
    
    builder = index_builder_faiss.DocumentIndexBuilder(
        model_name=test_model_name,
        chunk_size=200,
        overlap=30,
        device=test_device
    )
    
    documents = []
    for i, sample in enumerate(SAMPLE_DOCUMENTS):
        doc = {
            "id": i,
            "name": sample["name"],
            "size": len(sample["content"]),
            "content": sample["content"],
            "metadata": sample["metadata"],
            "updated_at": "2024-01-01T00:00:00"
        }
        documents.append(doc)
    
    index_name = "app_test_index"
    builder.build_index(documents, test_output_dir, index_name)
    return index_name

@pytest.mark.slow
def test_fastapp_with_real_mcp_server(test_model_name, test_device, test_output_dir):
    """Test FastAPI app creation with real MCP server."""
    from fastapi.testclient import TestClient
    import server
    
    # Create test index
    index_name = create_test_index_for_app(test_output_dir, test_model_name, test_device)
    
    # Create real server settings
    server_settings = server.ServerSettings(
        transport="http",
        server_name="test-fastapi-server",
        description="Test FastAPI server with real components",
        model_name=test_model_name,
        embedding_path=str(test_output_dir),
        embedding_name=index_name,
        transformer_device=test_device
    )
    
    # Create real MCP server
    mcp_server = server.MCPServer(server_settings)
    real_mcp_app = mcp_server.create_public_server()
    
    # Create FastAPI app
    fast_app_settings = server.FastAppSettings(server_settings, real_mcp_app)
    fast_app = server.FastApp(fast_app_settings)
    app = fast_app.create_app()
    
    # Test with TestClient
    client = TestClient(app)
    
    # Test /help endpoint
    response = client.get("/help")
    assert response.status_code == 200
    
    help_content = response.text
    assert "test-fastapi-server" in help_content
    assert "search_for_chunks" in help_content
    assert "search_for_documents" in help_content
    assert "health_check" in help_content
    
    # Verify MCP route exists
    mcp_routes = [route for route in app.routes if hasattr(route, 'path') and route.path.endswith('/mcp')]
    assert len(mcp_routes) > 0, "No MCP route found"

def test_fastapp_help_endpoint_content():
    """Test help endpoint content with real FastMCP setup."""
    from fastapi.testclient import TestClient
    import server
    from mcp.server.fastmcp import FastMCP
    
    # Create minimal settings
    settings = server.ServerSettings(
        server_name="help-test-server",
        description="Server for testing help endpoint"
    )
    
    # Create real FastMCP app with actual tools
    mcp_app = FastMCP(
        name="help-test-server",
        instructions="Server for testing help endpoint",
        debug=True,
        stateless_http=True
    )
    
    # Add real tools to test
    @mcp_app.tool()
    def test_tool_1() -> str:
        """Test tool 1"""
        return "test1"
    
    @mcp_app.tool()
    def test_tool_2() -> str:
        """Test tool 2"""
        return "test2"
    
    # Create FastAPI app
    fast_app_settings = server.FastAppSettings(settings, mcp_app)
    fast_app = server.FastApp(fast_app_settings)
    app = fast_app.create_app()
    
    client = TestClient(app)
    response = client.get("/help")
    
    assert response.status_code == 200
    content = response.text
    
    # Verify help content includes server info
    assert "help-test-server" in content
    assert "Server for testing help endpoint" in content
    assert "test_tool_1" in content
    assert "test_tool_2" in content

def test_fastapp_mcp_route_mounting():
    """Test that MCP route is properly mounted."""
    from fastapi.testclient import TestClient
    import server
    from mcp.server.fastmcp import FastMCP
    
    settings = server.ServerSettings(server_name="mount-test")
    
    # Create real FastMCP app
    mcp_app = FastMCP(
        name="mount-test",
        instructions="Test mounting",
        debug=True,
        stateless_http=True
    )
    
    fast_app_settings = server.FastAppSettings(settings, mcp_app)
    fast_app = server.FastApp(fast_app_settings)
    app = fast_app.create_app()
    
    # Verify MCP route is mounted
    mcp_routes = [route for route in app.routes if hasattr(route, 'path') and '/mcp' in route.path]
    assert len(mcp_routes) > 0, "MCP route not mounted"

def test_fastapp_settings_validation():
    """Test FastAppSettings validation."""
    import server
    from mcp.server.fastmcp import FastMCP
    
    server_settings = server.ServerSettings(
        server_name="validation-test",
        description="Test settings validation"
    )
    
    # Create real FastMCP app
    mcp_app = FastMCP(
        name="validation-test",
        instructions="Test settings validation",
        debug=True,
        stateless_http=True
    )
    
    # Valid settings
    fast_app_settings = server.FastAppSettings(server_settings, mcp_app)
    assert fast_app_settings.settings == server_settings
    assert mcp_app in fast_app_settings.servers
    
    # Test FastApp creation
    fast_app = server.FastApp(fast_app_settings)
    assert fast_app.app_settings == fast_app_settings

@pytest.mark.slow
def test_fastapp_integration_with_real_search(test_model_name, test_device, test_output_dir):
    """Integration test with real search functionality through FastAPI."""
    from fastapi.testclient import TestClient
    import server
    
    # Create test index
    index_name = create_test_index_for_app(test_output_dir, test_model_name, test_device)
    
    # Create complete real setup
    server_settings = server.ServerSettings(
        transport="http",
        server_name="integration-test-server",
        model_name=test_model_name,
        embedding_path=str(test_output_dir),
        embedding_name=index_name,
        transformer_device=test_device
    )
    
    mcp_server = server.MCPServer(server_settings)
    mcp_app = mcp_server.create_public_server()
    
    fast_app_settings = server.FastAppSettings(server_settings, mcp_app)
    fast_app = server.FastApp(fast_app_settings)
    app = fast_app.create_app()
    
    client = TestClient(app)
    
    # Test that the app starts successfully
    response = client.get("/help")
    assert response.status_code == 200
    
    # Verify server info in help
    help_content = response.text
    assert "integration-test-server" in help_content
    assert "search_for_chunks" in help_content
    assert "search_for_documents" in help_content
    
    # The MCP endpoints would be tested through the MCP protocol,
    # but we can verify the FastAPI app structure is correct
    assert len(app.routes) > 1  # Should have help route + MCP mount

def test_fastapp_error_handling():
    """Test FastAPI app error handling with real FastMCP."""
    from fastapi.testclient import TestClient
    import server
    from mcp.server.fastmcp import FastMCP
    
    settings = server.ServerSettings(server_name="error-test")
    
    # Create real FastMCP app - we'll test error handling by accessing non-existent routes
    mcp_app = FastMCP(
        name="error-test",
        instructions="Error test",
        debug=True,
        stateless_http=True
    )
    
    fast_app_settings = server.FastAppSettings(settings, mcp_app)
    fast_app = server.FastApp(fast_app_settings)
    app = fast_app.create_app()
    
    client = TestClient(app)
    
    # Test that help endpoint works correctly (should not error)
    response = client.get("/help")
    assert response.status_code == 200
    
    # Test accessing non-existent route returns 404
    response = client.get("/nonexistent")
    assert response.status_code == 404
    content = response.text
    assert "Not Found" in content
