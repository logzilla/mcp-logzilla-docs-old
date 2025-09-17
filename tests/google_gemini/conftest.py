# conftest.py (add this new fixture)

import faiss
import pickle

@pytest.fixture
def mock_index_files(tmp_path: Path):
    """
    Creates a set of dummy .faiss and .pkl files for testing the search engine.
    """
    index_dir = tmp_path / "indexes"
    index_dir.mkdir()
    index_name = "test_engine_index"

    # 1. Create dummy metadata
    metadata = {
        'vector_mapping': {
            0: {'doc_id': 0, 'chunk_index': 0},
            1: {'doc_id': 0, 'chunk_index': 1},
            2: {'doc_id': 1, 'chunk_index': 0},
        },
        'documents': {
            0: {
                'name': 'doc_alpha.txt',
                'chunks': ['First chunk of alpha.', 'Second chunk of alpha.']
            },
            1: {
                'name': 'doc_beta.md',
                'chunks': ['First chunk of beta.']
            }
        },
        'config': {
            'model_name': 'thenlper/gte-large',
            'dimension': 1024
        }
    }
    metadata_path = index_dir / f"{index_name}.pkl"
    with open(metadata_path, 'wb') as f:
        pickle.dump(metadata, f)

    # 2. Create a dummy FAISS index
    dimension = 1024
    num_vectors = 3
    index = faiss.IndexFlatIP(dimension)
    # Add some random vectors
    vectors = np.random.rand(num_vectors, dimension).astype('float32')
    faiss.normalize_L2(vectors)
    index.add(vectors)
    
    index_path = index_dir / f"{index_name}.faiss"
    faiss.write_index(index, str(index_path))

    return index_path, metadata_path