# tests/test_models.py
"""
Real implementation tests for models.py using actual file operations and datetime handling.
"""
from datetime import datetime
from pathlib import Path
from models import DocumentChunk, Document, SearchEngine, SearchEngineFactory
import pytest
from abc import ABC, abstractmethod

def test_document_chunk_to_dict():
    """Test DocumentChunk to_dict with real data."""
    chunk = DocumentChunk(
        document_id=1, 
        chunk_index=2, 
        content="This is real content from a document chunk", 
        metadata={"score": 0.95, "source": "real_document.md"}
    )
    
    result = chunk.to_dict()
    
    assert result["document_id"] == 1
    assert result["chunk_index"] == 2
    assert result["content"] == "This is real content from a document chunk"
    assert result["metadata"]["score"] == 0.95
    assert result["metadata"]["source"] == "real_document.md"

def test_document_from_file_and_to_dict(tmp_path):
    """Test Document.from_file and to_dict with real file operations."""
    # Create a real test file
    test_file = tmp_path / "test_document.md"
    test_content = """# Test Document

This is a real test document with actual content.

## Section 1
Some content here.

## Section 2
More content here.
"""
    test_file.write_text(test_content, encoding="utf-8")
    
    # Create document from real file
    doc = Document.from_file(test_file, document_id="docs/test_document.md")
    
    # Verify document properties
    assert doc.id == "docs/test_document.md"
    assert doc.name == "test_document"
    assert doc.size == test_file.stat().st_size
    assert doc.content == test_content
    assert isinstance(doc.updated_at, datetime)
    assert doc.metadata["file_extension"] == ".md"
    
    # Test to_dict conversion
    result = doc.to_dict()
    assert result["id"] == "docs/test_document.md"
    assert result["name"] == "test_document"
    assert result["size"] == test_file.stat().st_size
    assert result["content"] == test_content
    assert "updated_at" in result
    assert isinstance(result["updated_at"], str)
    
    # Verify datetime formatting
    assert "T" in result["updated_at"]  # ISO format includes T separator

def test_document_to_dict_with_datetime():
    """Test Document to_dict with real datetime objects."""
    # Test with specific datetime
    test_datetime = datetime(2024, 1, 15, 14, 30, 45)
    doc = Document(
        id="real_doc_1", 
        name="real_document", 
        size=1024, 
        content="Real document content with actual text", 
        updated_at=test_datetime,
        metadata={"category": "test", "version": "1.0"}
    )
    
    result = doc.to_dict()
    
    assert result["id"] == "real_doc_1"
    assert result["name"] == "real_document"
    assert result["size"] == 1024
    assert result["content"] == "Real document content with actual text"
    assert result["metadata"]["category"] == "test"
    assert result["metadata"]["version"] == "1.0"
    
    # Verify datetime serialization
    assert result["updated_at"].startswith("2024-01-15T14:30:45")
    
    # Test with current datetime
    current_time = datetime.now()
    doc2 = Document(
        id="real_doc_2",
        name="current_doc",
        size=512,
        content="Document with current timestamp",
        updated_at=current_time
    )
    
    result2 = doc2.to_dict()
    assert "updated_at" in result2
    assert isinstance(result2["updated_at"], str)
    # Should contain current year
    assert str(current_time.year) in result2["updated_at"]

def test_document_without_updated_at():
    """Test Document without updated_at field."""
    doc = Document(
        id="doc_no_date",
        name="no_date_doc",
        size=256,
        content="Document without updated_at"
    )
    
    result = doc.to_dict()
    assert result["id"] == "doc_no_date"
    assert result["name"] == "no_date_doc"
    assert result["content"] == "Document without updated_at"
    assert result["updated_at"] is None

def test_document_str_and_repr():
    """Test Document __str__ and __repr__ methods."""
    doc = Document(
        id="test_doc",
        name="test",
        size=512,
        content="Test content"
    )
    
    str_repr = str(doc)
    assert "Document" in str_repr
    assert "id=test_doc" in str_repr
    assert "name=test" in str_repr
    assert "size=512" in str_repr
    
    repr_repr = repr(doc)
    assert repr_repr == str_repr

def test_document_from_file_with_non_utf8(tmp_path):
    """Test Document.from_file with non-UTF8 encoding."""
    # Create a file with latin-1 encoding
    test_file = tmp_path / "latin1_doc.txt"
    latin1_content = "Content with special char: café"
    test_file.write_bytes(latin1_content.encode('latin-1'))
    
    # Should handle non-UTF8 gracefully
    doc = Document.from_file(test_file)
    assert doc.name == "latin1_doc"
    assert doc.content  # Should have some content
    assert doc.metadata["file_extension"] == ".txt"

def test_document_from_file_missing_file(tmp_path):
    """Test Document.from_file with missing file."""
    missing_file = tmp_path / "missing.txt"
    
    with pytest.raises(FileNotFoundError, match="File not found"):
        Document.from_file(missing_file)

def test_search_engine_abstract_class():
    """Test SearchEngine abstract base class."""
    # Should not be able to instantiate abstract class directly
    with pytest.raises(TypeError):
        SearchEngine()
    
    # Test that concrete implementation must implement all abstract methods
    class IncompleteSearchEngine(SearchEngine):
        """Incomplete implementation for testing."""
        pass
    
    with pytest.raises(TypeError):
        IncompleteSearchEngine()
    
    # Test complete implementation
    class CompleteSearchEngine(SearchEngine):
        """Complete implementation for testing."""
        
        def initialize(self, on_ready_fn=None):
            pass
        
        def search_for_chunks(self, query, top_k=10):
            return []
        
        def search_for_documents(self, query, top_k=10):
            return []
        
        def get_status(self):
            return ["OK"]
    
    # Should be able to instantiate complete implementation
    engine = CompleteSearchEngine()
    assert engine.name == "CompleteSearchEngine"
    assert engine.get_name() == "CompleteSearchEngine"

def test_search_engine_factory_abstract_class():
    """Test SearchEngineFactory abstract base class."""
    # Should not be able to instantiate abstract class
    with pytest.raises(TypeError):
        SearchEngineFactory()
    
    # Test that concrete implementation must implement all abstract methods
    class IncompleteFactory(SearchEngineFactory):
        """Incomplete factory implementation."""
        pass
    
    with pytest.raises(TypeError):
        IncompleteFactory()
    
    # Test complete implementation
    class CompleteFactory(SearchEngineFactory):
        """Complete factory implementation."""
        
        def get_engine(self, version):
            return None
        
        def clear_cache(self):
            pass
    
    # Should be able to instantiate complete implementation
    factory = CompleteFactory()
    assert factory.get_engine("test") is None
    factory.clear_cache()  # Should not raise

def test_document_chunk_with_different_id_types():
    """Test DocumentChunk with different document_id types."""
    # Test with integer ID
    chunk_int = DocumentChunk(
        document_id=42,
        chunk_index=0,
        content="Integer ID chunk"
    )
    assert chunk_int.document_id == 42
    
    # Test with string ID
    chunk_str = DocumentChunk(
        document_id="doc_42",
        chunk_index=1,
        content="String ID chunk"
    )
    assert chunk_str.document_id == "doc_42"
    
    # Test to_dict for both
    dict_int = chunk_int.to_dict()
    assert dict_int["document_id"] == 42
    
    dict_str = chunk_str.to_dict()
    assert dict_str["document_id"] == "doc_42"

def test_document_with_empty_metadata():
    """Test Document with empty or None metadata."""
    # Test with None metadata
    doc1 = Document(
        id="doc1",
        name="test1",
        size=100,
        content="Test content",
        metadata=None
    )
    assert doc1.metadata == {}
    
    # Test with empty metadata
    doc2 = Document(
        id="doc2",
        name="test2",
        size=200,
        content="Test content 2",
        metadata={}
    )
    assert doc2.metadata == {}
    
    # Test to_dict
    result1 = doc1.to_dict()
    assert result1["metadata"] == {}
    
    result2 = doc2.to_dict()
    assert result2["metadata"] == {}

def test_document_from_file_auto_id(tmp_path):
    """Test Document.from_file with automatic ID generation."""
    # Create nested directory structure
    nested_dir = tmp_path / "docs" / "subdocs"
    nested_dir.mkdir(parents=True)
    
    test_file = nested_dir / "test.md"
    test_file.write_text("Test content")
    
    # Without providing document_id, should generate from path
    doc = Document.from_file(test_file)
    
    # ID should be relative path from parent's parent
    assert doc.id  # Should have some ID
    assert doc.name == "test"
    
    # With explicit document_id
    doc2 = Document.from_file(test_file, document_id="custom_id")
    assert doc2.id == "custom_id"