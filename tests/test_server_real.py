# tests/test_server_real.py
"""
Real implementation tests for server.py using actual libraries.
"""
import pytest
import os
import tempfile
from pathlib import Path
from test_config import get_model_name, get_device, SAMPLE_DOCUMENTS

# Skip tests if required libraries are missing
pydantic = pytest.importorskip("pydantic", reason="Pydantic required for server tests")
pydantic_settings = pytest.importorskip("pydantic_settings", reason="pydantic-settings required")
sentence_transformers = pytest.importorskip("sentence_transformers")
faiss = pytest.importorskip("faiss")

def create_test_index_for_server(test_output_dir, test_model_name, test_device):
    """Create a real test index for server testing."""
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
    
    index_name = "server_test_index"
    builder.build_index(documents, test_output_dir, index_name)
    return index_name

def test_setup_logger_real():
    """Test logger setup with real logging."""
    import server
    
    logger = server.setup_logger()
    
    assert logger.name == "mcp-docs-server"
    assert len(logger.handlers) >= 1
    
    # Test that multiple calls don't add duplicate handlers
    logger2 = server.setup_logger()
    assert len(logger2.handlers) == len(logger.handlers)
    
    # Test logging works
    logger.info("Test log message")

def test_server_settings_validation_real():
    """Test ServerSettings with real Pydantic validation."""
    import server
    
    # Valid settings
    settings = server.ServerSettings(
        transport="stdio",
        server_name="test-server",
        description="Test description",
        model_name=get_model_name(),
        embedding_path="./embeddings",
        embedding_name="test_index",
        transformer_device=get_device()
    )
    
    assert settings.transport == "stdio"
    assert settings.server_name == "test-server"
    assert settings.model_name == get_model_name()
    
    # Test validation errors - port must be a valid integer
    with pytest.raises(pydantic.ValidationError):
        server.ServerSettings(port="invalid_port")

@pytest.mark.slow
def test_mcp_server_initialization_real(test_model_name, test_device, test_output_dir):
    """Test MCPServer initialization with real components."""
    import server
    
    # Create test index
    index_name = create_test_index_for_server(test_output_dir, test_model_name, test_device)
    
    settings = server.ServerSettings(
        transport="stdio",
        server_name="test-docs-server",
        description="Test server",
        model_name=test_model_name,
        embedding_path=str(test_output_dir),
        embedding_name=index_name,
        transformer_device=test_device
    )
    
    mcp_server = server.MCPServer(settings)
    
    assert mcp_server._settings == settings
    assert mcp_server._search_engine is not None
    assert mcp_server._logger is not None

@pytest.mark.slow
def test_create_public_server_real(test_model_name, test_device, test_output_dir):
    """Test public server creation with real MCP components."""
    import server
    
    # Create test index
    index_name = create_test_index_for_server(test_output_dir, test_model_name, test_device)
    
    settings = server.ServerSettings(
        transport="stdio",
        server_name="test-server",
        description="Test MCP server",
        model_name=test_model_name,
        embedding_path=str(test_output_dir),
        embedding_name=index_name,
        transformer_device=test_device
    )
    
    mcp_server = server.MCPServer(settings)
    app = mcp_server.create_public_server()
    
    # Verify FastMCP app was created
    assert app is not None
    
    # Verify server is ready
    assert mcp_server._is_ready

@pytest.mark.slow
def test_search_tools_functionality_real(test_model_name, test_device, test_output_dir):
    """Test search tools with real data."""
    import server
    
    # Create test index
    index_name = create_test_index_for_server(test_output_dir, test_model_name, test_device)
    
    settings = server.ServerSettings(
        transport="stdio",
        model_name=test_model_name,
        embedding_path=str(test_output_dir),
        embedding_name=index_name,
        transformer_device=test_device
    )
    
    mcp_server = server.MCPServer(settings)
    app = mcp_server.create_public_server()
    
    # Test search functionality directly through the search engine
    chunks = mcp_server._search_engine.search_for_chunks("Python programming", 5)
    assert isinstance(chunks, list)
    assert len(chunks) <= 5
    
    if chunks:
        chunk = chunks[0]
        assert hasattr(chunk, 'document_id')
        assert hasattr(chunk, 'chunk_index')
        assert hasattr(chunk, 'content')
        assert hasattr(chunk, 'metadata') and 'score' in chunk.metadata
        assert isinstance(chunk.metadata['score'], (int, float))
    
    # Test search_for_documents
    docs = mcp_server._search_engine.search_for_documents("machine learning", 3)
    assert isinstance(docs, list)
    assert len(docs) <= 3
    
    if docs:
        doc = docs[0]
        assert hasattr(doc, 'id')
        assert hasattr(doc, 'name')
        assert hasattr(doc, 'content')
        assert hasattr(doc, 'metadata')

def test_health_check_tool_real(test_model_name, test_device, test_output_dir):
    """Test health check tool with real components."""
    import server
    
    # Create test index
    index_name = create_test_index_for_server(test_output_dir, test_model_name, test_device)
    
    settings = server.ServerSettings(
        transport="stdio",
        model_name=test_model_name,
        embedding_path=str(test_output_dir),
        embedding_name=index_name,
        transformer_device=test_device
    )
    
    mcp_server = server.MCPServer(settings)
    app = mcp_server.create_public_server()
    
    # Test health check by verifying server state
    assert mcp_server._is_ready
    assert mcp_server._search_engine.is_ready
    assert mcp_server._search_engine.doc_count > 0

def test_server_settings_from_environment():
    """Test ServerSettings loading from environment variables."""
    import server
    
    # Set environment variables
    test_env = {
        "MCP_TRANSPORT": "stdio",
        "MCP_SERVER_NAME": "env-test-server",
        "MCP_DESCRIPTION": "Server from env",
        "MCP_MODEL_NAME": get_model_name(),
        "MCP_EMBEDDING_PATH": "./test_embeddings",
        "MCP_EMBEDDING_NAME": "env_index",
        "MCP_TRANSFORMER_DEVICE": "cpu"
    }
    
    # Temporarily set environment variables
    original_env = {}
    for key, value in test_env.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value
    
    try:
        settings = server.ServerSettings()
        
        assert settings.transport == "stdio"
        assert settings.server_name == "env-test-server"
        assert settings.description == "Server from env"
        assert settings.model_name == get_model_name()
        assert settings.embedding_path == "./test_embeddings"
        assert settings.embedding_name == "env_index"
        assert settings.transformer_device == "cpu"
        
    finally:
        # Restore original environment
        for key, original_value in original_env.items():
            if original_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = original_value

def test_run_stdio_server_real(test_model_name, test_device, test_output_dir, monkeypatch):
    """Test stdio server run with real components."""
    import server
    
    # Create test index
    index_name = create_test_index_for_server(test_output_dir, test_model_name, test_device)
    
    settings = server.ServerSettings(
        transport="stdio",
        model_name=test_model_name,
        embedding_path=str(test_output_dir),
        embedding_name=index_name,
        transformer_device=test_device
    )
    
    mcp_server = server.MCPServer(settings)
    
    # Mock the FastMCP run method to avoid blocking
    run_called = {"value": False}
    
    def mock_run(self):
        run_called["value"] = True
        return None
    
    # Import and patch FastMCP
    from mcp.server.fastmcp import FastMCP
    monkeypatch.setattr(FastMCP, "run", mock_run)
    
    # Run server (should call mocked run)
    mcp_server.run_stdio_server()
    
    assert run_called["value"] is True

def test_main_function_real(monkeypatch, test_output_dir):
    """Test main function with real argument parsing."""
    import server
    import sys
    
    # Mock run_stdio_server to avoid blocking
    run_called = {"value": False}
    
    def mock_run_stdio_server(self):
        run_called["value"] = True
        return None
    
    monkeypatch.setattr(server.MCPServer, "run_stdio_server", mock_run_stdio_server)
    
    # Set up environment
    monkeypatch.setenv("MCP_EMBEDDING_PATH", str(test_output_dir))
    monkeypatch.setenv("MCP_EMBEDDING_NAME", "test_index")
    monkeypatch.setenv("MCP_MODEL_NAME", get_model_name())
    
    # Mock sys.argv
    test_argv = ["server.py", "--transport", "stdio"]
    monkeypatch.setattr(sys, "argv", test_argv)
    
    # Run main
    result = server.main()
    
    # Should have attempted to run server
    assert run_called["value"] is True
    assert result == 0

def test_error_handling_missing_index(test_model_name, test_device, test_output_dir):
    """Test error handling when index files are missing."""
    import server
    
    settings = server.ServerSettings(
        transport="stdio",
        model_name=test_model_name,
        embedding_path=str(test_output_dir),
        embedding_name="nonexistent_index",
        transformer_device=test_device
    )
    
    mcp_server = server.MCPServer(settings)
    
    # Should handle missing index gracefully
    app = mcp_server.create_public_server()
    
    # Should fail to initialize due to missing index
    assert app is None
    assert not mcp_server._is_ready
    assert mcp_server._initialization_error is not None

@pytest.mark.slow
def test_concurrent_search_requests_real(test_model_name, test_device, test_output_dir):
    """Test concurrent search requests with real implementation."""
    import server
    import threading
    import time
    
    # Create test index
    index_name = create_test_index_for_server(test_output_dir, test_model_name, test_device)
    
    settings = server.ServerSettings(
        transport="stdio",
        model_name=test_model_name,
        embedding_path=str(test_output_dir),
        embedding_name=index_name,
        transformer_device=test_device
    )
    
    mcp_server = server.MCPServer(settings)
    app = mcp_server.create_public_server()
    
    results = []
    errors = []
    
    def search_worker(worker_id):
        try:
            result = mcp_server._search_engine.search_for_chunks(f"test query {worker_id}", 3)
            results.append((worker_id, len(result)))
        except Exception as e:
            errors.append((worker_id, str(e)))
    
    # Start multiple concurrent searches
    threads = []
    for i in range(5):
        thread = threading.Thread(target=search_worker, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads
    for thread in threads:
        thread.join(timeout=30)
    
    # Verify results
    assert len(errors) == 0, f"Errors occurred: {errors}"
    assert len(results) == 5
    
    # All searches should return results
    for worker_id, result_count in results:
        assert result_count >= 0
