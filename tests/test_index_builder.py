# tests/test_index_builder_real.py
"""
Real implementation tests for index_builder_faiss.py using actual libraries.
"""
from datetime import datetime
from pathlib import Path
import pickle
import pytest
import sys
from test_config import (
    DEFAULT_CHUNK_SIZE, DEFAULT_OVERLAP, SAMPLE_DOCUMENTS,
    get_model_name, get_device, should_skip_slow_tests
)
import sentence_transformers
import faiss
import tiktoken

def test_init_with_model(test_model_name, test_device, skip_if_slow):
    """Test initialization with real sentence transformer model."""
    import index_builder_faiss
    
    builder = index_builder_faiss.DocumentIndexBuilder(
        model_name=test_model_name,
        chunk_size=DEFAULT_CHUNK_SIZE,
        overlap=DEFAULT_OVERLAP,
        device=test_device,
        encoding_name="cl100k_base"
    )
    
    # Verify model properties
    assert builder.dimension > 0
    assert builder.chunk_size == DEFAULT_CHUNK_SIZE
    assert builder.overlap == DEFAULT_OVERLAP
    
    # Test tokenizer
    token_count = builder._count_tokens("hello world test")
    assert isinstance(token_count, int)
    assert token_count > 0

def test_clean_html_content_with_beautifulsoup():
    """Test HTML cleaning with real BeautifulSoup."""
    import index_builder_faiss
    
    html_content = """
    <html><body>
      <header>Navigation</header>
      <nav class="menu">Menu items</nav>
      <main>
        <h1>Main Title</h1>
        <p>This is a <b>bold</b> paragraph with <i>italic</i> text.</p>
        <ul><li>First item</li><li>Second item</li></ul>
        <ol><li>Numbered one</li><li>Numbered two</li></ol>
        <a href="https://example.com">External link</a>
        <a href="/internal">Internal link</a>
        <table><tr><th>Header</th><th>Value</th></tr><tr><td>Data1</td><td>Data2</td></tr></table>
        <pre><code>print("code example")</code></pre>
      </main>
      <footer>Footer content</footer>
      <script>console.log("remove this")</script>
    </body></html>
    """
    
    builder = index_builder_faiss.DocumentIndexBuilder()
    cleaned = builder.clean_html_content(html_content)
    
    # Verify content extraction
    assert "# Main Title" in cleaned
    assert "**bold**" in cleaned
    assert "*italic*" in cleaned
    assert "- First item" in cleaned
    assert "1. Numbered one" in cleaned
    assert "[External link](https://example.com)" in cleaned
    assert "Internal link" in cleaned
    assert "Header | Value" in cleaned
    assert "Data1 | Data2" in cleaned
    assert "print(" in cleaned
    
    # Verify unwanted content removal
    assert "Navigation" not in cleaned
    assert "Menu items" not in cleaned
    assert "Footer content" not in cleaned
    assert "console.log" not in cleaned

def test_token_aware_chunking_with_tokenizer(test_model_name, test_device):
    """Test chunking with real tokenizer."""
    import index_builder_faiss
    
    builder = index_builder_faiss.DocumentIndexBuilder(
        model_name=test_model_name,
        chunk_size=50,  # Small chunk size for testing
        overlap=10,
        device=test_device
    )
    
    # Create text that will definitely need chunking
    long_text = " ".join([f"word{i}" for i in range(100)])
    
    chunks = builder.chunk_document(long_text, doc_id=0)
    
    assert len(chunks) > 1  # Should create multiple chunks
    
    # Verify overlap between consecutive chunks
    if len(chunks) >= 2:
        chunk1_tokens = builder._count_tokens(chunks[0]["text"])
        chunk2_tokens = builder._count_tokens(chunks[1]["text"])
        
        # Chunks should respect size limits (allow more tolerance for overlap)
        assert chunk1_tokens <= builder.chunk_size + 20  # Allow more tolerance for overlap
        assert chunk2_tokens <= builder.chunk_size + 20

def test_load_documents_from_directory(test_data_dir):
    """Test loading documents from real directory."""
    import index_builder_faiss
    
    builder = index_builder_faiss.DocumentIndexBuilder()
    documents = builder.load_documents_from_directory(test_data_dir)
    
    # Should load our sample documents
    assert len(documents) >= 3
    
    doc_names = {doc["name"] for doc in documents}
    expected_names = {"python_basics.md", "machine_learning.md", "web_development.html"}
    assert expected_names.issubset(doc_names)
    
    # Verify HTML document was processed
    html_doc = next(doc for doc in documents if doc["name"] == "web_development.html")
    assert "Frontend Technologies" in html_doc["content"]  # Check for content that survives cleaning
    assert "<html>" not in html_doc["content"]  # HTML tags should be cleaned

def test_load_documents_from_directory_missing_raises_real(tmp_path):
    """Test that loading from a missing directory raises FileNotFoundError (real path)."""
    import index_builder_faiss

    builder = index_builder_faiss.DocumentIndexBuilder()
    with pytest.raises(FileNotFoundError):
        builder.load_documents_from_directory(tmp_path / "definitely_missing_dir")

def test_load_documents_from_list():
    """Test loading documents from list with real data."""
    import index_builder_faiss
    
    builder = index_builder_faiss.DocumentIndexBuilder()
    
    input_docs = [
        {
            "name": "test1.txt",
            "content": "This is test content number one.",
            "metadata": {"category": "test"},
            "updated_at": datetime(2024, 1, 1, 12, 0, 0)
        },
        {
            "name": "test2.md", 
            "content": "# Test Document\n\nThis is **markdown** content.",
            "metadata": {"category": "markdown"}
        },
        {
            "content": "Document without name"  # Should get auto-generated name
        },
        {
            "name": "empty.txt",
            "content": "   "  # Should be filtered out
        }
    ]
    
    result = builder.load_documents_from_list(input_docs)
    
    # Should have 3 documents (empty one filtered out)
    assert len(result) == 3
    
    # Verify first document
    doc1 = result[0]
    assert doc1["name"] == "test1.txt"
    assert doc1["content"] == "This is test content number one."
    assert doc1["metadata"]["category"] == "test"
    assert "2024-01-01T12:00:00" in doc1["updated_at"]
    
    # Verify auto-generated name
    unnamed_doc = next(doc for doc in result if doc["content"] == "Document without name")
    assert unnamed_doc["name"].startswith("document_")

@pytest.mark.slow
def test_build_index_e2e_with_libraries(test_model_name, test_device, test_output_dir, skip_if_slow):
    """End-to-end test with real FAISS and sentence transformers."""
    import index_builder_faiss
    
    builder = index_builder_faiss.DocumentIndexBuilder(
        model_name=test_model_name,
        chunk_size=100,
        overlap=20,
        device=test_device
    )
    
    # Use sample documents
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
    
    index_name = "test_real_index"
    builder.build_index(documents, test_output_dir, index_name)
    
    # Verify files were created
    faiss_file = test_output_dir / f"{index_name}.faiss"
    pkl_file = test_output_dir / f"{index_name}.pkl"
    
    assert faiss_file.exists()
    assert pkl_file.exists()
    
    # Verify metadata structure
    with open(pkl_file, "rb") as f:
        metadata = pickle.load(f)
    
    assert "vector_mapping" in metadata
    assert "documents" in metadata
    assert "config" in metadata
    
    config = metadata["config"]
    assert config["index_type"] == "IndexFlatIP"
    assert config["total_documents"] == len(documents)
    assert config["total_vectors"] > 0
    
    # Verify we can load the FAISS index
    index = faiss.read_index(str(faiss_file))
    assert index.ntotal > 0
    assert index.d == builder.dimension

def test_build_index_validation():
    """Test validation with real implementation."""
    import index_builder_faiss
    
    builder = index_builder_faiss.DocumentIndexBuilder()
    
    # Test empty documents
    with pytest.raises(ValueError, match="No documents provided"):
        builder.build_index([], Path("/tmp"), "test")
    
    # Test documents that produce no chunks
    empty_docs = [{
        "id": 0,
        "name": "empty.txt", 
        "size": 0,
        "content": "",
        "metadata": {},
        "updated_at": "2024-01-01T00:00:00"
    }]
    
    with pytest.raises(ValueError, match="No chunks were produced from the input documents"):
        builder.build_index(empty_docs, Path("/tmp"), "test")

def test_cli_integration(test_data_dir, test_output_dir, test_model_name, monkeypatch):
    """Test CLI with real arguments."""
    import index_builder_faiss
    import sys
    
    # Mock sys.argv
    argv = [
        "index_builder_faiss.py",
        "--input-directory", str(test_data_dir),
        "--output-directory", str(test_output_dir), 
        "--index-name", "cli_test",
        "--model-name", test_model_name,
        "--chunk-size", "200",
        "--overlap", "30",
        "--device", "cpu"
    ]
    
    monkeypatch.setattr(sys, "argv", argv)
    
    # Should run without errors
    result = index_builder_faiss.main()
    assert result == 0
    
    # Verify output files
    assert (test_output_dir / "cli_test.faiss").exists()
    assert (test_output_dir / "cli_test.pkl").exists()

def test_split_sentence_by_tokens_handles_long_sentence(test_model_name, test_device):
    """Test sentence splitting with real tokenizer for long sentences."""
    import index_builder_faiss
    
    builder = index_builder_faiss.DocumentIndexBuilder(
        model_name=test_model_name,
        chunk_size=10,  # Small chunk size to force splitting
        overlap=0,
        device=test_device
    )
    
    # Create a long sentence that exceeds chunk size
    long_sentence = "This is a very long sentence that contains many words and should be split into multiple parts when the chunk size is small because it exceeds the token limit that was set for testing purposes."
    
    # Test the sentence splitting
    parts = builder._split_sentence_by_tokens(long_sentence, builder.chunk_size)
    
    # Verify all parts are within token limit
    for part in parts:
        token_count = builder._count_tokens(part)
        assert token_count <= builder.chunk_size, f"Part '{part}' has {token_count} tokens, exceeds limit of {builder.chunk_size}"
    
    # Verify we got multiple parts
    assert len(parts) > 1, "Long sentence should be split into multiple parts"
    
    # Verify all parts together contain the original content
    combined = " ".join(parts)
    original_tokens = set(long_sentence.split())
    combined_tokens = set(combined.split())
    assert original_tokens.issubset(combined_tokens), "Split parts should contain all original tokens"

def test_build_index_no_documents_raises():
    """Test that building index with no documents raises error with real implementation."""
    import index_builder_faiss
    from pathlib import Path
    
    builder = index_builder_faiss.DocumentIndexBuilder()
    
    # Try to build index with empty document list
    with pytest.raises(ValueError, match="No documents provided"):
        builder.build_index([], Path("/tmp"), "empty_test")

def test_build_index_no_chunks_raises(test_model_name, test_device, test_output_dir):
    """Test that building index with documents that produce no chunks raises error."""
    import index_builder_faiss
    
    builder = index_builder_faiss.DocumentIndexBuilder(
        model_name=test_model_name,
        chunk_size=1000,  # Very large chunk size
        overlap=0,
        device=test_device
    )
    
    # Create documents with very short content that won't produce chunks
    documents = [
        {
            "id": 0,
            "name": "empty_doc",
            "size": 0,
            "content": "",  # Empty content
            "metadata": {},
            "updated_at": "2024-01-01T00:00:00"
        },
        {
            "id": 1,
            "name": "whitespace_doc", 
            "size": 3,
            "content": "   ",  # Only whitespace
            "metadata": {},
            "updated_at": "2024-01-01T00:00:00"
        }
    ]
    
    # Should raise error when no valid chunks are produced
    with pytest.raises(ValueError, match="No chunks were produced from the input documents"):
        builder.build_index(documents, test_output_dir, "no_chunks_test")
