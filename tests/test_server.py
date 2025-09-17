# tests/test_server_real.py
"""
Real implementation tests for server.py using actual libraries.
"""
import os
from pathlib import Path
import pydantic
import pydantic_settings
import pytest
import tempfile
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

