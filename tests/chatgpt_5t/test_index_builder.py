# tests/test_index_builder_faiss.py
import os
import io
import pickle
import yaml
import numpy as np
import pytest
from pathlib import Path

def test_init_uses_tokenizer_and_model(install_stubs, monkeypatch):
    index_builder = import_fresh("index_builder_faiss")
    b = index_builder.DocumentIndexBuilder(
        model_name="stub-model",
        chunk_size=16,
        overlap=4,
        device="auto",
        encoding_name="stub-enc",
    )
    assert b.dimension == 8  # from stub model
    assert b.chunk_size == 16
    assert b.overlap == 4
    # tokenization sanity
    assert b._count_tokens("hello world") == 2

def test_clean_html_content_semantics(install_stubs):
    index_builder = import_fresh("index_builder_faiss")
    html = """
    <html><body>
      <header>junk</header>
      <nav class="menu">menu</nav>
      <main>
        <h1>Title</h1>
        <p>Intro <b>bold</b> and <i>em</i>.</p>
        <ul><li>one</li><li>two</li></ul>
        <ol><li>a</li><li>b</li></ol>
        <a href="https://example.com">ext</a>
        <a href="/docs/page">int</a>
        <table><tr><th>H</th><th>C</th></tr><tr><td>A</td><td>B</td></tr></table>
        <pre>print(1)</pre>
      </main>
      <footer>junk</footer>
      <script>alert(1)</script>
    </body></html>
    """
    b = index_builder.DocumentIndexBuilder()
    txt = b.clean_html_content(html)
    # headings converted
    assert "# Title" in txt
    # bold/em emphasis markdown-like
    assert "**bold**" in txt
    assert "*em*" in txt
    # lists flattened
    assert "- one" in txt and "- two" in txt
    assert "1. a" in txt and "2. b" in txt
    # external link kept as markdown
    assert "[ext](https://example.com)" in txt
    # internal link becomes plain text
    assert "int" in txt and "[int](" not in txt
    # table condensed
    assert "H | C" in txt and "A | B" in txt
    # code rendered with fences/backticks
    assert "```" in txt or "`print(1)`" in txt
    # junk removed
    assert "menu" not in txt and "junk" not in txt and "alert(" not in txt

def test_token_aware_chunking_overlap(install_stubs):
    index_builder = import_fresh("index_builder_faiss")
    # small chunk size to force splits; overlap=2 tokens
    b = index_builder.DocumentIndexBuilder(chunk_size=5, overlap=2)
    text = "one two three four five six seven eight nine ten"
    chunks = b.chunk_document(text, doc_id=0)
    assert len(chunks) >= 2
    # verify overlap tokens appear at boundary
    c0 = chunks[0]["text"].split()
    c1 = chunks[1]["text"].split()
    assert c0[-2:] == c1[:2]

def test_split_sentence_by_tokens_handles_long_sentence(install_stubs):
    index_builder = import_fresh("index_builder_faiss")
    b = index_builder.DocumentIndexBuilder(chunk_size=4, overlap=0)
    s = "one two three four five six seven"
    parts = b._split_sentence_by_tokens(s, max_tokens=4)
    # every part <= 4 tokens
    assert all(len(p.split()) <= 4 for p in parts)
    assert "one two three four" in parts[0]

def test_load_documents_from_directory(install_stubs, tmp_path, monkeypatch):
    index_builder = import_fresh("index_builder_faiss")
    base = tmp_path / "docs"
    base.mkdir()
    (base / "a.txt").write_text("alpha beta", encoding="utf-8")
    (base / "b.md").write_text("**bold** text", encoding="utf-8")
    (base / "c.html").write_text("<html><body><h1>T</h1><p>x</p></body></html>", encoding="utf-8")
    (base / "ignored.bin").write_bytes(b"\x00\x01")

    b = index_builder.DocumentIndexBuilder()
    docs = b.load_documents_from_directory(base)
    names = {d["name"] for d in docs}
    assert {"a.txt", "b.md", "c.html"}.issubset(names)
    # HTML was cleaned
    html_doc = [d for d in docs if d["name"] == "c.html"][0]
    assert "# T" in html_doc["content"]

def test_load_documents_from_list_variants(install_stubs):
    index_builder = import_fresh("index_builder_faiss")
    from datetime import datetime
    docs_in = [
        {"name": "keep1.txt", "content": "hello", "metadata": {"x": 1}, "updated_at": datetime(2020,1,1)},
        {"name": "skip-empty", "content": "   "},
        {"content": "no name"},
    ]
    b = index_builder.DocumentIndexBuilder()
    out = b.load_documents_from_list(docs_in)
    assert len(out) == 2
    assert out[0]["name"] == "keep1.txt"
    assert "T" in out[0]["updated_at"]  # ISO-ish

def test_build_index_e2e_writes_files(install_stubs, tmp_path, monkeypatch):
    index_builder = import_fresh("index_builder_faiss")
    b = index_builder.DocumentIndexBuilder(chunk_size=8, overlap=2)
    documents = [
        {"id": 0, "name": "d0", "size": 5, "content": "a b c d e f g h i", "metadata": {}, "updated_at": "2024-01-01T00:00:00"},
        {"id": 1, "name": "d1", "size": 3, "content": "one two three four", "metadata": {}, "updated_at": "2024-01-02T00:00:00"},
    ]
    out_dir = tmp_path / "idx"
    monkeypatch.chdir(tmp_path)  # DEBUG writes YAML in CWD

    b.build_index(documents, out_dir, "my_index")

    idx = out_dir / "my_index.faiss"
    pkl = out_dir / "my_index.pkl"
    yml = tmp_path / "my_index.yaml"
    assert idx.exists() and pkl.exists() and yml.exists()

    meta = pickle.loads((out_dir / "my_index.pkl").read_bytes())
    assert "vector_mapping" in meta and "documents" in meta and "config" in meta
    assert meta["config"]["index_type"] == "IndexFlatIP"
    assert meta["config"]["total_documents"] == 2
    assert meta["config"]["total_vectors"] >= 2

def test_build_index_no_documents_raises(install_stubs, tmp_path):
    index_builder = import_fresh("index_builder_faiss")
    b = index_builder.DocumentIndexBuilder()
    with pytest.raises(ValueError):
        b.build_index([], tmp_path, "x")

def test_build_index_no_chunks_raises(install_stubs, tmp_path, monkeypatch):
    index_builder = import_fresh("index_builder_faiss")
    b = index_builder.DocumentIndexBuilder()
    docs = [{"id": 0, "name": "d", "size": 0, "content": "something", "metadata": {}, "updated_at": "now"}]
    # Force chunker to produce nothing
    monkeypatch.setattr(b, "chunk_document", lambda text, doc_id: [])
    with pytest.raises(ValueError):
        b.build_index(docs, tmp_path, "x")
