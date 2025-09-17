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
    m.cleanup()

def test_faiss_search_engine_initialize_success(install_stubs, tmp_path):
    sef = import_fresh("search_engine_faiss")
    faiss = __import__("faiss")
    idx = faiss.IndexFlatIP(8)
    faiss._READ_INDEX_INSTANCE = idx
    meta = {
        "vector_mapping": {0: {"doc_id": 0, "chunk_index": 0}, 1: {"doc_id": 0, "chunk_index": 1}},
        "documents": {0: {"id": 0, "name": "d", "size": 1, "content": "C", "chunks": ["a", "b"], "metadata": {}, "updated_at": "2024-01-01T00:00:00"}},
        "config": {"index_type": "IndexFlatIP"}
    }
    embdir = tmp_path
    (embdir / "emb.faiss").write_bytes(b"X")
    _write_metadata(embdir, "emb", meta)
    eng = sef.FaissSearchEngine("emb", embdir, "stub-model", device="cpu")
    eng.initialize()
    assert eng.is_ready is True
    assert eng.doc_count == 1

def test_faiss_initialize_missing_files_raises(install_stubs, tmp_path):
    sef = import_fresh("search_engine_faiss")
    eng = sef.FaissSearchEngine("missing", tmp_path, "stub-model", device="cpu")
    with pytest.raises(FileNotFoundError):
        eng.initialize()

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

def test_faiss_initialize_corrupted_metadata_raises(install_stubs, tmp_path):
    sef = import_fresh("search_engine_faiss")
    faiss = __import__("faiss")
    faiss._READ_INDEX_INSTANCE = faiss.IndexFlatIP(8)
    (tmp_path / "e.faiss").write_bytes(b"X")
    (tmp_path / "e.pkl").write_bytes(b"\x00\x01notapickle")
    eng = sef.FaissSearchEngine("e", tmp_path, "stub-model", device="cpu")
    with pytest.raises(Exception):
        eng.initialize()

def test_faiss_initialize_invalid_metadata_structure_raises(install_stubs, tmp_path):
    sef = import_fresh("search_engine_faiss")
    faiss = __import__("faiss")
    faiss._READ_INDEX_INSTANCE = faiss.IndexFlatIP(8)
    (tmp_path / "e.faiss").write_bytes(b"X")
    _write_metadata(tmp_path, "e", {"oops": 1})
    eng = sef.FaissSearchEngine("e", tmp_path, "stub-model", device="cpu")
    with pytest.raises(ValueError):
        eng.initialize()

def test_search_for_chunks_ip_normalization_and_invalid_ids(install_stubs, tmp_path):
    sef = import_fresh("search_engine_faiss")
    faiss = __import__("faiss")
    idx = faiss.IndexFlatIP(8)
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
    enc = eng._sentence_transformer
    xb = enc.encode(["alpha", "beta"]).astype(np.float32)
    faiss.normalize_L2(xb)
    idx.add(xb)
    chunks = eng.search_for_chunks("alpha", top_k=2)
    assert len(chunks) >= 1
    assert 0.0 <= chunks[0].metadata["score"] <= 1.0
    # Now simulate invalid vector ids
    class DummyIdx:
        metric_type = faiss.METRIC_INNER_PRODUCT
        ntotal = 2
        def search(self, q, k):
            return np.array([[0.9, 0.8]], dtype=np.float32), np.array([[-1, 999]], dtype=np.int64)
    eng._index = DummyIdx()
    out = eng.search_for_chunks("alpha", top_k=2)
    assert out == []

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
    xb = enc.encode(["a0", "a1", "b0"]).astype(np.float32)
    faiss.normalize_L2(xb)
    idx.add(xb)
    docs = eng.search_for_documents("a0", top_k=2)
    assert [d.name for d in docs] == ["d0", "d1"]

def test_result_multiplier_thresholds_precise(install_stubs):
    sef = import_fresh("search_engine_faiss")
    eng = sef.FaissSearchEngine("n", ".", "stub-model")
    # avg_chunks_per_doc = 2 -> 2
    md = {"vector_mapping": {0:{"doc_id":0,"chunk_index":0},1:{"doc_id":0,"chunk_index":1}}, "documents": {0:{}}, "config":{}}
    assert eng._calculate_document_search_result_multiplier(md) == 2
    # avg = 5 -> 3
    md = {"vector_mapping": {i:{"doc_id":0,"chunk_index":i} for i in range(5)}, "documents": {0:{}}, "config":{}}
    assert eng._calculate_document_search_result_multiplier(md) == 3
    # avg = 9 -> 4
    md = {"vector_mapping": {i:{"doc_id":0,"chunk_index":i} for i in range(9)}, "documents": {0:{}}, "config":{}}
    assert eng._calculate_document_search_result_multiplier(md) == 4

def test_should_normalize_query_meta_and_metric(install_stubs):
    sef = import_fresh("search_engine_faiss")
    faiss = __import__("faiss")
    eng = sef.FaissSearchEngine("n", ".", "stub-model")
    class DummyIdx:
        def __init__(self, metric_type):
            self.metric_type = metric_type
            self.__class__.__name__ = "IndexFlatIP"
    # IP metric => normalize
    eng._index = DummyIdx(faiss.METRIC_INNER_PRODUCT)
    eng._metadata = {"config":{"index_type":"IndexFlatIP"}}
    assert eng._should_normalize_query() is True
    # L2 metric => no normalize
    eng._index = DummyIdx(faiss.METRIC_L2)
    assert eng._should_normalize_query() is False

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
    eng.cleanup()
    assert eng._index is None
    assert eng._sentence_transformer is None
