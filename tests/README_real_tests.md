# Real Implementation Tests

This directory contains tests that use actual libraries instead of stubs, providing higher confidence in the test results.

## Test Structure

### Configuration Files
- `test_config.py` - Central configuration for test parameters, model names, and sample data
- `conftest_real.py` - Real library fixtures and test environment setup

### Test Files
- `test_models.py` - Basic model tests (no changes needed, already real)
- `test_index_builder_real.py` - Real tests for document indexing with actual sentence transformers and FAISS
- `test_search_engine_real.py` - Real tests for search functionality with actual embeddings
- `test_server_real.py` - Real tests for MCP server with actual components
- `test_server_app_factory_real.py` - Real tests for FastAPI app factory
- `test_integration_real.py` - End-to-end integration tests

### Legacy Files (Stub-based)
- `conftest.py` - Original stub-based configuration (kept for reference)
- `test_*.py` (original files) - Stub-based tests (kept for reference)

## Running Tests

### Quick Tests (Real Libraries, No Slow Operations)
```bash
pytest tests/test_*_real.py -m "not slow"
```

### Full Test Suite (Including Slow Tests)
```bash
pytest tests/test_*_real.py
```

### Specific Test Categories
```bash
# Unit tests only
pytest tests/test_*_real.py -m "unit"

# Integration tests only  
pytest tests/test_*_real.py -m "integration"

# Skip slow tests
pytest tests/test_*_real.py -m "not slow"
```

### Environment Variables

Set these environment variables to customize test behavior:

- `TEST_MODEL_NAME` - Sentence transformer model to use (default: `sentence-transformers/all-MiniLM-L6-v2`)
- `TEST_DEVICE` - Device for model inference (default: `cpu`)
- `SKIP_SLOW_TESTS` - Set to `true` to skip slow tests (default: `false`)
- `KEEP_TEST_DATA` - Set to `true` to keep test data after tests complete

### Example Commands

```bash
# Run with custom model
TEST_MODEL_NAME="sentence-transformers/all-mpnet-base-v2" pytest tests/test_*_real.py

# Run on GPU (if available)
TEST_DEVICE="cuda" pytest tests/test_*_real.py

# Skip slow tests for faster feedback
SKIP_SLOW_TESTS=true pytest tests/test_*_real.py

# Keep test data for inspection
KEEP_TEST_DATA=true pytest tests/test_*_real.py -s
```

## Test Data

The tests use realistic sample documents:
- `python_basics.md` - Programming tutorial content
- `machine_learning.md` - AI/ML overview content  
- `web_development.html` - Web development guide with HTML structure

These documents are automatically created in temporary directories during test runs.

## Performance Considerations

### Slow Tests
Tests marked with `@pytest.mark.slow` involve:
- Downloading and loading sentence transformer models
- Building FAISS indices with real embeddings
- End-to-end search operations

These tests provide the highest confidence but take longer to run.

### Fast Tests
Unmarked tests focus on:
- Configuration and setup
- Error handling
- Basic functionality without heavy computation

## Dependencies

Real tests require all production dependencies:
- `sentence-transformers` - For embedding generation
- `faiss-cpu` - For vector similarity search
- `tiktoken` - For tokenization
- `beautifulsoup4` - For HTML processing
- `pydantic` - For configuration validation
- `fastapi` - For web server tests
- `httpx` - For HTTP client testing

## Confidence Improvements

Compared to stub-based tests, real implementation tests provide:

1. **Actual Library Behavior** - Tests use real sentence transformers, FAISS indices, and tokenizers
2. **Real Data Processing** - HTML cleaning, text chunking, and embedding generation use production code paths
3. **Semantic Search Validation** - Tests verify that semantically related queries return relevant documents
4. **Performance Characteristics** - Tests reveal actual memory usage and processing times
5. **Integration Validation** - End-to-end tests ensure all components work together correctly
6. **Error Handling** - Tests use real error conditions from actual libraries

## Migration from Stubs

The original stub-based tests are preserved for reference. Key differences:

| Aspect | Stub Tests | Real Tests |
|--------|------------|------------|
| Model Loading | Fake 8-dimensional vectors | Real sentence transformer models |
| Tokenization | Simple word splitting | Real tiktoken encoding |
| HTML Processing | Basic text extraction | Full BeautifulSoup processing |
| FAISS Operations | In-memory array operations | Real FAISS index operations |
| Search Quality | Synthetic similarity scores | Actual semantic similarity |
| Performance | Instant execution | Realistic processing times |

## Troubleshooting

### Model Download Issues
If tests fail due to model download problems:
```bash
# Pre-download models
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
```

### Memory Issues
For memory-constrained environments:
```bash
# Use smaller model
TEST_MODEL_NAME="sentence-transformers/all-MiniLM-L12-v2" pytest tests/test_*_real.py
```

### Slow Test Issues
To debug slow tests:
```bash
# Run with timing information
pytest tests/test_*_real.py --durations=10 -v
```
