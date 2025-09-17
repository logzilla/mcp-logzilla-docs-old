# tests/conftest.py
import sys
import types
import math
import numpy as np
import pytest
from pathlib import Path

# ---------------------------
# Stub: tiktoken
# ---------------------------
class _StubEncoding:
    def __init__(self, name="stub"):
        self.name = name
        self._word2id = {}
        self._id2word = {}

    def _ensure_word(self, w: str) -> int:
        if w not in self._word2id:
            i = len(self._word2id) + 1
            self._word2id[w] = i
            self._id2word[i] = w
        return self._word2id[w]

    def encode(self, text: str):
        if not text:
            return []
        # simple whitespace-based "tokenizer"
        words = text.split()
        return [self._ensure_word(w) for w in words]

    def decode(self, ids):
        if not ids:
            return ""
        words = [self._id2word.get(int(i), "<UNK>") for i in ids]
        # join with spaces (good enough for chunk overlap tests)
        return " ".join(words)

def _install_tiktoken_stub(monkeypatch):
    mod = types.ModuleType("tiktoken")
    def get_encoding(name):
        return _StubEncoding(name)
    mod.get_encoding = get_encoding
    sys.modules["tiktoken"] = mod

# ---------------------------
# Stub: sentence_transformers
# ---------------------------
class _StubSentenceTransformer:
    def __init__(self, model_name="stub-model", device=None):
        self._name = model_name
        self.device = device or "cpu"
        self._dim = 8

    def get_sentence_embedding_dimension(self):
        return self._dim

    def encode(self, texts, convert_to_numpy=True, show_progress_bar=False, batch_size=None):
        if isinstance(texts, str):
            texts = [texts]
        vecs = []
        for t in texts:
            v = np.zeros(self._dim, dtype=np.float32)
            # deterministic toy embedding from characters
            for i, ch in enumerate(t):
                v[i % self._dim] += (ord(ch) % 13) / 13.0
            vecs.append(v)
        arr = np.vstack(vecs).astype(np.float32)
        if convert_to_numpy:
            return arr
        return arr.tolist()

def _install_sentence_transformers_stub(monkeypatch):
    pkg = types.ModuleType("sentence_transformers")
    pkg.SentenceTransformer = _StubSentenceTransformer
    sys.modules["sentence_transformers"] = pkg

# ---------------------------
# Stub: faiss
# ---------------------------
class _StubIndexFlatIP:
    def __init__(self, d):
        self.d = d
        self.metric_type = 0  # METRIC_INNER_PRODUCT
        self._vecs = None

    @property
    def ntotal(self):
        return 0 if self._vecs is None else self._vecs.shape[0]

    def add(self, xb):
        xb = np.asarray(xb, dtype=np.float32)
        if self._vecs is None:
            self._vecs = xb.copy()
        else:
            self._vecs = np.vstack([self._vecs, xb])

    def search(self, q, k):
        q = np.asarray(q, dtype=np.float32)
        if self._vecs is None or self.ntotal == 0:
            scores = np.full((q.shape[0], k), -1.0, dtype=np.float32)
            ids = np.full((q.shape[0], k), -1, dtype=np.int64)
            return scores, ids
        # inner product
        sims = q @ self._vecs.T
        # top-k
        idx = np.argsort(-sims, axis=1)[:, :k]
        scores = np.take_along_axis(sims, idx, axis=1)
        return scores.astype(np.float32), idx.astype(np.int64)

    def reset(self):
        self._vecs = None

def _faiss_normalize_L2(x):
    x[:] = x / np.maximum(np.linalg.norm(x, axis=1, keepdims=True), 1e-12).astype(x.dtype)

class _FaissModule(types.ModuleType):
    METRIC_INNER_PRODUCT = 0
    METRIC_L2 = 1
    IndexFlatIP = _StubIndexFlatIP
    _READ_INDEX_INSTANCE = None  # allow tests to inject a ready-made index

    def normalize_L2(self, x):
        return _faiss_normalize_L2(x)

    def write_index(self, index, path):
        # write a tiny marker so .stat() has size
        Path(path).write_bytes(b"FAISS_STUB")

    def read_index(self, path):
        # return injected instance if present; else empty IP index
        if self._READ_INDEX_INSTANCE is not None:
            return self._READ_INDEX_INSTANCE
        # default dimensionality 8 to match stub encoder
        return _StubIndexFlatIP(8)

def _install_faiss_stub(monkeypatch):
    mod = _FaissModule("faiss")
    sys.modules["faiss"] = mod
    return mod

# ---------------------------
# Stubs for dotenv & MCP (server tests)
# ---------------------------
def _install_dotenv_stub(monkeypatch):
    m = types.ModuleType("dotenv")
    def load_dotenv():
        return None
    m.load_dotenv = load_dotenv
    sys.modules["dotenv"] = m

class _StubFastMCP:
    def __init__(self, name, instructions="", debug=False, stateless_http=False):
        self.name = name
        self.instructions = instructions
        self.debug = debug
        self.stateless_http = stateless_http
        self._tools = {}
        self._ran = False

    def tool(self, name=None, description=None):
        def deco(fn):
            key = name or fn.__name__
            self._tools[key] = fn
            return fn
        return deco

    def streamable_http_app(self):
        # Not used in tests, just return self
        return self

    def run(self):
        self._ran = True

    # Compatibility shim for help page in server FastAPI app
    class _TM:
        def __init__(self, tools):
            self._tools = tools
        def list_tools(self):
            # objects with "name" attr
            return [types.SimpleNamespace(name=k) for k in self._tools.keys()]

    @property
    def _tool_manager(self):
        return _StubFastMCP._TM(self._tools)

def _install_mcp_stubs(monkeypatch):
    mcp = types.ModuleType("mcp")
    server_pkg = types.ModuleType("mcp.server")
    fastmcp_mod = types.ModuleType("mcp.server.fastmcp")
    auth_mod = types.ModuleType("mcp.server.auth")
    auth_settings_mod = types.ModuleType("mcp.server.auth.settings")
    types_mod = types.ModuleType("mcp.types")

    fastmcp_mod.FastMCP = _StubFastMCP
    class _AuthSettings: ...
    auth_settings_mod.AuthSettings = _AuthSettings
    class _PM: ...
    class _TC: ...
    types_mod.PromptMessage = _PM
    types_mod.TextContent = _TC

    sys.modules["mcp"] = mcp
    sys.modules["mcp.server"] = server_pkg
    sys.modules["mcp.server.fastmcp"] = fastmcp_mod
    sys.modules["mcp.server.auth"] = auth_mod
    sys.modules["mcp.server.auth.settings"] = auth_settings_mod
    sys.modules["mcp.types"] = types_mod

# ---------------------------
# Master fixture to install stubs
# ---------------------------
@pytest.fixture
def install_stubs(monkeypatch):
    _install_tiktoken_stub(monkeypatch)
    _install_sentence_transformers_stub(monkeypatch)
    faiss_mod = _install_faiss_stub(monkeypatch)
    _install_dotenv_stub(monkeypatch)
    _install_mcp_stubs(monkeypatch)
    return faiss_mod

# Utility: quickly import a module fresh after stubs
def import_fresh(module_name: str):
    if module_name in sys.modules:
        del sys.modules[module_name]
    return __import__(module_name, fromlist=["*"])
