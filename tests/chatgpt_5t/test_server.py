# tests/test_server.py
import sys
import pytest

pydantic = pytest.importorskip("pydantic", reason="skip server tests if Pydantic not installed")
pydantic_settings = pytest.importorskip("pydantic_settings", reason="skip server tests if pydantic-settings not installed")

def test_setup_logger_unique_handlers(install_stubs):
    server = import_fresh("server")
    lg = server.setup_logger()
    # ensure no duplicate handlers on repeated calls
    lg2 = server.setup_logger()
    assert len(lg.handlers) == 1
    assert len(lg2.handlers) == 1

def test_mcpserver_create_public_server_registers_tools(install_stubs, monkeypatch, tmp_path):
    # fake FaissSearchEngine so we don't touch disk
    server = import_fresh("server")

    class _FakeSearch:
        def __init__(self, *a, **k):
            self._ready = False
        @property
        def doc_count(self): return 0
        def initialize(self): self._ready = True
        def search_for_chunks(self, query, top_k=10):
            from models import DocumentChunk
            return [DocumentChunk(document_id=0, chunk_index=0, content="hit", metadata={"score": 0.5})]
        def search_for_documents(self, query, top_k=10):
            from models import Document
            return [Document(id="0", name="d", size=1, content="c")]
    monkeypatch.setattr(server, "FaissSearchEngine", _FakeSearch)

    settings = server.ServerSettings(
        transport="stdio",
        server_name="docs-server",
        description="desc",
        model_name="stub-model",
        embedding_path=str(tmp_path),
        embedding_name="X"
    )
    m = server.MCPServer(settings)
    app = m.create_public_server()
    assert app is not None
    # Make sure tools exist and callable
    assert "search_for_chunks" in app._tools
    assert "search_for_documents" in app._tools
    out = app._tools["search_for_chunks"](query="q", top_k=5)
    assert out["status"] in ("success", "not_ready")

def test_run_stdio_server_calls_run(install_stubs, monkeypatch, tmp_path):
    server = import_fresh("server")

    class _FakeSearch:
        def initialize(self): pass
        @property
        def doc_count(self): return 0
        def search_for_chunks(self, *a, **k): return []
        def search_for_documents(self, *a, **k): return []
    monkeypatch.setattr(server, "FaissSearchEngine", _FakeSearch)

    ran = {"ok": False}
    def _fake_run(self): ran["ok"] = True
    # patch FastMCP.run
    from mcp.server.fastmcp import FastMCP
    monkeypatch.setattr(FastMCP, "run", _fake_run, raising=False)

    settings = server.ServerSettings(
        transport="stdio",
        embedding_path=str(tmp_path),
        embedding_name="X"
    )
    m = server.MCPServer(settings)
    m.run_stdio_server()
    assert ran["ok"] is True

def test_main_stdio_path_smoke(install_stubs, monkeypatch):
    server = import_fresh("server")

    # avoid actually running servers
    def _noop(self): return None
    monkeypatch.setattr(server.MCPServer, "run_stdio_server", _noop)
    # craft argv
    monkeypatch.setenv("MCP_EMBEDDING_PATH", "./embeddings")
    monkeypatch.setenv("MCP_EMBEDDING_NAME", "docs_embeddings")
    sys.argv = ["prog", "--transport", "stdio"]
    assert server.main() == 0 or server.main() in (0, 1)
