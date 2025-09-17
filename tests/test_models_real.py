# tests/test_models_real.py
"""
Real implementation tests for models.py using actual file operations and datetime handling.
"""
import pytest
from pathlib import Path
from datetime import datetime
from models import DocumentChunk, Document

def test_document_chunk_to_dict_real():
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

def test_document_from_file_and_to_dict_real(tmp_path):
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
    
    # Test to_dict conversion
    result = doc.to_dict()
    assert result["id"] == "docs/test_document.md"
    assert result["name"] == "test_document"
    assert result["size"] == test_file.stat().st_size
    assert result["content"] == test_content
    assert "updated_at" in result
    assert isinstance(result["updated_at"], str)
    
    # Verify datetime formatting
    assert result["updated_at"].endswith("Z") or "T" in result["updated_at"]

def test_document_to_dict_with_datetime_real():
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
