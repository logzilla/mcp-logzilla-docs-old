# tests/test_search_engine_faiss.py
import pickle
import numpy as np
import pytest
from pathlib import Path

def _write_metadata(tmpdir, name, meta):
    p = tmpdir / f"{name}.pkl"
    p.write_bytes(pickle.dumps(meta))
    return p

def test_model_sentence_transformer_encode_and_cleanup(install_stubs):
    sef = import_fresh("search_engine_faiss")
    m = sef.ModelSentenceTransformer("stub", "cpu")
    v = m.encode(["hello", "world"])
    assert v.shape == (2, m.dimension)
    m.cleanup()  # should not raise

def test_faiss_search_engine_initialize_success(install_stubs, tmp_path):
    sef = import_fresh("search_engine_faiss")
    faiss = __import__("faiss")
    # build a stub index with known dim
    idx = faiss.IndexFlatIP(8)
    faiss._READ_INDEX_INSTANCE = idx  # returned by read_index

    # metadata with two vectors → one doc
    meta = {
        "vector_mapping": {0: {"doc_id": 0, "chunk_index": 0}, 1: {"doc_id": 0, "chunk_index": 1}},
        "documents": {0: {"id": 0, "name": "d", "size": 1, "content": "C", "chunks": ["a", "b"], "metadata": {}, "updated_at": "2024-01-01T00:00:00"}},
        "config": {"index_type": "IndexFlatIP"}
    }
    embdir = tmp_path
    (embdir / "emb.faiss").write_bytes(b"X")  # existence check
    _write_metadata(embdir, "emb", meta)

    eng = sef.FaissSearchEngine("emb", embdir, "stub-model", device="cpu")
    eng.initialize()
    assert eng.is_ready is True
    assert eng.doc_count == 1

def test_faiss_initialize_dimension_mismatch_raises(install_stubs, tmp_path):
    sef = import_fresh("search_engine_faiss")
    faiss = __import__("faiss")
    bad_idx = faiss.IndexFlatIP(16)  # model gives 8
    faiss._READ_INDEX_INSTANCE = bad_idx
    meta = {"vector_mapping": {}, "documents": {}, "config": {"index_type": "IndexFlatIP"}}
    (tmp_path / "e.faiss").write_bytes(b"X")
    _write_metadata(tmp_path, "e", meta)
    eng = sef.FaissSearchEngine("e", tmp_path, "stub-model", device="cpu")
    with pytest.raises(ValueError):
        eng.initialize()

def test_faiss_initialize_invalid_metadata_raises(install_stubs, tmp_path):
    sef = import_fresh("search_engine_faiss")
    faiss = __import__("faiss")
    faiss._READ_INDEX_INSTANCE = faiss.IndexFlatIP(8)
    bad_meta = {"oops": 1}
    (tmp_path / "e.faiss").write_bytes(b"X")
    _write_metadata(tmp_path, "e", bad_meta)
    eng = sef.FaissSearchEngine("e", tmp_path, "stub-model", device="cpu")
    with pytest.raises(ValueError):
        eng.initialize()

def test_search_for_chunks_ip_normalization(install_stubs, tmp_path):
    sef = import_fresh("search_engine_faiss")
    faiss = __import__("faiss")
    idx = faiss.IndexFlatIP(8)
    # create metadata for two vectors
    meta = {
        "vector_mapping": {0: {"doc_id": 0, "chunk_index": 0}, 1: {"doc_id": 0, "chunk_index": 1}},
        "documents": {0: {"id": 0, "name": "d", "size": 1, "content": "C", "chunks": ["alpha", "beta"], "metadata": {}, "updated_at": "2024-01-01T00:00:00"}},
        "config": {"index_type": "IndexFlatIP"}
    }
    (tmp_path / "X.faiss").write_bytes(b"X")
    _write_metadata(tmp_path, "X", meta)
    faiss._READ_INDEX_INSTANCE = idx

    eng = sef.FaissSearchEngine("X", tmp_path, "stub-model", device="cpu")
    eng.initialize()

    # manually "train" index by adding vectors from the same encoder
    enc = eng._sentence_transformer
    mat = enc.encode(["alpha", "beta"]).astype(np.float32)
    faiss.normalize_L2(mat)
    idx.add(mat)

    chunks = eng.search_for_chunks("alpha", top_k=2)
    assert len(chunks) >= 1
    # scores mapped to [0,1]
    assert 0.0 <= chunks[0].metadata["score"] <= 1.0
    assert chunks[0].content in ("alpha", "beta")

def test_search_for_documents_dedup_and_order(install_stubs, tmp_path):
    sef = import_fresh("search_engine_faiss")
    faiss = __import__("faiss")
    idx = faiss.IndexFlatIP(8)
    meta = {
        "vector_mapping": {
            0: {"doc_id": 0, "chunk_index": 0},
            1: {"doc_id": 0, "chunk_index": 1},
            2: {"doc_id": 1, "chunk_index": 0},
        },
        "documents": {
            0: {"id": 0, "name": "d0", "size": 1, "content": "", "chunks": ["a0", "a1"], "metadata": {}, "updated_at": "2024-01-01T00:00:00"},
            1: {"id": 1, "name": "d1", "size": 1, "content": "", "chunks": ["b0"], "metadata": {}, "updated_at": "2024-01-02T00:00:00"},
        },
        "config": {"index_type": "IndexFlatIP"},
    }
    (tmp_path / "Z.faiss").write_bytes(b"X")
    _write_metadata(tmp_path, "Z", meta)
    faiss._READ_INDEX_INSTANCE = idx

    eng = sef.FaissSearchEngine("Z", tmp_path, "stub-model", device="cpu")
    eng.initialize()

    enc = eng._sentence_transformer
    # two chunks from doc 0, one chunk from doc 1
    xb = enc.encode(["a0", "a1", "b0"]).astype(np.float32)
    faiss.normalize_L2(xb)
    idx.add(xb)

    docs = eng.search_for_documents("a0", top_k=2)
    # de-dup ensures we can get both docs, not repeated doc 0
    assert [d.name for d in docs] == ["d0", "d1"]

def test_result_multiplier_thresholds(install_stubs):
    sef = import_fresh("search_engine_faiss")
    eng = sef.FaissSearchEngine("n", ".", "stub-model")
    md = {"vector_mapping": {i: {"doc_id": i//2, "chunk_index": 0} for i in range(4)}, "documents": {0:{},1:{}}, "config":{}}
    assert eng._calculate_document_search_result_multiplier(md) == 2
    md = {"vector_mapping": {i: {"doc_id": i//1, "chunk_index": 0} for i in range(8)}, "documents": {i:{} for i in range(1,2)}, "config":{}}
    assert eng._calculate_document_search_result_multiplier(md) == 4 or eng._calculate_document_search_result_multiplier(md) in (3,4)

def test_cleanup_safe_and_doc_count(install_stubs, tmp_path):
    sef = import_fresh("search_engine_faiss")
    faiss = __import__("faiss")
    faiss._READ_INDEX_INSTANCE = faiss.IndexFlatIP(8)
    meta = {"vector_mapping": {}, "documents": {}, "config": {"index_type": "IndexFlatIP"}}
    (tmp_path / "A.faiss").write_bytes(b"X")
    _write_metadata(tmp_path, "A", meta)
    eng = sef.FaissSearchEngine("A", tmp_path, "stub-model")
    eng.initialize()
    assert eng.doc_count == 0
    eng.cleanup()  # should not raise
