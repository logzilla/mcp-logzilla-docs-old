# tests/test_models.py
import pytest
from pathlib import Path
from datetime import datetime
from models import DocumentChunk, Document

def test_document_chunk_to_dict():
    dc = DocumentChunk(document_id=1, chunk_index=2, content="abc", metadata={"score": 0.9})
    d = dc.to_dict()
    assert d["document_id"] == 1 and d["chunk_index"] == 2 and d["content"] == "abc"
    assert d["metadata"]["score"] == 0.9

def test_document_from_file_and_to_dict(tmp_path):
    p = tmp_path / "x.txt"
    p.write_text("hello", encoding="utf-8")
    doc = Document.from_file(p, document_id="docs/x.txt")
    assert doc.id == "docs/x.txt"
    assert doc.name == "x"
    assert doc.size == p.stat().st_size
    d = doc.to_dict()
    assert d["name"] == "x"
    assert "updated_at" in d and isinstance(d["updated_at"], str)

def test_document_to_dict_with_datetime():
    dt = datetime(2023, 5, 1, 12, 0, 0)
    doc = Document(id="1", name="n", size=10, content="c", updated_at=dt)
    d = doc.to_dict()
    assert d["updated_at"].startswith("2023-05-01T12:00:00")
