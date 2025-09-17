# tests/conftest.py
"""
Real library configuration for tests - replaces stubs with actual implementations.
"""
import pytest
import sys
import os
from pathlib import Path
from test_config import (
    ensure_test_directories, cleanup_test_directories, 
    get_model_name, get_device, should_skip_slow_tests,
    TEST_DATA_DIR, TEST_EMBEDDINGS_DIR, TEST_OUTPUT_DIR,
    SAMPLE_DOCUMENTS
)

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment with real directories and data."""
    ensure_test_directories()
    
    # Create sample test documents
    for doc in SAMPLE_DOCUMENTS:
        doc_path = TEST_DATA_DIR / doc["name"]
        doc_path.write_text(doc["content"], encoding="utf-8")
    
    yield
    
    # Cleanup after all tests
    if not os.getenv("KEEP_TEST_DATA"):
        cleanup_test_directories()

@pytest.fixture
def test_model_name():
    """Get the model name for testing."""
    return get_model_name()

@pytest.fixture  
def test_device():
    """Get the device for testing."""
    return get_device()

@pytest.fixture
def test_data_dir():
    """Get the test data directory."""
    return TEST_DATA_DIR

@pytest.fixture
def test_embeddings_dir():
    """Get the test embeddings directory."""
    return TEST_EMBEDDINGS_DIR

@pytest.fixture
def test_output_dir():
    """Get the test output directory."""
    return TEST_OUTPUT_DIR

@pytest.fixture
def sample_documents():
    """Get sample documents for testing."""
    return SAMPLE_DOCUMENTS

@pytest.fixture
def skip_if_slow():
    """No-op; do not skip slow tests."""
    return None

# Import utilities for tests
def import_fresh(module_name: str):
    """Import a module fresh, removing it from cache first."""
    if module_name in sys.modules:
        del sys.modules[module_name]
    return __import__(module_name, fromlist=["*"])

# Make import_fresh available globally
import builtins
builtins.import_fresh = import_fresh
