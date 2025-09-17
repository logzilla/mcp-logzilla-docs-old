# test_search_engine_faiss.py

import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from pathlib import Path

# Assume search_engine_faiss.py contains a FaissSearchEngine class
# We need to import it for testing.
from search_engine_faiss import FaissSearchEngine

# Use the mock model/tokenizer for all tests in this file
pytestmark = pytest.mark.usefixtures("mock_tokenizer_and_model")

class TestFaissSearchEngine:
    """Tests for the FaissSearchEngine class."""

    def test_initialization_success(self, mock_index_files):
        """Verify the engine loads index and metadata files correctly."""
        index_path, metadata_path = mock_index_files
        engine = FaissSearchEngine(index_path, metadata_path)

        assert engine.index is not None
        assert engine.index.ntotal == 3  # From mock_index_files
        assert engine.metadata is not None
        assert 'vector_mapping' in engine.metadata
        assert engine.model is not None
        assert engine.dimension == 1024

    def test_initialization_file_not_found(self, tmp_path):
        """Ensure FileNotFoundError is raised if files are missing."""
        with pytest.raises(FileNotFoundError):
            FaissSearchEngine(
                tmp_path / "nonexistent.faiss",
                tmp_path / "nonexistent.pkl"
            )

    def test_search_happy_path(self, mock_index_files):
        """
        Test a standard search query, mocking the FAISS search call to ensure
        the result mapping logic is correct.
        """
        index_path, metadata_path = mock_index_files
        engine = FaissSearchEngine(index_path, metadata_path)
        
        # Mock the actual search on the index to return predictable results
        # Return indices for vector 2, then 0. Score 0.9 and 0.85
        mock_distances = np.array([[0.9, 0.85]], dtype='float32')
        mock_indices = np.array([[2, 0]]) # Vector 2 (doc_beta), Vector 0 (doc_alpha)
        engine.index.search = MagicMock(return_value=(mock_distances, mock_indices))

        query = "find beta content"
        results = engine.search(query, k=2)

        # Verify the search method was called correctly
        engine.index.search.assert_called_once()
        # The first argument to search is the query vector, second is k
        assert engine.index.search.call_args[0][1] == 2

        # Verify the results are correctly mapped and ordered
        assert len(results) == 2
        
        # First result should correspond to index 2
        assert results[0]['score'] == 0.9
        assert results[0]['document_name'] == 'doc_beta.md'
        assert results[0]['content'] == 'First chunk of beta.'
        
        # Second result should correspond to index 0
        assert results[1]['score'] == 0.85
        assert results[1]['document_name'] == 'doc_alpha.txt'
        assert results[1]['content'] == 'First chunk of alpha.'
        
    def test_search_with_empty_query(self, mock_index_files):
        """An empty or whitespace query should return no results."""
        index_path, metadata_path = mock_index_files
        engine = FaissSearchEngine(index_path, metadata_path)
        
        results = engine.search("   ")
        assert results == []

    def test_search_no_results_found(self, mock_index_files):
        """Test the case where FAISS returns no valid indices (-1)."""
        index_path, metadata_path = mock_index_files
        engine = FaissSearchEngine(index_path, metadata_path)

        # FAISS returns -1 for indices when no neighbors are found within the radius (for IndexIVF)
        # or for empty results.
        mock_distances = np.array([[]], dtype='float32')
        mock_indices = np.array([[-1, -1]]) 
        engine.index.search = MagicMock(return_value=(mock_distances, mock_indices))

        results = engine.search("some obscure query")
        assert results == []