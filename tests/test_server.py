# tests/test_server.py
"""
Real implementation tests for server.py using actual libraries.
"""
import os
from pathlib import Path
import pydantic
import pydantic_settings
import pytest
import tempfile
import yaml
import json
from test_config import get_model_name, get_device, SAMPLE_DOCUMENTS
import sentence_transformers
import faiss


def test_setup_logger():
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


def test_server_settings_validation():
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


def test_mcp_server_initialization(test_model_name, test_device):
    """Test MCPServer initialization."""
    import server
    
    settings = server.ServerSettings(
        server_name="test-init-server",
        model_name=test_model_name,
        transformer_device=test_device
    )
    
    mcp_server = server.MCPServer(settings, device=test_device)
    
    assert mcp_server._settings == settings
    assert mcp_server._device == test_device
    assert mcp_server._engine_factory is not None
    assert mcp_server._engine_cache == {}
    assert mcp_server._is_ready == False


def test_mcp_server_load_alias_mapping(test_model_name, test_device, tmp_path):
    """Test loading alias mapping from YAML."""
    import server
    
    # Create alias YAML file
    alias_file = tmp_path / "aliases.yaml"
    alias_data = {
        "1.0.0": ["latest", "stable"],
        "0.9.0": ["beta"],
        "0.8.0": []
    }
    with open(alias_file, 'w') as f:
        yaml.dump(alias_data, f)
    
    settings = server.ServerSettings(
        server_name="test-alias-server",
        model_name=test_model_name,
        transformer_device=test_device,
        alias_file=str(alias_file)
    )
    
    mcp_server = server.MCPServer(settings)
    
    # Check alias mapping was loaded
    assert mcp_server._alias_to_version["latest"] == "1.0.0"
    assert mcp_server._alias_to_version["stable"] == "1.0.0"
    assert mcp_server._alias_to_version["beta"] == "0.9.0"
    assert mcp_server._valid_versions == {"1.0.0", "0.9.0", "0.8.0"}


def test_mcp_server_resolve_version(test_model_name, test_device, tmp_path):
    """Test version resolution with aliases."""
    import server
    
    # Create alias YAML file
    alias_file = tmp_path / "aliases.yaml"
    alias_data = {
        "1.0.0": ["latest", "stable"],
        "0.9.0": ["beta"]
    }
    with open(alias_file, 'w') as f:
        yaml.dump(alias_data, f)
    
    settings = server.ServerSettings(
        server_name="test-resolve-server",
        model_name=test_model_name,
        transformer_device=test_device,
        alias_file=str(alias_file),
        default_version="latest"
    )
    
    mcp_server = server.MCPServer(settings)
    
    # Test resolution
    assert mcp_server._resolve_version("latest") == "1.0.0"
    assert mcp_server._resolve_version("stable") == "1.0.0"
    assert mcp_server._resolve_version("beta") == "0.9.0"
    assert mcp_server._resolve_version("1.0.0") == "1.0.0"
    assert mcp_server._resolve_version(None) == "1.0.0"  # Uses default
    
    # Test unknown version
    with pytest.raises(ValueError, match="Unknown version"):
        mcp_server._resolve_version("unknown")


@pytest.mark.slow
def test_mcp_server_get_search_engine(test_model_name, test_device, test_output_dir):
    """Test getting search engine through MCPServer."""
    import server
    import index_builder_faiss
    
    # Create test index
    builder = index_builder_faiss.DocumentIndexBuilder(
        model_name=test_model_name,
        device=test_device
    )
    
    documents = [{
        "id": 0,
        "name": "test.md",
        "size": 100,
        "content": "Test content",
        "metadata": {},
        "updated_at": "2024-01-01T00:00:00"
    }]
    
    builder.build_index(documents, test_output_dir, "index-latest")
    
    settings = server.ServerSettings(
        server_name="test-engine-server",
        model_name=test_model_name,
        embedding_path=str(test_output_dir),
        transformer_device=test_device,
        default_version="latest"
    )
    
    mcp_server = server.MCPServer(settings)
    
    # Get search engine
    engine = mcp_server._get_search_engine()
    assert engine is not None
    assert engine.doc_count == 1
    
    # Should be cached
    engine2 = mcp_server._get_search_engine()
    assert engine2 is engine


@pytest.mark.slow
def test_mcp_server_create_public_server(test_model_name, test_device, test_output_dir):
    """Test creating public server with MCPServer."""
    import server
    import index_builder_faiss
    
    # Create test index
    builder = index_builder_faiss.DocumentIndexBuilder(
        model_name=test_model_name,
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
    
    builder.build_index(documents, test_output_dir, "index-latest")
    
    settings = server.ServerSettings(
        server_name="test-public-server",
        description="Test public server",
        model_name=test_model_name,
        embedding_path=str(test_output_dir),
        transformer_device=test_device
    )
    
    mcp_server = server.MCPServer(settings)
    public_server = mcp_server.create_public_server()
    
    assert public_server is not None
    assert mcp_server._is_ready == True
    
    # Test that tools are registered
    tools = public_server._tool_manager.list_tools()
    tool_names = [tool.name for tool in tools]
    
    assert "search_for_chunks" in tool_names
    assert "search_for_documents" in tool_names
    assert "health_check" in tool_names
    assert "list_versions" in tool_names


def test_server_settings_defaults():
    """Test ServerSettings default values."""
    import server
    
    settings = server.ServerSettings()
    
    assert settings.transport == "stdio"
    assert settings.host == "localhost"
    assert settings.port == 8000
    assert settings.server_name == "docs-server"
    assert settings.description == "company documentation"
    assert settings.model_name == "thenlper/gte-large"
    assert settings.embedding_path == "./embeddings"
    assert settings.embedding_name == "docs_embeddings"
    assert settings.transformer_device == "auto"
    assert settings.default_version == "latest"


def test_fast_app_settings():
    """Test FastAppSettings initialization."""
    import server
    from mcp.server.fastmcp import FastMCP
    
    settings = server.ServerSettings(
        server_name="test-fast-settings"
    )
    
    mcp_app = FastMCP(
        name="test-app",
        instructions="Test instructions"
    )
    
    fast_app_settings = server.FastAppSettings(settings, mcp_app)
    
    assert fast_app_settings.settings == settings
    assert mcp_app in fast_app_settings.servers
    assert fast_app_settings.expose_url == str(settings.server_url)


def test_mcp_server_missing_index(test_model_name, test_device, test_output_dir):
    """Test MCPServer behavior with missing index."""
    import server
    
    settings = server.ServerSettings(
        server_name="test-missing-server",
        model_name=test_model_name,
        embedding_path=str(test_output_dir),
        embedding_name="nonexistent",
        transformer_device=test_device
    )
    
    mcp_server = server.MCPServer(settings)
    
    # Should fail to create public server
    public_server = mcp_server.create_public_server()
    assert public_server is None
    assert mcp_server._initialization_error is not None


def test_mcp_server_version_caching(test_model_name, test_device, test_output_dir):
    """Test that MCPServer caches engines by version."""
    import server
    import index_builder_faiss
    
    # Create multiple version indices
    builder = index_builder_faiss.DocumentIndexBuilder(
        model_name=test_model_name,
        device=test_device
    )
    
    documents = [{
        "id": 0,
        "name": "test.md",
        "size": 100,
        "content": "Test content",
        "metadata": {},
        "updated_at": "2024-01-01T00:00:00"
    }]
    
    builder.build_index(documents, test_output_dir, "index-v1")
    builder.build_index(documents, test_output_dir, "index-v2")
    
    settings = server.ServerSettings(
        server_name="test-cache-server",
        model_name=test_model_name,
        embedding_path=str(test_output_dir),
        transformer_device=test_device
    )
    
    mcp_server = server.MCPServer(settings)
    
    # Get engines for different versions
    engine1 = mcp_server._get_search_engine("v1")
    engine2 = mcp_server._get_search_engine("v2")
    
    assert engine1 is not engine2
    assert "v1" in mcp_server._engine_cache
    assert "v2" in mcp_server._engine_cache
    
    # Getting same version again should return cached engine
    engine1_again = mcp_server._get_search_engine("v1")
    assert engine1_again is engine1


def test_constants_class():
    """Test DEFAULTS constants."""
    import server
    
    assert server.DEFAULTS.MODEL_NAME == "thenlper/gte-large"
    assert server.DEFAULTS.EMBEDDING_PATH == "./embeddings"
    assert server.DEFAULTS.DEVICE == "auto"