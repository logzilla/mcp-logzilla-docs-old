# tests/test_search_engine_factory.py
"""
Tests for SearchEngineFactory abstract base class and FaissSearchEngineFactory implementation.
"""
import pytest
from pathlib import Path
from test_config import (
    get_model_name, get_device, SAMPLE_DOCUMENTS
)


def create_test_index_for_factory(test_output_dir, test_model_name, test_device, version="v1.0"):
    """Helper to create a test index for factory testing."""
    import index_builder_faiss
    
    builder = index_builder_faiss.DocumentIndexBuilder(
        model_name=test_model_name,
        chunk_size=200,
        overlap=30,
        device=test_device
    )
    
    # Prepare documents
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
    
    index_name = f"index-{version}"
    builder.build_index(documents, test_output_dir, index_name)
    return index_name


def test_search_engine_factory_abstract_methods():
    """Test that SearchEngineFactory is properly abstract."""
    from models import SearchEngineFactory
    
    # Should not be able to instantiate abstract class
    with pytest.raises(TypeError):
        SearchEngineFactory()


def test_faiss_search_engine_factory_initialization(test_model_name, test_device, test_output_dir):
    """Test FaissSearchEngineFactory initialization."""
    from search_engine_faiss import FaissSearchEngineFactory
    
    factory = FaissSearchEngineFactory(
        model_name=test_model_name,
        device=test_device,
        embedding_dir=test_output_dir,
        embedding_prefix="test-"
    )
    
    assert factory._model_name == test_model_name
    assert factory._device == test_device
    assert factory._embedding_dir == Path(test_output_dir)
    assert factory._embedding_prefix == "test-"
    assert factory._shared_transformer is None  # Lazy initialization


def test_faiss_search_engine_factory_lazy_transformer_creation(test_model_name, test_device, test_output_dir):
    """Test lazy creation of shared transformer."""
    from search_engine_faiss import FaissSearchEngineFactory
    
    factory = FaissSearchEngineFactory(
        model_name=test_model_name,
        device=test_device,
        embedding_dir=test_output_dir
    )
    
    # Initially no transformer
    assert factory._shared_transformer is None
    
    # First access creates transformer
    transformer1 = factory._get_sentence_transformer()
    assert transformer1 is not None
    assert factory._shared_transformer is not None
    
    # Second access returns same instance
    transformer2 = factory._get_sentence_transformer()
    assert transformer1 is transformer2


def test_faiss_search_engine_factory_transformer_property(test_model_name, test_device, test_output_dir):
    """Test transformer property access."""
    from search_engine_faiss import FaissSearchEngineFactory
    
    factory = FaissSearchEngineFactory(
        model_name=test_model_name,
        device=test_device,
        embedding_dir=test_output_dir
    )
    
    # Access via property
    transformer = factory.transformer
    assert transformer is not None
    assert transformer.model_name == test_model_name


@pytest.mark.slow
def test_faiss_search_engine_factory_get_engine(test_model_name, test_device, test_output_dir, skip_if_slow):
    """Test engine creation via factory."""
    from search_engine_faiss import FaissSearchEngineFactory
    
    # Create test index first
    version = "test-version"
    create_test_index_for_factory(test_output_dir, test_model_name, test_device, version)
    
    factory = FaissSearchEngineFactory(
        model_name=test_model_name,
        device=test_device,
        embedding_dir=test_output_dir,
        embedding_prefix="index-"
    )
    
    # Get engine for version
    engine = factory.get_engine(version)
    
    assert engine is not None
    assert hasattr(engine, '_sentence_transformer')
    assert engine._sentence_transformer is factory._shared_transformer
    assert engine.doc_count == len(SAMPLE_DOCUMENTS)


def test_faiss_search_engine_factory_get_engine_missing_version(test_model_name, test_device, test_output_dir):
    """Test engine creation with missing version."""
    from search_engine_faiss import FaissSearchEngineFactory
    
    factory = FaissSearchEngineFactory(
        model_name=test_model_name,
        device=test_device,
        embedding_dir=test_output_dir,
        embedding_prefix="index-"
    )
    
    # Should raise error for missing version
    with pytest.raises(FileNotFoundError):
        factory.get_engine("nonexistent-version")


@pytest.mark.slow
def test_faiss_search_engine_factory_shared_transformer(test_model_name, test_device, test_output_dir, skip_if_slow):
    """Test that multiple engines share the same transformer."""
    from search_engine_faiss import FaissSearchEngineFactory
    
    # Create test indices for multiple versions
    version1 = "v1.0"
    version2 = "v2.0"
    create_test_index_for_factory(test_output_dir, test_model_name, test_device, version1)
    create_test_index_for_factory(test_output_dir, test_model_name, test_device, version2)
    
    factory = FaissSearchEngineFactory(
        model_name=test_model_name,
        device=test_device,
        embedding_dir=test_output_dir,
        embedding_prefix="index-"
    )
    
    # Get engines for different versions
    engine1 = factory.get_engine(version1)
    engine2 = factory.get_engine(version2)
    
    # Should share the same transformer instance
    assert engine1._sentence_transformer is engine2._sentence_transformer
    assert engine1._sentence_transformer is factory._shared_transformer


def test_search_engine_factory_interface_compliance():
    """Test that FaissSearchEngineFactory implements required interface."""
    from search_engine_faiss import FaissSearchEngineFactory
    from models import SearchEngineFactory
    
    # Should be a subclass
    assert issubclass(FaissSearchEngineFactory, SearchEngineFactory)
    
    factory = FaissSearchEngineFactory()
    
    # Should have required methods
    assert hasattr(factory, 'get_engine')
    assert callable(factory.get_engine)
    
    # Note: clear_cache is not implemented in the actual class,
    # but required by the abstract interface. This test documents that issue.
    # The implementation should add this method.


def test_faiss_search_engine_factory_error_handling(test_model_name, test_device, test_output_dir):
    """Test factory error handling."""
    from search_engine_faiss import FaissSearchEngineFactory
    
    factory = FaissSearchEngineFactory(
        model_name=test_model_name,
        device=test_device,
        embedding_dir="/nonexistent/path",  # Invalid path
        embedding_prefix="index-"
    )
    
    # Should handle missing directory gracefully
    with pytest.raises((FileNotFoundError, ValueError)):
        factory.get_engine("any-version")


def test_faiss_search_engine_factory_with_different_prefixes(test_model_name, test_device, test_output_dir):
    """Test factory with different embedding prefixes."""
    from search_engine_faiss import FaissSearchEngineFactory
    
    # Create index with custom prefix
    import index_builder_faiss
    builder = index_builder_faiss.DocumentIndexBuilder(
        model_name=test_model_name,
        device=test_device
    )
    
    documents = [{
        "id": 0,
        "name": "test.md",
        "size": 100,
        "content": "Test content for prefix testing",
        "metadata": {},
        "updated_at": "2024-01-01T00:00:00"
    }]
    
    # Build with custom prefix
    custom_prefix = "custom-prefix-"
    index_name = "test-version"
    builder.build_index(documents, test_output_dir, index_name, file_prefix=custom_prefix)
    
    # Factory should use same prefix
    factory = FaissSearchEngineFactory(
        model_name=test_model_name,
        device=test_device,
        embedding_dir=test_output_dir,
        embedding_prefix=custom_prefix
    )
    
    # Should find the index with custom prefix
    engine = factory.get_engine(index_name)
    assert engine is not None


def test_faiss_search_engine_factory_default_params():
    """Test factory with default parameters."""
    from search_engine_faiss import FaissSearchEngineFactory
    
    # Test with default initialization
    factory = FaissSearchEngineFactory()
    
    # Should have reasonable defaults
    assert factory._model_name == "thenlper/gte-large"
    assert factory._device == "auto"
    assert factory._embedding_dir == Path("embeddings")
    assert factory._embedding_prefix == "index-"


def test_faiss_search_engine_factory_multiple_calls_same_version(test_model_name, test_device, test_output_dir):
    """Test that calling get_engine multiple times for same version works."""
    from search_engine_faiss import FaissSearchEngineFactory
    
    # Create test index
    version = "test-multi"
    create_test_index_for_factory(test_output_dir, test_model_name, test_device, version)
    
    factory = FaissSearchEngineFactory(
        model_name=test_model_name,
        device=test_device,
        embedding_dir=test_output_dir,
        embedding_prefix="index-"
    )
    
    # Get same engine multiple times
    engine1 = factory.get_engine(version)
    engine2 = factory.get_engine(version)
    
    # Should create new engine instances (no caching in factory)
    # but share the same transformer
    assert engine1 is not engine2  # Different engine instances
    assert engine1._sentence_transformer is engine2._sentence_transformer  # Same transformer


def test_faiss_search_engine_factory_cleanup_not_implemented():
    """Test that clear_cache is not implemented (documenting missing method)."""
    from search_engine_faiss import FaissSearchEngineFactory
    
    factory = FaissSearchEngineFactory()
    
    # clear_cache is required by abstract base but not implemented
    # This test documents that the method is missing
    assert not hasattr(factory, 'clear_cache')
    
    # If it were implemented, it should work like this:
    # factory.clear_cache()
    # assert factory._shared_transformer is None