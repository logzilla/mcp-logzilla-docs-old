# tests/test_integration_real.py
"""
Integration tests using real libraries and end-to-end workflows.
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from test_config import (
    get_model_name, get_device, SAMPLE_DOCUMENTS, TEST_QUERIES, EXPECTED_RESULTS
)

# Skip all tests if libraries are missing
sentence_transformers = pytest.importorskip("sentence_transformers")
faiss = pytest.importorskip("faiss")
pydantic = pytest.importorskip("pydantic")

@pytest.mark.slow
def test_full_pipeline_real(test_model_name, test_device):
    """Test complete pipeline from document loading to search with real libraries."""
    import index_builder_faiss
    import search_engine_faiss
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Step 1: Create documents
        docs_dir = temp_path / "documents"
        docs_dir.mkdir()
        
        for sample in SAMPLE_DOCUMENTS:
            doc_path = docs_dir / sample["name"]
            doc_path.write_text(sample["content"], encoding="utf-8")
        
        # Step 2: Build index
        builder = index_builder_faiss.DocumentIndexBuilder(
            model_name=test_model_name,
            chunk_size=300,
            overlap=50,
            device=test_device
        )
        
        documents = builder.load_documents_from_directory(docs_dir)
        assert len(documents) == len(SAMPLE_DOCUMENTS)
        
        embeddings_dir = temp_path / "embeddings"
        embeddings_dir.mkdir()
        
        index_name = "integration_test"
        builder.build_index(documents, embeddings_dir, index_name)
        
        # Verify index files exist
        assert (embeddings_dir / f"{index_name}.faiss").exists()
        assert (embeddings_dir / f"{index_name}.pkl").exists()
        
        # Step 3: Initialize search engine
        engine = search_engine_faiss.FaissSearchEngine(
            embedding_name=index_name,
            embedding_path=embeddings_dir,
            model_name=test_model_name,
            device=test_device
        )
        
        engine.initialize()
        assert engine.is_ready
        assert engine.doc_count == len(SAMPLE_DOCUMENTS)
        
        # Step 4: Test searches
        for query in TEST_QUERIES:
            # Test chunk search
            chunks = engine.search_for_chunks(query, top_k=5)
            assert isinstance(chunks, list)
            assert len(chunks) <= 5
            
            for chunk in chunks:
                assert hasattr(chunk, 'content')
                assert hasattr(chunk, 'metadata')
                assert 'score' in chunk.metadata
                assert 0.0 <= chunk.metadata['score'] <= 1.0
            
            # Test document search
            docs = engine.search_for_documents(query, top_k=3)
            assert isinstance(docs, list)
            assert len(docs) <= 3
            
            for doc in docs:
                assert hasattr(doc, 'name')
                assert hasattr(doc, 'content')
                assert len(doc.content) > 0
        
        # Step 5: Test semantic accuracy
        for query, expected_docs in EXPECTED_RESULTS.items():
            results = engine.search_for_documents(query, top_k=5)
            result_names = [doc.name for doc in results]
            
            # At least one expected document should be found
            found_expected = any(expected in result_names for expected in expected_docs)
            assert found_expected, f"Query '{query}' should find one of {expected_docs}, got {result_names}"
        
        # Step 6: Cleanup
        engine.cleanup()

@pytest.mark.slow
def test_server_integration_real(test_model_name, test_device):
    """Test server integration with real components."""
    import server
    import index_builder_faiss
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test index
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
        
        embeddings_dir = temp_path / "embeddings"
        embeddings_dir.mkdir()
        
        index_name = "server_integration"
        builder.build_index(documents, embeddings_dir, index_name)
        
        # Create server
        settings = server.ServerSettings(
            transport="stdio",
            server_name="integration-test-server",
            description="Integration test server",
            model_name=test_model_name,
            embedding_path=str(embeddings_dir),
            embedding_name=index_name,
            transformer_device=test_device
        )
        
        mcp_server = server.MCPServer(settings)
        app = mcp_server.create_public_server()
        
        # Test server functionality
        assert mcp_server._is_ready
        assert mcp_server._search_engine.is_ready
        assert mcp_server._search_engine.doc_count == len(SAMPLE_DOCUMENTS)
        
        # Test search functionality directly
        chunks = mcp_server._search_engine.search_for_chunks("Python programming", 3)
        assert len(chunks) <= 3
        
        docs = mcp_server._search_engine.search_for_documents("machine learning", 2)
        assert len(docs) <= 2

def test_error_recovery_real(test_model_name, test_device):
    """Test error recovery with real components."""
    import search_engine_faiss
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Test missing index files
        engine = search_engine_faiss.FaissSearchEngine(
            embedding_name="nonexistent",
            embedding_path=temp_path,
            model_name=test_model_name,
            device=test_device
        )
        
        with pytest.raises(FileNotFoundError):
            engine.initialize()
        
        # Engine should remain in safe state
        assert not engine.is_ready
        assert engine.doc_count == 0
        
        # Cleanup should be safe even after failed initialization
        engine.cleanup()

def test_concurrent_access_real(test_model_name, test_device):
    """Test concurrent access with real components."""
    import threading
    import time
    import index_builder_faiss
    import search_engine_faiss
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test index
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
        
        embeddings_dir = temp_path / "embeddings"
        embeddings_dir.mkdir()
        
        index_name = "concurrent_test"
        builder.build_index(documents, embeddings_dir, index_name)
        
        # Create search engine
        engine = search_engine_faiss.FaissSearchEngine(
            embedding_name=index_name,
            embedding_path=embeddings_dir,
            model_name=test_model_name,
            device=test_device
        )
        engine.initialize()
        
        results = []
        errors = []
        
        def search_worker(worker_id):
            try:
                for i in range(3):
                    chunks = engine.search_for_chunks(f"test query {worker_id} {i}", 2)
                    results.append((worker_id, i, len(chunks)))
                    time.sleep(0.1)  # Small delay
            except Exception as e:
                errors.append((worker_id, str(e)))
        
        # Start multiple workers
        threads = []
        for worker_id in range(3):
            thread = threading.Thread(target=search_worker, args=(worker_id,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=30)
        
        # Verify results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 9  # 3 workers * 3 searches each
        
        engine.cleanup()

def test_memory_usage_real(test_model_name, test_device):
    """Test memory usage with real components."""
    import psutil
    import os
    import index_builder_faiss
    import search_engine_faiss
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create and use search engine
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
        
        embeddings_dir = temp_path / "embeddings"
        embeddings_dir.mkdir()
        
        index_name = "memory_test"
        builder.build_index(documents, embeddings_dir, index_name)
        
        engine = search_engine_faiss.FaissSearchEngine(
            embedding_name=index_name,
            embedding_path=embeddings_dir,
            model_name=test_model_name,
            device=test_device
        )
        engine.initialize()
        
        # Perform searches
        for _ in range(10):
            engine.search_for_chunks("test query", 5)
            engine.search_for_documents("test query", 3)
        
        peak_memory = process.memory_info().rss
        
        # Cleanup
        engine.cleanup()
        del engine
        del builder
        
        final_memory = process.memory_info().rss
        
        # Memory should not grow excessively
        memory_growth = peak_memory - initial_memory
        memory_after_cleanup = final_memory - initial_memory
        
        # Allow reasonable memory growth (100MB) but ensure cleanup works
        assert memory_growth < 100 * 1024 * 1024, f"Memory grew by {memory_growth / 1024 / 1024:.1f}MB"
        
        # Memory should be mostly freed after cleanup (allow some tolerance for test environment)
        cleanup_ratio = memory_after_cleanup / max(memory_growth, 1)
        assert cleanup_ratio < 0.6, f"Memory not properly cleaned up: {cleanup_ratio:.2f}"
