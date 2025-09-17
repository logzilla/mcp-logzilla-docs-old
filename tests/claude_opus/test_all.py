#!/usr/bin/env python3
"""
Comprehensive Test Suite for MCP Documentation Server
=====================================================

Test coverage for all modules:
- index_builder_faiss.py
- models.py
- search_engine_faiss.py
- server.py
"""

import pytest
import tempfile
import shutil
import json
import pickle
import numpy as np
import faiss
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, mock_open, PropertyMock, AsyncMock
from datetime import datetime
import asyncio
import sys
import io
import os

# Import modules to test
sys.path.insert(0, '.')  # Ensure we can import local modules

from index_builder_faiss import DocumentIndexBuilder, Constants
from models import Document, DocumentChunk, SearchEngine
from search_engine_faiss import FaissSearchEngine, ModelSentenceTransformer
from server import MCPServer, ServerSettings, FastApp, FastAppSettings


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_documents():
    """Create sample documents for testing."""
    return [
        {
            'id': 0,
            'name': 'doc1.txt',
            'size': 100,
            'content': 'This is a test document about artificial intelligence and machine learning.',
            'metadata': {'category': 'tech'},
            'updated_at': datetime.now().isoformat()
        },
        {
            'id': 1,
            'name': 'doc2.md',
            'size': 150,
            'content': 'Python programming is essential for data science and web development.',
            'metadata': {'category': 'programming'},
            'updated_at': datetime.now().isoformat()
        }
    ]


@pytest.fixture
def mock_sentence_transformer():
    """Create a mock sentence transformer model."""
    mock_model = MagicMock()
    mock_model.encode.return_value = np.random.randn(2, 384).astype(np.float32)
    mock_model.get_sentence_embedding_dimension.return_value = 384
    mock_model.device = 'cpu'
    return mock_model


@pytest.fixture
def mock_faiss_index():
    """Create a mock FAISS index."""
    index = MagicMock()
    index.d = 384
    index.ntotal = 10
    index.metric_type = faiss.METRIC_INNER_PRODUCT
    index.search.return_value = (
        np.array([[0.9, 0.8, 0.7]], dtype=np.float32),
        np.array([[0, 1, 2]], dtype=np.int64)
    )
    return index


@pytest.fixture
def sample_metadata():
    """Create sample metadata for FAISS index."""
    return {
        'vector_mapping': {
            0: {'doc_id': 0, 'chunk_index': 0},
            1: {'doc_id': 0, 'chunk_index': 1},
            2: {'doc_id': 1, 'chunk_index': 0}
        },
        'documents': {
            0: {
                'id': 0,
                'name': 'doc1.txt',
                'size': 100,
                'chunks': ['chunk 1 text', 'chunk 2 text'],
                'content': 'Full document content',
                'metadata': {},
                'updated_at': datetime.now().isoformat()
            },
            1: {
                'id': 1,
                'name': 'doc2.txt',
                'size': 150,
                'chunks': ['chunk 3 text'],
                'content': 'Another document',
                'metadata': {},
                'updated_at': datetime.now().isoformat()
            }
        },
        'config': {
            'model_name': 'test-model',
            'dimension': 384,
            'index_type': 'IndexFlatIP'
        }
    }


# ============================================================================
# Tests for index_builder_faiss.py
# ============================================================================

class TestDocumentIndexBuilder:
    """Test suite for DocumentIndexBuilder class."""
    
    def test_initialization(self):
        """Test DocumentIndexBuilder initialization."""
        with patch('index_builder_faiss.SentenceTransformer') as mock_st:
            mock_model = MagicMock()
            mock_model.get_sentence_embedding_dimension.return_value = 384
            mock_st.return_value = mock_model
            
            builder = DocumentIndexBuilder(
                model_name="test-model",
                chunk_size=512,
                overlap=50,
                device="cpu"
            )
            
            assert builder.model_name == "test-model"
            assert builder.chunk_size == 512
            assert builder.overlap == 50
            assert builder.dimension == 384
    
    def test_clean_html_content(self):
        """Test HTML content cleaning."""
        builder = DocumentIndexBuilder()
        
        # Test basic HTML cleaning
        html = """
        <html>
        <head><script>alert('test');</script></head>
        <body>
            <h1>Title</h1>
            <p>This is a <strong>test</strong> paragraph.</p>
            <nav>Navigation menu</nav>
            <div class="content">Main content here</div>
        </body>
        </html>
        """
        
        cleaned = builder.clean_html_content(html)
        
        # Should remove scripts and navigation
        assert 'alert' not in cleaned
        assert 'Navigation menu' not in cleaned
        
        # Should preserve main content
        assert 'Title' in cleaned
        assert 'test' in cleaned
        assert 'Main content' in cleaned
    
    def test_clean_html_with_lists(self):
        """Test HTML cleaning with lists."""
        builder = DocumentIndexBuilder()
        
        html = """
        <ul>
            <li>Item 1</li>
            <li>Item 2</li>
        </ul>
        <ol>
            <li>First</li>
            <li>Second</li>
        </ol>
        """
        
        cleaned = builder.clean_html_content(html)
        
        assert 'Item 1' in cleaned
        assert 'Item 2' in cleaned
        assert 'First' in cleaned
        assert 'Second' in cleaned
    
    def test_count_tokens(self):
        """Test token counting."""
        builder = DocumentIndexBuilder()
        
        text = "This is a test sentence."
        token_count = builder._count_tokens(text)
        
        # Should return a positive integer
        assert isinstance(token_count, int)
        assert token_count > 0
    
    def test_split_by_structure(self):
        """Test text splitting by structure."""
        builder = DocumentIndexBuilder()
        
        text = """Paragraph 1 content here.

Paragraph 2 with more text.

Another paragraph."""
        
        sections = builder._split_by_structure(text)
        
        assert len(sections) == 3
        assert 'Paragraph 1' in sections[0]
        assert 'Paragraph 2' in sections[1]
    
    @patch('index_builder_faiss.SentenceTransformer')
    def test_chunk_document(self, mock_st):
        """Test document chunking."""
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_st.return_value = mock_model
        
        builder = DocumentIndexBuilder(chunk_size=100, overlap=10)
        
        # Create a document with multiple sentences
        text = "First sentence. " * 20  # Create long text
        chunks = builder.chunk_document(text, doc_id=0)
        
        assert len(chunks) > 0
        assert all('text' in chunk for chunk in chunks)
        assert all('chunk_index' in chunk for chunk in chunks)
        assert all('doc_id' in chunk for chunk in chunks)
        assert all(chunk['doc_id'] == 0 for chunk in chunks)
    
    def test_load_documents_from_directory(self, temp_dir):
        """Test loading documents from directory."""
        # Create test files
        (temp_dir / 'test1.txt').write_text('Content 1')
        (temp_dir / 'test2.md').write_text('Content 2')
        (temp_dir / 'test3.html').write_text('<p>HTML content</p>')
        (temp_dir / 'ignored.pdf').write_text('PDF content')  # Should be ignored
        
        builder = DocumentIndexBuilder()
        docs = builder.load_documents_from_directory(temp_dir)
        
        assert len(docs) == 3  # Only txt, md, html files
        assert any(d['name'] == 'test1.txt' for d in docs)
        assert any(d['name'] == 'test2.md' for d in docs)
        assert any(d['name'] == 'test3.html' for d in docs)
    
    def test_load_documents_from_list(self):
        """Test loading documents from list."""
        builder = DocumentIndexBuilder()
        
        input_docs = [
            {'name': 'doc1', 'content': 'Content 1', 'metadata': {'key': 'value'}},
            {'name': 'doc2', 'content': 'Content 2'},
            {'content': ''},  # Empty content, should be skipped
        ]
        
        docs = builder.load_documents_from_list(input_docs)
        
        assert len(docs) == 2
        assert docs[0]['name'] == 'doc1'
        assert docs[0]['metadata'] == {'key': 'value'}
        assert docs[1]['name'] == 'doc2'
    
    @patch('index_builder_faiss.faiss.write_index')
    @patch('index_builder_faiss.SentenceTransformer')
    def test_build_index(self, mock_st, mock_write_index, temp_dir, sample_documents):
        """Test building FAISS index."""
        # Setup mocks
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_model.encode.return_value = np.random.randn(10, 384).astype(np.float32)
        mock_st.return_value = mock_model
        
        builder = DocumentIndexBuilder()
        
        # Build index
        builder.build_index(
            documents=sample_documents,
            output_path=temp_dir,
            index_name="test_index"
        )
        
        # Check that files would be created
        mock_write_index.assert_called_once()
        
        # Check metadata file was created
        metadata_file = temp_dir / "test_index.pkl"
        assert metadata_file.exists()
        
        # Load and verify metadata
        with open(metadata_file, 'rb') as f:
            metadata = pickle.load(f)
        
        assert 'vector_mapping' in metadata
        assert 'documents' in metadata
        assert 'config' in metadata
    
    def test_build_index_empty_documents(self):
        """Test building index with empty documents."""
        builder = DocumentIndexBuilder()
        
        with pytest.raises(ValueError, match="No documents provided"):
            builder.build_index([], "/tmp", "test")
    
    def test_process_large_section(self):
        """Test processing large sections that exceed chunk size."""
        builder = DocumentIndexBuilder(chunk_size=50, overlap=5)
        
        # Create a very long section
        large_section = "This is a very long sentence that will definitely exceed our chunk size. " * 10
        
        chunks = []
        builder._process_large_section(large_section, chunks, doc_id=0)
        
        assert len(chunks) > 1
        assert all(builder._count_tokens(c['text']) <= 50 for c in chunks)


# ============================================================================
# Tests for models.py
# ============================================================================

class TestModels:
    """Test suite for models module."""
    
    def test_document_chunk_creation(self):
        """Test DocumentChunk creation and methods."""
        chunk = DocumentChunk(
            document_id="doc1",
            chunk_index=0,
            content="Test content",
            metadata={'score': 0.95}
        )
        
        assert chunk.document_id == "doc1"
        assert chunk.chunk_index == 0
        assert chunk.content == "Test content"
        assert chunk.metadata['score'] == 0.95
        
        # Test to_dict method
        chunk_dict = chunk.to_dict()
        assert chunk_dict['document_id'] == "doc1"
        assert chunk_dict['content'] == "Test content"
    
    def test_document_creation(self):
        """Test Document creation."""
        doc = Document(
            id="doc1",
            name="test.txt",
            size=100,
            content="Test content",
            metadata={'key': 'value'},
            updated_at=datetime.now()
        )
        
        assert doc.id == "doc1"
        assert doc.name == "test.txt"
        assert doc.size == 100
        assert doc.content == "Test content"
        assert doc.metadata['key'] == 'value'
        
        # Test string representation
        str_rep = str(doc)
        assert "doc1" in str_rep
        assert "test.txt" in str_rep
    
    def test_document_from_file(self, temp_dir):
        """Test Document.from_file class method."""
        # Create a test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("File content", encoding='utf-8')
        
        doc = Document.from_file(test_file, document_id="custom_id")
        
        assert doc.id == "custom_id"
        assert doc.name == "test"
        assert doc.content == "File content"
        assert doc.metadata['file_extension'] == '.txt'
        assert isinstance(doc.updated_at, datetime)
    
    def test_document_to_dict(self):
        """Test Document.to_dict method."""
        now = datetime.now()
        doc = Document(
            id="doc1",
            name="test.txt",
            size=100,
            content="Test content",
            metadata={'key': 'value'},
            updated_at=now
        )
        
        doc_dict = doc.to_dict()
        
        assert doc_dict['id'] == "doc1"
        assert doc_dict['name'] == "test.txt"
        assert doc_dict['size'] == 100
        assert doc_dict['content'] == "Test content"
        assert doc_dict['metadata'] == {'key': 'value'}
        assert doc_dict['updated_at'] == now.isoformat()
    
    def test_search_engine_abstract_class(self):
        """Test SearchEngine abstract base class."""
        # Cannot instantiate abstract class
        with pytest.raises(TypeError):
            SearchEngine()
        
        # Test that subclass must implement abstract methods
        class IncompleteEngine(SearchEngine):
            pass
        
        with pytest.raises(TypeError):
            IncompleteEngine()


# ============================================================================
# Tests for search_engine_faiss.py
# ============================================================================

class TestModelSentenceTransformer:
    """Test suite for ModelSentenceTransformer."""
    
    @patch('search_engine_faiss.SentenceTransformer')
    def test_initialization(self, mock_st):
        """Test ModelSentenceTransformer initialization."""
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 768
        mock_model.device = 'cuda'
        mock_st.return_value = mock_model
        
        transformer = ModelSentenceTransformer(
            model_name="test-model",
            device="cuda"
        )
        
        assert transformer.model_name == "test-model"
        assert transformer.dimension == 768
        mock_st.assert_called_with("test-model", device="cuda")
    
    @patch('search_engine_faiss.SentenceTransformer')
    def test_encode_single_text(self, mock_st):
        """Test encoding single text."""
        mock_model = MagicMock()
        mock_model.encode.return_value = np.array([[1, 2, 3]], dtype=np.float32)
        mock_st.return_value = mock_model
        
        transformer = ModelSentenceTransformer()
        embeddings = transformer.encode("test text")
        
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.dtype == np.float32
        mock_model.encode.assert_called_once()
    
    @patch('search_engine_faiss.SentenceTransformer')
    def test_encode_multiple_texts(self, mock_st):
        """Test encoding multiple texts."""
        mock_model = MagicMock()
        mock_model.encode.return_value = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.float32)
        mock_st.return_value = mock_model
        
        transformer = ModelSentenceTransformer()
        embeddings = transformer.encode(["text1", "text2"])
        
        assert embeddings.shape == (2, 3)
        assert embeddings.dtype == np.float32
    
    @patch('search_engine_faiss.SentenceTransformer')
    def test_cleanup(self, mock_st):
        """Test cleanup method."""
        transformer = ModelSentenceTransformer()
        transformer.cleanup()
        
        assert transformer._model is None


class TestFaissSearchEngine:
    """Test suite for FaissSearchEngine."""
    
    def test_initialization(self):
        """Test FaissSearchEngine initialization."""
        engine = FaissSearchEngine(
            embedding_name="test",
            embedding_path="/tmp",
            model_name="test-model",
            device="cpu"
        )
        
        assert not engine.is_ready
        assert engine._index_path == Path("/tmp/test.faiss")
        assert engine._metadata_file == Path("/tmp/test.pkl")
        assert engine._model_name == "test-model"
    
    @patch('search_engine_faiss.pickle.load')
    @patch('search_engine_faiss.faiss.read_index')
    @patch('search_engine_faiss.ModelSentenceTransformer')
    def test_initialize_success(self, mock_transformer, mock_read_index, mock_pickle, temp_dir):
        """Test successful initialization."""
        # Create dummy files
        index_file = temp_dir / "test.faiss"
        metadata_file = temp_dir / "test.pkl"
        index_file.touch()
        metadata_file.touch()
        
        # Setup mocks
        mock_index = MagicMock()
        mock_index.d = 384
        mock_index.ntotal = 10
        mock_read_index.return_value = mock_index
        
        mock_transformer_instance = MagicMock()
        mock_transformer_instance.dimension = 384
        mock_transformer.return_value = mock_transformer_instance
        
        mock_pickle.return_value = {
            'vector_mapping': {},
            'documents': {},
            'config': {}
        }
        
        engine = FaissSearchEngine(
            embedding_name="test",
            embedding_path=str(temp_dir),
            model_name="test-model"
        )
        
        with patch('builtins.open', mock_open()):
            engine.initialize()
        
        assert engine.is_ready
        assert engine._index is not None
        assert engine._metadata is not None
    
    def test_initialize_missing_files(self):
        """Test initialization with missing files."""
        engine = FaissSearchEngine(
            embedding_name="nonexistent",
            embedding_path="/tmp",
            model_name="test-model"
        )
        
        with pytest.raises(FileNotFoundError):
            engine.initialize()
    
    @patch('search_engine_faiss.ModelSentenceTransformer')
    def test_search_for_chunks(self, mock_transformer, mock_faiss_index, sample_metadata):
        """Test searching for chunks."""
        # Setup mocks
        mock_transformer_instance = MagicMock()
        mock_transformer_instance.encode.return_value = np.array([[0.1, 0.2, 0.3]], dtype=np.float32)
        mock_transformer.return_value = mock_transformer_instance
        
        engine = FaissSearchEngine(
            embedding_name="test",
            embedding_path="/tmp",
            model_name="test-model"
        )
        
        # Manually set internal state
        engine._is_ready = True
        engine._index = mock_faiss_index
        engine._metadata = sample_metadata
        engine._sentence_transformer = mock_transformer_instance
        
        # Perform search
        chunks = engine.search_for_chunks("test query", top_k=3)
        
        assert len(chunks) == 3
        assert all(isinstance(c, DocumentChunk) for c in chunks)
        assert chunks[0].metadata['score'] > 0
    
    def test_search_for_documents(self, mock_faiss_index, sample_metadata):
        """Test searching for documents."""
        with patch('search_engine_faiss.ModelSentenceTransformer') as mock_transformer:
            mock_transformer_instance = MagicMock()
            mock_transformer_instance.encode.return_value = np.array([[0.1, 0.2, 0.3]], dtype=np.float32)
            mock_transformer.return_value = mock_transformer_instance
            
            engine = FaissSearchEngine(
                embedding_name="test",
                embedding_path="/tmp",
                model_name="test-model"
            )
            
            # Manually set internal state
            engine._is_ready = True
            engine._index = mock_faiss_index
            engine._metadata = sample_metadata
            engine._sentence_transformer = mock_transformer_instance
            
            # Perform search
            docs = engine.search_for_documents("test query", top_k=2)
            
            assert len(docs) <= 2
            assert all(isinstance(d, Document) for d in docs)
    
    def test_should_normalize_query(self, mock_faiss_index):
        """Test _should_normalize_query method."""
        engine = FaissSearchEngine(
            embedding_name="test",
            embedding_path="/tmp",
            model_name="test-model"
        )
        
        # Test with IndexFlatIP
        engine._index = mock_faiss_index
        engine._metadata = {'config': {'index_type': 'IndexFlatIP'}}
        assert engine._should_normalize_query()
        
        # Test with L2 metric
        mock_faiss_index.metric_type = faiss.METRIC_L2
        assert not engine._should_normalize_query()
    
    def test_cleanup(self):
        """Test cleanup method."""
        engine = FaissSearchEngine(
            embedding_name="test",
            embedding_path="/tmp",
            model_name="test-model"
        )
        
        # Create mock objects
        engine._index = MagicMock()
        engine._sentence_transformer = MagicMock()
        
        engine.cleanup()
        
        assert engine._index is None
        assert engine._sentence_transformer is None
    
    def test_get_status(self):
        """Test get_status method."""
        engine = FaissSearchEngine(
            embedding_name="test",
            embedding_path="/tmp",
            model_name="test-model"
        )
        
        # Not ready
        status = engine.get_status()
        assert "Not ready" in status[0]
        
        # Ready
        engine._is_ready = True
        status = engine.get_status()
        assert "Ready" in status[0]
    
    def test_doc_count(self, sample_metadata):
        """Test doc_count property."""
        engine = FaissSearchEngine(
            embedding_name="test",
            embedding_path="/tmp",
            model_name="test-model"
        )
        
        # No metadata
        assert engine.doc_count == 0
        
        # With metadata
        engine._metadata = sample_metadata
        assert engine.doc_count == 2


# ============================================================================
# Tests for server.py
# ============================================================================

class TestServerSettings:
    """Test suite for ServerSettings."""
    
    def test_default_settings(self):
        """Test default server settings."""
        settings = ServerSettings()
        
        assert settings.transport == "stdio"
        assert settings.host == "localhost"
        assert settings.port == 8000
        assert settings.model_name == "thenlper/gte-large"
    
    def test_custom_settings(self):
        """Test custom server settings."""
        settings = ServerSettings(
            transport="http",
            host="0.0.0.0",
            port=8080,
            model_name="custom-model"
        )
        
        assert settings.transport == "http"
        assert settings.host == "0.0.0.0"
        assert settings.port == 8080
        assert settings.model_name == "custom-model"
    
    def test_environment_variables(self, monkeypatch):
        """Test loading settings from environment variables."""
        monkeypatch.setenv("MCP_TRANSPORT", "https")
        monkeypatch.setenv("MCP_HOST", "192.168.1.1")
        monkeypatch.setenv("MCP_PORT", "9000")
        
        settings = ServerSettings()
        
        assert settings.transport == "https"
        assert settings.host == "192.168.1.1"
        assert settings.port == 9000


class TestMCPServer:
    """Test suite for MCPServer."""
    
    @patch('server.FaissSearchEngine')
    def test_initialization(self, mock_engine_class):
        """Test MCPServer initialization."""
        settings = ServerSettings()
        server = MCPServer(settings, device="cpu")
        
        assert server._settings == settings
        assert server._device == "cpu"
        assert not server._is_ready
        mock_engine_class.assert_called_once()
    
    @patch('server.FastMCP')
    @patch('server.FaissSearchEngine')
    def test_create_public_server_success(self, mock_engine_class, mock_fastmcp):
        """Test successful public server creation."""
        # Setup mocks
        mock_engine = MagicMock()
        mock_engine.doc_count = 10
        mock_engine_class.return_value = mock_engine
        
        mock_mcp_instance = MagicMock()
        mock_fastmcp.return_value = mock_mcp_instance
        
        settings = ServerSettings()
        server = MCPServer(settings)
        
        # Create server
        result = server.create_public_server()
        
        assert result is not None
        assert server._is_ready
        mock_engine.initialize.assert_called_once()
        mock_fastmcp.assert_called_once()
    
    @patch('server.FaissSearchEngine')
    def test_create_public_server_failure(self, mock_engine_class):
        """Test failed public server creation."""
        # Setup mock to raise exception
        mock_engine = MagicMock()
        mock_engine.initialize.side_effect = Exception("Init failed")
        mock_engine_class.return_value = mock_engine
        
        settings = ServerSettings()
        server = MCPServer(settings)
        
        # Create server
        result = server.create_public_server()
        
        assert result is None
        assert not server._is_ready
        assert server._initialization_error == "Init failed"
    
    @patch('server.FastMCP')
    @patch('server.FaissSearchEngine')
    def test_search_tools_registration(self, mock_engine_class, mock_fastmcp):
        """Test that search tools are properly registered."""
        mock_engine = MagicMock()
        mock_engine.doc_count = 5
        mock_engine_class.return_value = mock_engine
        
        # Track tool registrations
        registered_tools = {}
        
        def mock_tool(name=None, description=None):
            def decorator(func):
                registered_tools[name or func.__name__] = func
                return func
            return decorator
        
        mock_mcp_instance = MagicMock()
        mock_mcp_instance.tool = mock_tool
        mock_fastmcp.return_value = mock_mcp_instance
        
        settings = ServerSettings()
        server = MCPServer(settings)
        server.create_public_server()
        
        # Check that tools were registered
        assert 'search_for_chunks' in registered_tools
        assert 'search_for_documents' in registered_tools
        assert 'health_check' in registered_tools
    
    @patch('server.MCPServer.create_public_server')
    def test_run_stdio_server(self, mock_create_server):
        """Test running server in stdio mode."""
        mock_server = MagicMock()
        mock_create_server.return_value = mock_server
        
        settings = ServerSettings(transport="stdio")
        server = MCPServer(settings)
        
        server.run_stdio_server()
        
        mock_create_server.assert_called_once()
        mock_server.run.assert_called_once()
    
    @patch('server.uvicorn.run')
    @patch('server.FastApp')
    @patch('server.MCPServer.create_public_server')
    def test_run_http_server(self, mock_create_server, mock_fast_app, mock_uvicorn):
        """Test running server in HTTP mode."""
        mock_mcp = MagicMock()
        mock_create_server.return_value = mock_mcp
        
        mock_app_instance = MagicMock()
        mock_app_instance.create_app.return_value = MagicMock()
        mock_fast_app.return_value = mock_app_instance
        
        settings = ServerSettings(transport="http")
        server = MCPServer(settings)
        
        server.run_http_server_with_mcp()
        
        mock_create_server.assert_called_once()
        mock_uvicorn.assert_called_once()


class TestFastApp:
    """Test suite for FastApp."""
    
    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
    def test_create_app(self):
        """Test FastAPI app creation."""
        from fastapi import FastAPI
        
        # Create mock MCP server
        mock_mcp = MagicMock()
        mock_mcp.name = "test-server"
        mock_mcp.instructions = "Test instructions"
        mock_mcp.session_manager.run = AsyncMock()
        mock_mcp.streamable_http_app.return_value = MagicMock()
        
        settings = ServerSettings()
        app_settings = FastAppSettings(settings, mock_mcp)
        fast_app = FastApp(app_settings)
        
        app = fast_app.create_app()
        
        assert isinstance(app, FastAPI)
        assert len(app.routes) > 0


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for the complete system."""
    
    @pytest.mark.integration
    def test_end_to_end_index_and_search(self, temp_dir):
        """Test complete flow from indexing to searching."""
        # Step 1: Create documents
        docs_dir = temp_dir / "docs"
        docs_dir.mkdir()
        (docs_dir / "doc1.txt").write_text("Python is a programming language for AI")
        (docs_dir / "doc2.txt").write_text("Machine learning requires data and algorithms")
        
        # Step 2: Build index
        with patch('index_builder_faiss.SentenceTransformer') as mock_st:
            mock_model = MagicMock()
            mock_model.get_sentence_embedding_dimension.return_value = 384
            mock_model.encode.return_value = np.random.randn(10, 384).astype(np.float32)
            mock_st.return_value = mock_model
            
            builder = DocumentIndexBuilder()
            documents = builder.load_documents_from_directory(docs_dir)
            builder.build_index(documents, temp_dir, "test_index")
        
        # Step 3: Initialize search engine
        with patch('search_engine_faiss.ModelSentenceTransformer') as mock_transformer:
            with patch('search_engine_faiss.faiss.read_index') as mock_read:
                mock_index = MagicMock()
                mock_index.d = 384
                mock_index.ntotal = 10
                mock_index.search.return_value = (
                    np.array([[0.9]], dtype=np.float32),
                    np.array([[0]], dtype=np.int64)
                )
                mock_read.return_value = mock_index
                
                mock_transformer_instance = MagicMock()
                mock_transformer_instance.dimension = 384
                mock_transformer_instance.encode.return_value = np.array([[0.1, 0.2, 0.3]], dtype=np.float32)
                mock_transformer.return_value = mock_transformer_instance
                
                engine = FaissSearchEngine(
                    embedding_name="test_index",
                    embedding_path=str(temp_dir),
                    model_name="test-model"
                )
                engine.initialize()
                
                # Step 4: Search
                chunks = engine.search_for_chunks("Python", top_k=1)
                assert len(chunks) > 0
    
    @pytest.mark.integration
    def test_server_with_search_engine(self, temp_dir):
        """Test server integration with search engine."""
        # Create minimal index files
        index_file = temp_dir / "test.faiss"
        metadata_file = temp_dir / "test.pkl"
        
        # Create a simple FAISS index
        index = faiss.IndexFlatIP(384)
        index.add(np.random.randn(5, 384).astype(np.float32))
        faiss.write_index(index, str(index_file))
        
        # Create metadata
        metadata = {
            'vector_mapping': {i: {'doc_id': i, 'chunk_index': 0} for i in range(5)},
            'documents': {
                i: {
                    'id': i,
                    'name': f'doc{i}.txt',
                    'size': 100,
                    'chunks': [f'chunk {i}'],
                    'content': f'Document {i} content',
                    'metadata': {},
                    'updated_at': datetime.now().isoformat()
                } for i in range(5)
            },
            'config': {
                'model_name': 'test-model',
                'dimension': 384,
                'index_type': 'IndexFlatIP'
            }
        }
        
        with open(metadata_file, 'wb') as f:
            pickle.dump(metadata, f)
        
        # Create server with search engine
        with patch('search_engine_faiss.ModelSentenceTransformer'):
            settings = ServerSettings(
                embedding_name="test",
                embedding_path=str(temp_dir)
            )
            server = MCPServer(settings)
            
            with patch('server.FastMCP') as mock_fastmcp:
                mock_mcp_instance = MagicMock()
                mock_fastmcp.return_value = mock_mcp_instance
                
                result = server.create_public_server()
                assert result is not None


# ============================================================================
# Performance Tests
# ============================================================================

class TestPerformance:
    """Performance and stress tests."""
    
    @pytest.mark.performance
    def test_large_document_chunking(self):
        """Test chunking performance with large documents."""
        builder = DocumentIndexBuilder(chunk_size=512, overlap=50)
        
        # Create a very large document (10MB)
        large_text = "This is a test sentence. " * 100000
        
        import time
        start = time.time()
        chunks = builder.chunk_document(large_text, doc_id=0)
        duration = time.time() - start
        
        assert len(chunks) > 100
        assert duration < 10  # Should complete within 10 seconds
    
    @pytest.mark.performance
    def test_concurrent_searches(self):
        """Test concurrent search operations."""
        import concurrent.futures
        
        with patch('search_engine_faiss.ModelSentenceTransformer'):
            engine = FaissSearchEngine(
                embedding_name="test",
                embedding_path="/tmp",
                model_name="test-model"
            )
            
            # Mock the internal state
            engine._is_ready = True
            engine._index = MagicMock()
            engine._index.ntotal = 1000
            engine._index.search.return_value = (
                np.array([[0.9]], dtype=np.float32),
                np.array([[0]], dtype=np.int64)
            )
            engine._metadata = {
                'vector_mapping': {0: {'doc_id': 0, 'chunk_index': 0}},
                'documents': {
                    0: {
                        'id': 0,
                        'name': 'doc.txt',
                        'size': 100,
                        'chunks': ['test chunk'],
                        'content': 'test content',
                        'metadata': {},
                        'updated_at': datetime.now().isoformat()
                    }
                }
            }
            engine._sentence_transformer = MagicMock()
            engine._sentence_transformer.encode.return_value = np.random.randn(1, 384).astype(np.float32)
            
            # Run concurrent searches
            def search_task():
                return engine.search_for_chunks("test query", top_k=1)
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(search_task) for _ in range(100)]
                results = [f.result() for f in futures]
            
            assert len(results) == 100
            assert all(len(r) > 0 for r in results)


# ============================================================================
# Edge Cases and Error Handling Tests
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_search_query(self):
        """Test handling of empty search queries."""
        engine = FaissSearchEngine(
            embedding_name="test",
            embedding_path="/tmp",
            model_name="test-model"
        )
        
        # Should handle gracefully
        with patch.object(engine, '_search_for_chunks_internal', return_value=[]):
            result = engine.search_for_chunks("", top_k=10)
            assert result == []
    
    def test_invalid_vector_ids(self, mock_faiss_index, sample_metadata):
        """Test handling of invalid vector IDs from FAISS."""
        mock_faiss_index.search.return_value = (
            np.array([[0.9, 0.8]], dtype=np.float32),
            np.array([[-1, 999]], dtype=np.int64)  # Invalid IDs
        )
        
        with patch('search_engine_faiss.ModelSentenceTransformer'):
            engine = FaissSearchEngine(
                embedding_name="test",
                embedding_path="/tmp",
                model_name="test-model"
            )
            
            engine._is_ready = True
            engine._index = mock_faiss_index
            engine._metadata = sample_metadata
            engine._sentence_transformer = MagicMock()
            engine._sentence_transformer.encode.return_value = np.random.randn(1, 384).astype(np.float32)
            
            chunks = engine.search_for_chunks("test", top_k=2)
            assert len(chunks) == 0  # Should skip invalid IDs
    
    def test_corrupted_metadata(self, temp_dir):
        """Test handling of corrupted metadata file."""
        # Create valid index file
        index_file = temp_dir / "test.faiss"
        index = faiss.IndexFlatIP(384)
        faiss.write_index(index, str(index_file))
        
        # Create corrupted metadata file
        metadata_file = temp_dir / "test.pkl"
        metadata_file.write_bytes(b"corrupted data")
        
        engine = FaissSearchEngine(
            embedding_name="test",
            embedding_path=str(temp_dir),
            model_name="test-model"
        )
        
        with pytest.raises(Exception):
            engine.initialize()
    
    def test_dimension_mismatch(self, temp_dir):
        """Test handling of dimension mismatch between model and index."""
        # Create index with different dimension
        index_file = temp_dir / "test.faiss"
        index = faiss.IndexFlatIP(512)  # Different dimension
        faiss.write_index(index, str(index_file))
        
        metadata_file = temp_dir / "test.pkl"
        with open(metadata_file, 'wb') as f:
            pickle.dump({'vector_mapping': {}, 'documents': {}}, f)
        
        with patch('search_engine_faiss.ModelSentenceTransformer') as mock_transformer:
            mock_instance = MagicMock()
            mock_instance.dimension = 384  # Different from index
            mock_transformer.return_value = mock_instance
            
            engine = FaissSearchEngine(
                embedding_name="test",
                embedding_path=str(temp_dir),
                model_name="test-model"
            )
            
            with pytest.raises(ValueError, match="dimension mismatch"):
                engine.initialize()


# ============================================================================
# Main test runner
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])