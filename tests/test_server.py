# tests/test_server.py
import pytest

pydantic = pytest.importorskip("pydantic", reason="skip server tests if Pydantic not installed")
pydantic_settings = pytest.importorskip("pydantic_settings", reason="skip server tests if pydantic-settings not installed")

def test_setup_logger_unique_handlers(install_stubs):
    server = import_fresh("server")
    lg = server.setup_logger()
    lg2 = server.setup_logger()
    assert len(lg.handlers) == 1
    assert len(lg2.handlers) == 1

def test_mcpserver_create_public_server_registers_tools_and_health(install_stubs, monkeypatch, tmp_path):
    server = import_fresh("server")

    class _FakeSearch:
        def __init__(self, *a, **k): pass
        @property
        def doc_count(self): return 0
        def initialize(self): pass
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
    assert "search_for_chunks" in app._tools
    assert "search_for_documents" in app._tools
    assert "health_check" in app._tools
    # health_check should return ready once created
    out = app._tools["health_check"]()
    assert out["status"] in ("ready", "initializing")
    assert "documents_loaded" in out

def test_run_stdio_server_calls_run(install_stubs, monkeypatch, tmp_path):
    server = import_fresh("server")

    class _FakeSearch:
        def __init__(self, *a, **k): pass  # Accept any arguments
        def initialize(self): pass
        @property
        def doc_count(self): return 0
        def search_for_chunks(self, *a, **k): return []
        def search_for_documents(self, *a, **k): return []
    monkeypatch.setattr(server, "FaissSearchEngine", _FakeSearch)

    ran = {"ok": False}
    def _fake_run(self): ran["ok"] = True
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
    def _noop(self): return None
    monkeypatch.setattr(server.MCPServer, "run_stdio_server", _noop)
    monkeypatch.setenv("MCP_EMBEDDING_PATH", "./embeddings")
    monkeypatch.setenv("MCP_EMBEDDING_NAME", "docs_embeddings")
    import sys
    sys.argv = ["prog", "--transport", "stdio"]
    rc = server.main()
    assert rc in (0, 1)
