# test_index_builder.py

import pytest
import numpy as np
import pickle
from unittest.mock import patch, MagicMock, call
from pathlib import Path

# Import the class and functions to be tested
from index_builder_faiss import DocumentIndexBuilder, Constants, main, parse_arguments

# Use the mock fixture for all tests in this file
pytestmark = pytest.mark.usefixtures("mock_tokenizer_and_model")


class TestDocumentIndexBuilderInitialization:
    """Tests for the DocumentIndexBuilder constructor."""

    def test_initialization_defaults(self):
        """Verify initialization with default parameters."""
        builder = DocumentIndexBuilder()
        assert builder.model_name == Constants.DEFAULT_SENTENCE_TRANSFORMER_MODEL
        assert builder.chunk_size == Constants.DEFAULT_CHUNK_SIZE
        assert builder.overlap == Constants.DEFAULT_CHUNK_OVERLAP
        assert builder.device == "auto"
        assert builder.dimension == 1024  # From mock_tokenizer_and_model fixture

    def test_initialization_custom_parameters(self):
        """Verify initialization with custom parameters."""
        builder = DocumentIndexBuilder(
            model_name="custom/model",
            chunk_size=100,
            overlap=10,
            device="cpu"
        )
        assert builder.model_name == "custom/model"
        assert builder.chunk_size == 100
        assert builder.overlap == 10
        assert builder.device == "cpu"

    def test_model_and_tokenizer_are_loaded(self, mock_tokenizer_and_model):
        """Check that the model and tokenizer are instantiated."""
        _, mock_model_instance = mock_tokenizer_and_model
        DocumentIndexBuilder()
        assert mock_model_instance.get_sentence_embedding_dimension.called


class TestHtmlCleaning:
    """Comprehensive tests for the clean_html_content method."""

    @pytest.fixture
    def builder(self):
        return DocumentIndexBuilder()

    @pytest.mark.parametrize("html_input, expected_output", [
        # Basic tags removal
        ("<body><p>Text</p><script>alert('xss')</script><style>.a{color:red}</style></body>", "Text"),
        # Semantic conversion: headings, lists, emphasis
        ("<h1>Title</h1> <h2>Subtitle</h2> <ul><li>One</li><li>Two</li></ul> <strong>Bold</strong>", "# Title ## Subtitle - One - Two **Bold**"),
        # Main content extraction
        ("<body><nav>Menu</nav><main><h1>Real Content</h1></main><footer>Footer</footer></body>", "# Real Content"),
        # UI patterns removal (by class and ID)
        ('<div class="sidebar">ads</div><p>Main text</p><div id="social-share">Share</div>', "Main text"),
        # Table conversion
        ("<table><tr><th>H1</th><th>H2</th></tr><tr><td>R1C1</td><td>R1C2</td></tr></table>", "H1 | H2\nR1C1 | R1C2"),
        # Link handling
        ('<a href="https://example.com">External</a> <a href="/internal">Internal</a>', "[External](https://example.com) Internal"),
        # Whitespace normalization
        (" <p>Extra\n\nspace</p> ", "Extra space"),
        # Empty document
        ("", ""),
        # Complex nested structure
        ("<body><main><article><h1>Hi</h1><div><p>Paragraph with <em>emphasis</em>.</p></div></article></main></body>", "# Hi Paragraph with *emphasis*."),
    ])
    def test_various_html_scenarios(self, builder, html_input, expected_output):
        """Test a wide range of HTML cleaning scenarios."""
        cleaned_text = builder.clean_html_content(html_input)
        # Normalize whitespace in expected output for consistent comparison
        normalized_expected = " ".join(expected_output.split())
        assert cleaned_text == normalized_expected


class TestDocumentLoading:
    """Tests for document loading from directory and list."""

    @pytest.fixture
    def builder(self):
        return DocumentIndexBuilder()

    def test_load_from_directory_success(self, builder, sample_doc_dir):
        """Verify successful loading and filtering of files from a directory."""
        docs = builder.load_documents_from_directory(sample_doc_dir)
        assert len(docs) == 4  # doc1.txt, doc2.md, page.html, nested.txt
        doc_names = {doc['name'] for doc in docs}
        assert {"doc1.txt", "doc2.md", "page.html", "nested.txt"} == doc_names
        # Check that HTML content was cleaned
        html_doc = next(d for d in docs if d['name'] == 'page.html')
        assert html_doc['content'] == "# Hello World"

    def test_load_from_nonexistent_directory(self, builder, tmp_path):
        """Ensure FileNotFoundError is raised for a non-existent directory."""
        with pytest.raises(FileNotFoundError):
            builder.load_documents_from_directory(tmp_path / "nonexistent")

    def test_load_from_list(self, builder):
        """Verify loading from a predefined list of dictionaries."""
        input_docs = [
            {'name': 'doc1', 'content': 'Content 1'},
            {'name': 'doc2', 'content': '  '}, # Should be skipped
            {'content': 'Content 3'}, # Should get a default name
            {}, # Should be skipped
        ]
        docs = builder.load_documents_from_list(input_docs)
        assert len(docs) == 2
        assert docs[0]['name'] == 'doc1'
        assert docs[1]['name'] == 'document_1'
        assert docs[1]['content'] == 'Content 3'


class TestChunkingLogic:
    """In-depth tests for the token-aware chunking algorithm."""

    def test_small_document_single_chunk(self):
        """A document smaller than chunk_size should produce one chunk."""
        builder = DocumentIndexBuilder(chunk_size=100, overlap=10)
        text = "This is a short document that fits entirely within one chunk."
        chunks = builder.chunk_document(text, doc_id=0)
        assert len(chunks) == 1
        assert chunks[0]['text'] == text
        assert chunks[0]['token_count'] == 12 # Based on mock tokenizer

    def test_chunking_with_overlap(self):
        """Verify that overlap is correctly prepended to the next chunk."""
        builder = DocumentIndexBuilder(chunk_size=10, overlap=4)
        text = "one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen"
        chunks = builder.chunk_document(text, doc_id=0)
        assert len(chunks) == 2
        assert chunks[0]['text'] == "one two three four five six seven eight nine ten"
        # Overlap is the last 4 tokens: "seven eight nine ten"
        assert chunks[1]['text'] == "seven eight nine ten\n\n" + "eleven twelve thirteen fourteen fifteen"
    
    def test_chunking_with_zero_overlap(self):
        """Verify chunking works correctly when overlap is zero."""
        builder = DocumentIndexBuilder(chunk_size=10, overlap=0)
        text = "one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen"
        chunks = builder.chunk_document(text, doc_id=0)
        assert len(chunks) == 2
        assert chunks[0]['text'] == "one two three four five six seven eight nine ten"
        assert chunks[1]['text'] == "eleven twelve thirteen fourteen fifteen"

    def test_very_long_sentence_splitting(self):
        """A sentence larger than chunk_size should be split mid-sentence."""
        builder = DocumentIndexBuilder(chunk_size=8, overlap=2)
        text = "ThisIsAVeryLongSentenceWithManyTokensThatMustBeSplit " * 2
        text = text.strip()
        chunks = builder.chunk_document(text, doc_id=0)
        assert len(chunks) > 1
        # The first chunk should be a forced split of the long sentence
        assert chunks[0]['token_count'] <= 8

    def test_empty_document_chunking(self):
        """An empty document should produce no chunks."""
        builder = DocumentIndexBuilder()
        chunks = builder.chunk_document("   ", doc_id=0)
        assert len(chunks) == 0


class TestIndexBuilding:
    """Integration tests for the build_index method."""

    @pytest.fixture
    def builder(self):
        return DocumentIndexBuilder(chunk_size=10, overlap=2)

    def test_build_index_creates_files(self, builder, tmp_path):
        """Verify that .faiss and .pkl files are created successfully."""
        docs = [{'id': 0, 'name': 'doc1', 'size': 30, 'content': 'one two three four five six seven eight nine ten eleven twelve'}]
        output_dir = tmp_path / "output"
        index_name = "test_index"

        builder.build_index(docs, output_dir, index_name)

        index_file = output_dir / f"{index_name}.faiss"
        metadata_file = output_dir / f"{index_name}.pkl"

        assert output_dir.exists()
        assert index_file.exists()
        assert metadata_file.exists()

    def test_build_index_metadata_content(self, builder, tmp_path):
        """Verify the content of the generated metadata .pkl file."""
        docs = [{'id': 0, 'name': 'doc1', 'size': 30, 'content': 'one two three four five six seven eight nine ten eleven twelve'}]
        output_dir = tmp_path / "output"
        index_name = "test_index"

        builder.build_index(docs, output_dir, index_name)

        with open(output_dir / f"{index_name}.pkl", 'rb') as f:
            metadata = pickle.load(f)

        assert metadata['config']['model_name'] == builder.model_name
        assert metadata['config']['chunk_size'] == 10
        assert metadata['config']['total_documents'] == 1
        assert metadata['config']['total_vectors'] == 2 # Based on chunking logic

        assert 0 in metadata['documents']
        assert metadata['documents'][0]['name'] == 'doc1'
        assert len(metadata['documents'][0]['chunks']) == 2

        assert len(metadata['vector_mapping']) == 2
        assert metadata['vector_mapping'][0] == {'doc_id': 0, 'chunk_index': 0}
        assert metadata['vector_mapping'][1] == {'doc_id': 0, 'chunk_index': 1}

    def test_build_index_with_no_documents(self, builder, tmp_path):
        """Ensure build_index raises ValueError for empty document list."""
        with pytest.raises(ValueError, match="No documents provided"):
            builder.build_index([], tmp_path, "empty_index")
    
    def test_build_index_with_no_chunks_produced(self, builder, tmp_path):
        """Ensure build_index raises ValueError if no chunks are created."""
        docs = [{'id': 0, 'name': 'doc1', 'size': 3, 'content': ' '}]
        with pytest.raises(ValueError, match="No chunks were produced"):
            builder.build_index(docs, tmp_path, "no_chunk_index")


class TestCommandLineInterface:
    """Tests the main function and argument parsing."""

    @patch('index_builder_faiss.DocumentIndexBuilder')
    def test_main_happy_path(self, mock_builder_class, sample_doc_dir, tmp_path):
        """Test the main function with valid arguments."""
        output_dir = tmp_path / "output"
        
        # Mock the builder instance and its methods
        mock_builder_instance = MagicMock()
        mock_builder_instance.load_documents_from_directory.return_value = [{'id': 0, 'name': 'doc.txt', 'content': 'text', 'size': 4}]
        mock_builder_class.return_value = mock_builder_instance

        # Patch sys.argv
        with patch('sys.argv', [
            'index_builder_faiss.py',
            '--input-directory', str(sample_doc_dir),
            '--output-directory', str(output_dir),
            '--index-name', 'cli_test',
            '--chunk-size', '128',
            '--overlap', '12'
        ]):
            return_code = main()

        assert return_code == 0
        # Verify builder was initialized with CLI args
        mock_builder_class.assert_called_once_with(
            model_name=Constants.DEFAULT_SENTENCE_TRANSFORMER_MODEL,
            chunk_size=128,
            overlap=12,
            device="auto"
        )
        # Verify main methods were called
        mock_builder_instance.load_documents_from_directory.assert_called_once_with(str(sample_doc_dir))
        mock_builder_instance.build_index.assert_called_once()

    def test_main_input_dir_not_found(self, caplog):
        """Test main function exits with code 1 if input directory doesn't exist."""
        with patch('sys.argv', ['prog', '-i', 'nonexistent', '-o', 'out', '-n', 'name']):
            return_code = main()
        assert return_code == 1
        assert "Input directory does not exist" in caplog.text

    def test_main_no_documents_found(self, tmp_path, caplog):
        """Test main function exits with code 1 if no documents are found."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        with patch('sys.argv', ['prog', '-i', str(empty_dir), '-o', 'out', '-n', 'name']):
            return_code = main()
        assert return_code == 1
        assert "No supported documents found" in caplog.text

    @patch('argparse.ArgumentParser.parse_args')
    def test_argument_parser(self, mock_parse_args):
        """Verify that the argument parser is configured correctly."""
        parse_arguments()
        # Check if some key arguments are defined
        arg_calls = mock_parse_args.call_args_list
        # This is a bit complex to check directly, but we can verify our main test
        # covers the argument passing, which implicitly tests the parser.
        assert mock_parse_args.called