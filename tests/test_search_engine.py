# tests/test_search_engine.py
"""
Real implementation tests for search_engine_faiss.py using actual libraries.
"""
import numpy as np
from pathlib import Path
import pickle
import pytest
from test_config import (
    get_model_name, get_device, should_skip_slow_tests,
    SAMPLE_DOCUMENTS, TEST_QUERIES, EXPECTED_RESULTS
)
import sentence_transformers
import faiss

def create_test_index(test_output_dir, test_model_name, test_device):
    """Helper to create a real test index."""
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
    
    index_name = "test_search_index"
    builder.build_index(documents, test_output_dir, index_name)
    return index_name

def test_model_sentence_transformer(test_model_name, test_device):
    """Test real SentenceTransformer model."""
    import search_engine_faiss
    
    model = search_engine_faiss.ModelSentenceTransformer(test_model_name, test_device)
    
    # Test encoding
    texts = ["hello world", "machine learning", "python programming"]
    embeddings = model.encode(texts)
    
    assert embeddings.shape[0] == len(texts)
    assert embeddings.shape[1] == model.dimension
    assert embeddings.dtype == np.float32
    
    # Test single text encoding
    single_embedding = model.encode("test text")
    assert single_embedding.shape[0] == 1
    assert single_embedding.shape[1] == model.dimension
    
    # Test cleanup
    model.cleanup()

@pytest.mark.slow
def test_faiss_search_engine_initialize(test_model_name, test_device, test_output_dir, skip_if_slow):
    """Test FaissSearchEngine initialization with real index."""
    import search_engine_faiss
    
    # Create real test index
    index_name = create_test_index(test_output_dir, test_model_name, test_device)
    
    # Create shared sentence transformer
    sentence_transformer = search_engine_faiss.ModelSentenceTransformer(test_model_name, test_device)
    
    # Initialize search engine
    engine = search_engine_faiss.FaissSearchEngine(
        embedding_name=index_name,
        embedding_path=test_output_dir,
        model_name=test_model_name,
        device=test_device,
        sentence_transformer=sentence_transformer
    )
    
    engine.initialize()
    
    assert engine.doc_count == len(SAMPLE_DOCUMENTS)
    
    # Verify internal components
    assert engine._index is not None
    assert engine._sentence_transformer is not None
    assert engine._metadata is not None
    assert "vector_mapping" in engine._metadata
    assert "documents" in engine._metadata

def test_faiss_initialize_missing_files(test_model_name, test_device, test_output_dir):
    """Test initialization with missing files."""
    import search_engine_faiss
    
    sentence_transformer = search_engine_faiss.ModelSentenceTransformer(test_model_name, test_device)
    
    engine = search_engine_faiss.FaissSearchEngine(
        embedding_name="nonexistent",
        embedding_path=test_output_dir,
        model_name=test_model_name,
        device=test_device,
        sentence_transformer=sentence_transformer
    )
    
    with pytest.raises(FileNotFoundError):
        engine.initialize()

@pytest.mark.slow
def test_search_for_chunks(test_model_name, test_device, test_output_dir, skip_if_slow):
    """Test chunk search with real implementation."""
    import search_engine_faiss
    
    # Create and initialize search engine
    index_name = create_test_index(test_output_dir, test_model_name, test_device)
    sentence_transformer = search_engine_faiss.ModelSentenceTransformer(test_model_name, test_device)
    
    engine = search_engine_faiss.FaissSearchEngine(
        embedding_name=index_name,
        embedding_path=test_output_dir,
        model_name=test_model_name,
        device=test_device,
        sentence_transformer=sentence_transformer
    )
    engine.initialize()
    
    # Test search queries
    for query in TEST_QUERIES[:3]:  # Test first 3 queries
        chunks = engine.search_for_chunks(query, top_k=5)
        
        assert isinstance(chunks, list)
        assert len(chunks) <= 5
        
        for chunk in chunks:
            assert hasattr(chunk, 'document_id')
            assert hasattr(chunk, 'chunk_index')
            assert hasattr(chunk, 'content')
            assert hasattr(chunk, 'metadata')
            assert 'score' in chunk.metadata
            assert 0.0 <= chunk.metadata['score'] <= 1.0
            assert len(chunk.content) > 0

@pytest.mark.slow  
def test_search_for_documents(test_model_name, test_device, test_output_dir, skip_if_slow):
    """Test document search with real implementation."""
    import search_engine_faiss
    
    # Create and initialize search engine
    index_name = create_test_index(test_output_dir, test_model_name, test_device)
    sentence_transformer = search_engine_faiss.ModelSentenceTransformer(test_model_name, test_device)
    
    engine = search_engine_faiss.FaissSearchEngine(
        embedding_name=index_name,
        embedding_path=test_output_dir,
        model_name=test_model_name,
        device=test_device,
        sentence_transformer=sentence_transformer
    )
    engine.initialize()
    
    # Test specific queries with expected results
    for query, expected_docs in EXPECTED_RESULTS.items():
        documents = engine.search_for_documents(query, top_k=3)
        
        assert isinstance(documents, list)
        assert len(documents) <= 3
        
        # Verify at least one expected document is found
        found_names = [doc.name for doc in documents]
        assert any(expected in found_names for expected in expected_docs), \
            f"Query '{query}' should find one of {expected_docs}, but found {found_names}"
        
        for doc in documents:
            assert hasattr(doc, 'id')
            assert hasattr(doc, 'name') 
            assert hasattr(doc, 'content')
            assert hasattr(doc, 'metadata')
            assert len(doc.content) > 0

def test_search_empty_query(test_model_name, test_device, test_output_dir):
    """Test search with empty query."""
    import search_engine_faiss
    
    # Create minimal index for testing
    index_name = create_test_index(test_output_dir, test_model_name, test_device)
    sentence_transformer = search_engine_faiss.ModelSentenceTransformer(test_model_name, test_device)
    
    engine = search_engine_faiss.FaissSearchEngine(
        embedding_name=index_name,
        embedding_path=test_output_dir,
        model_name=test_model_name,
        device=test_device,
        sentence_transformer=sentence_transformer
    )
    engine.initialize()
    
    # Empty query should return empty results
    chunks = engine.search_for_chunks("", top_k=5)
    assert chunks == []
    
    documents = engine.search_for_documents("", top_k=5)
    assert documents == []

def test_search_before_initialization(test_model_name, test_device, test_output_dir):
    """Test search before engine is initialized."""
    import search_engine_faiss
    
    sentence_transformer = search_engine_faiss.ModelSentenceTransformer(test_model_name, test_device)
    
    engine = search_engine_faiss.FaissSearchEngine(
        embedding_name="test",
        embedding_path=test_output_dir,
        model_name=test_model_name,
        device=test_device,
        sentence_transformer=sentence_transformer
    )
    
    # Should raise error when not initialized
    with pytest.raises(ValueError, match="not initialized"):
        engine.search_for_chunks("test query")

def test_result_multiplier_calculation():
    """Test result multiplier calculation with real metadata."""
    import search_engine_faiss
    
    engine = search_engine_faiss.FaissSearchEngine("test", ".", "model", "cpu")
    
    # Test with different chunk-to-document ratios
    metadata_cases = [
        # 1 doc, 2 chunks -> ratio 2
        {
            "vector_mapping": {0: {"doc_id": 0, "chunk_index": 0}, 1: {"doc_id": 0, "chunk_index": 1}},
            "documents": {0: {"id": 0, "name": "doc1"}},
            "config": {}
        },
        # 2 docs, 10 chunks -> ratio 5
        {
            "vector_mapping": {i: {"doc_id": i//5, "chunk_index": i%5} for i in range(10)},
            "documents": {0: {"id": 0, "name": "doc1"}, 1: {"id": 1, "name": "doc2"}},
            "config": {}
        }
    ]
    
    multipliers = []
    for metadata in metadata_cases:
        multiplier = engine._calculate_document_search_result_multiplier(metadata)
        multipliers.append(multiplier)
        assert isinstance(multiplier, int)
        assert multiplier >= 2  # Minimum multiplier
    
    # Higher chunk-to-doc ratio should give higher multiplier (up to limit)
    assert multipliers[1] >= multipliers[0]

def test_normalization_logic():
    """Test query normalization logic with real FAISS index."""
    import search_engine_faiss
    
    engine = search_engine_faiss.FaissSearchEngine("test", ".", "model", "cpu")
    
    # Create real FAISS indices with different metrics
    ip_index = faiss.IndexFlatIP(128)
    l2_index = faiss.IndexFlatL2(128)
    
    # Test IP index (should normalize)
    engine._index = ip_index
    engine._metadata = {"config": {"index_type": "IndexFlatIP"}}
    assert engine._should_normalize_query() is True
    
    # Test L2 index (should not normalize)  
    engine._index = l2_index
    engine._metadata = {"config": {"index_type": "IndexFlatL2"}}
    assert engine._should_normalize_query() is False

def test_cleanup(test_model_name, test_device, test_output_dir):
    """Test cleanup with real components."""
    import search_engine_faiss
    
    # Create and initialize engine
    index_name = create_test_index(test_output_dir, test_model_name, test_device)
    sentence_transformer = search_engine_faiss.ModelSentenceTransformer(test_model_name, test_device)
    
    engine = search_engine_faiss.FaissSearchEngine(
        embedding_name=index_name,
        embedding_path=test_output_dir,
        model_name=test_model_name,
        device=test_device,
        sentence_transformer=sentence_transformer
    )
    engine.initialize()
    
    # Verify components exist
    assert engine._index is not None
    assert engine._sentence_transformer is not None
    
    # Cleanup
    engine.cleanup()
    
    # Verify cleanup
    assert engine._index is None
    assert engine._sentence_transformer is None

@pytest.mark.slow
def test_end_to_end_search_accuracy(test_model_name, test_device, test_output_dir, skip_if_slow):
    """End-to-end test of search accuracy with real data."""
    import search_engine_faiss
    
    # Create search engine with real index
    index_name = create_test_index(test_output_dir, test_model_name, test_device)
    sentence_transformer = search_engine_faiss.ModelSentenceTransformer(test_model_name, test_device)
    
    engine = search_engine_faiss.FaissSearchEngine(
        embedding_name=index_name,
        embedding_path=test_output_dir,
        model_name=test_model_name,
        device=test_device,
        sentence_transformer=sentence_transformer
    )
    engine.initialize()
    
    # Test semantic search quality
    test_cases = [
        ("Python programming language", "python_basics.md"),
        ("artificial intelligence algorithms", "machine_learning.md"),
        ("HTML CSS frontend", "web_development.html")
    ]
    
    for query, expected_doc in test_cases:
        documents = engine.search_for_documents(query, top_k=3)
        
        # Should find relevant document
        found_names = [doc.name for doc in documents]
        assert expected_doc in found_names, \
            f"Query '{query}' should find '{expected_doc}' but found {found_names}"

def test_faiss_initialize_dimension_mismatch(test_model_name, test_device, test_output_dir):
    """Test initialization with dimension mismatch using real FAISS index."""
    import search_engine_faiss
    import faiss
    
    # Create a FAISS index with wrong dimension
    wrong_dimension = 128  # Different from model dimension
    bad_index = faiss.IndexFlatIP(wrong_dimension)
    
    # Save the bad index
    index_path = test_output_dir / "bad_index.faiss"
    faiss.write_index(bad_index, str(index_path))
    
    # Create valid metadata
    metadata = {
        "vector_mapping": {0: {"doc_id": 0, "chunk_index": 0}},
        "documents": {0: {"name": "test", "content": "test"}},
        "config": {"model_name": test_model_name, "dimension": wrong_dimension}
    }
    metadata_path = test_output_dir / "bad_index.pkl"
    import pickle
    with open(metadata_path, 'wb') as f:
        pickle.dump(metadata, f)
    
    sentence_transformer = search_engine_faiss.ModelSentenceTransformer(test_model_name, test_device)
    
    # Try to initialize with mismatched dimensions
    engine = search_engine_faiss.FaissSearchEngine(
        "bad_index", test_output_dir, test_model_name, device=test_device, 
        sentence_transformer=sentence_transformer
    )
    
    with pytest.raises(ValueError, match="dimension mismatch"):
        engine.initialize()

def test_faiss_initialize_invalid_metadata_structure(test_model_name, test_device, test_output_dir):
    """Test initialization with invalid metadata structure using real implementation."""
    import search_engine_faiss
    import faiss
    import pickle
    
    # Create valid FAISS index
    model = search_engine_faiss.ModelSentenceTransformer(test_model_name, test_device)
    index = faiss.IndexFlatIP(model.dimension)
    index_path = test_output_dir / "invalid_meta.faiss"
    faiss.write_index(index, str(index_path))
    
    # Create metadata with invalid structure (missing required keys)
    invalid_metadata = {"incomplete": "structure"}
    metadata_path = test_output_dir / "invalid_meta.pkl"
    with open(metadata_path, 'wb') as f:
        pickle.dump(invalid_metadata, f)
    
    engine = search_engine_faiss.FaissSearchEngine(
        "invalid_meta", test_output_dir, test_model_name, device=test_device,
        sentence_transformer=model
    )
    
    with pytest.raises(ValueError, match="Invalid metadata structure"):
        engine.initialize()
    
    model.cleanup()

def test_get_status():
    """Test get_status method."""
    import search_engine_faiss
    
    engine = search_engine_faiss.FaissSearchEngine("test", ".", "model", "cpu")
    status = engine.get_status()
    
    assert isinstance(status, list)
    assert len(status) == 1
    assert status[0] == "Initialized"