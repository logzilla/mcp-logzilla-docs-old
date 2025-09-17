# test_server.py

import pytest
from unittest.mock import patch, MagicMock

# Assuming server.py is a FastAPI app
from fastapi.testclient import TestClient

# We need to import the app object from server.py
# This might fail if server.py runs code at the global scope.
# It's best practice to have the app creation in a factory function.
# For this example, we assume `from server import app` works.
from server import app

# Create a client to interact with the FastAPI app
client = TestClient(app)

@patch('server.FaissSearchEngine')
def test_search_endpoint_success(mock_search_engine_class):
    """Test the /api/search endpoint with a valid query."""
    # Configure the mock
    mock_engine_instance = MagicMock()
    mock_results = [
        {'score': 0.95, 'document_name': 'doc1.txt', 'content': 'Test content', 'document_id': 1},
    ]
    mock_engine_instance.search.return_value = mock_results
    
    # This patch makes the `search_engine` variable in `server.py` use our mock
    with patch('server.search_engine', mock_engine_instance):
        response = client.get("/api/search?q=test_query&k=1")

        # Assertions
        assert response.status_code == 200
        assert response.json() == mock_results
        mock_engine_instance.search.assert_called_once_with(query="test_query", k=1)

@patch('server.search_engine')
def test_search_endpoint_no_results(mock_search_engine):
    """Test the search endpoint when the engine returns no results."""
    mock_search_engine.search.return_value = []
    
    response = client.get("/api/search?q=no_results_query")
    
    assert response.status_code == 200
    assert response.json() == []

def test_search_endpoint_no_query_param():
    """Test that a 422 error is returned if the 'q' parameter is missing."""
    response = client.get("/api/search")
    assert response.status_code == 422 # Unprocessable Entity

def test_search_endpoint_empty_query_param():
    """Test that a 422 error is returned if 'q' is empty."""
    response = client.get("/api/search?q=")
    assert response.status_code == 422

@patch('server.search_engine')
def test_search_engine_not_loaded(mock_search_engine):
    """Test the 503 error when the search engine failed to load."""
    with patch('server.search_engine', None):
        response = client.get("/api/search?q=test")
        assert response.status_code == 503
        assert response.json() == {"detail": "Search engine is not available."}
        
@patch('server.search_engine')
def test_search_internal_error(mock_search_engine):
    """Test the 500 error when the search method raises an exception."""
    mock_search_engine.search.side_effect = Exception("Something broke")
    
    response = client.get("/api/search?q=test")
    assert response.status_code == 500
    assert "An error occurred during search" in response.json()['detail']

def test_health_check_endpoint():
    """Test the /health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    # The actual value of 'search_engine_loaded' depends on the test runner's state,
    # so we just check for the presence of the key.
    assert "status" in response.json()
    assert "search_engine_loaded" in response.json()