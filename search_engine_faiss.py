#!/usr/bin/env python3
"""
FAISS Vector Search Engine Implementation
=========================================

A pure vector-based search engine that inherits from the base SearchEngine class.
Provides semantic search using dense vector embeddings and FAISS indexing.
"""

from abc import ABC
from dataclasses import dataclass
from datetime import datetime
import faiss
import logging
import numpy as np
from pathlib import Path
import pickle
from sentence_transformers import SentenceTransformer
from typing import Dict, List, Optional, Iterable, Any, Union, Protocol, Callable

from models import Document, DocumentChunk, SearchEngine

# Initialize logger
logger = logging.getLogger(__name__)

class ModelSentenceTransformer:
    """HuggingFace sentence-transformers provider for local embeddings"""
    
    # any huggingface model is supported, but here are some suggestions
    # MODEL_SUGGESTIONS = {
    #     "sentence-transformers/all-MiniLM-L6-v2": {
    #         "dimension": 384,
    #         "description": "Fast, lightweight model for general use"
    #     },
    #     "BAAI/bge-small-en-v1.5": {
    #         "dimension": 384,
    #         "description": "High-quality small model, good balance of speed and accuracy"
    #     },
    #     "thenlper/gte-large": {
    #         "dimension": 1024,
    #         "description": "Large model with excellent performance on technical content"
    #     },
    #     "sentence-transformers/all-mpnet-base-v2": {
    #         "dimension": 768,
    #         "description": "High-quality model, good for semantic search"
    #     }
    # }
    
    def __init__(self, model_name: str = "thenlper/gte-large", device: str = "auto"):
        """Initialize ModelSentenceTransformer provider
        
        Args:
            model_name: Name of the model to load
            device: Device to use. Options:
                - "cpu": Force CPU usage (recommended for avoiding CUDA issues)
                - "cuda": Use default GPU
                - "mps": Use Apple Silicon GPU (Mac M1/M2)
                - "auto": Auto-detect best available device
        """
        self._model_name = model_name
        
        # Handle auto-detection
        actual_device = None if device == "auto" else device
        
        self._model = SentenceTransformer(self._model_name, device=actual_device)
        self._dimension = self._model.get_sentence_embedding_dimension() or 384
        
        # Log the actual device being used
        device_used = str(self._model.device) if hasattr(self._model, 'device') else 'unknown'
        logger.info(f"Initialized ModelSentenceTransformer: {self._model_name} (requested: {device}, actual: {device_used}, dimension: {self._dimension})")
    
    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Encode text(s) using sentence transformers"""
        if self._model is None:
            raise ValueError("ModelSentenceTransformer model is not initialized")
            
        # Always return numpy array - sentence_transformers handles both single strings and lists
        embeddings = self._model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return embeddings.astype(np.float32)
    
    @property
    def dimension(self) -> int:
        return self._dimension
    
    @property
    def model_name(self) -> str:
        return self._model_name
    
    def cleanup(self) -> None:
        """Clean up the ModelSentenceTransformer model to prevent memory issues"""
        if hasattr(self, '_model') and self._model is not None:
            try:
                # Note: .eval() is not needed for SentenceTransformer models
                # as they are not raw nn.Module instances
                # Delete the model
                del self._model
                self._model = None
                
                # Clear PyTorch CUDA cache if available
                try:
                    import torch
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                except ImportError:
                    pass
                    
            except Exception as e:
                logger.warning(f"Error during ModelSentenceTransformer cleanup: {e}")
    
    def __del__(self):
        """Destructor to ensure proper cleanup"""
        try:
            self.cleanup()
        except Exception:
            # Ignore errors during destruction to prevent issues during shutdown
            pass


class FaissSearchEngine(SearchEngine):
    """Facebook AI Similarity Search (FAISS)"""
    
    def __init__(self, 
                 embedding_name: str, 
                 embedding_path: Union[str, Path], 
                 model_name: str, 
                 device: str = "auto"):
        self._is_ready = False
        self._index_path = Path(embedding_path) / f"{embedding_name}.faiss" # must be .faiss format
        self._metadata_file = Path(embedding_path) / f"{embedding_name}.pkl" # must be in pickle format
        self._metadata = None
        self._model_name = model_name
        self._device = device
        self._index = None
        self._sentence_transformer = None
    
    @property
    def is_ready(self) -> bool:
        """Check if the search engine is ready"""
        return self._is_ready
        
    def initialize(self) -> None:
        """Initialize the search engine"""
        try:
            # Validate files exist
            if not Path(self._index_path).exists():
                raise FileNotFoundError(f"FAISS index file not found: {self._index_path}")
            if not Path(self._metadata_file).exists():
                raise FileNotFoundError(f"Metadata file not found: {self._metadata_file}")
            
            # load model
            self._sentence_transformer = ModelSentenceTransformer(self._model_name, self._device)
            
            # read index - convert Path to string for FAISS compatibility
            self._index = faiss.read_index(str(self._index_path))
            logger.info(f"Successfully loaded FAISS index with {self._index.ntotal} vectors")

            # validate embedding dimension compatibility
            index_dim = getattr(self._index, 'd', None)
            model_dim = self._sentence_transformer.dimension
            if index_dim is not None and index_dim != model_dim:
                raise ValueError(f"Embedding dimension mismatch: FAISS index d={index_dim}, model dimension={model_dim}")
            
            # read metadata, chunks, and documents
            with open(self._metadata_file, 'rb') as metadata_file:
                self._metadata = pickle.load(metadata_file)
            
            # Validate metadata structure
            if 'vector_mapping' not in self._metadata or 'documents' not in self._metadata:
                raise ValueError("Invalid metadata structure: missing 'vector_mapping' or 'documents'")
            
            self._is_ready = True
            
        except Exception as e:
            logger.error(f"Failed to initialize search engine: {e}")
            self._is_ready = False
            raise
    
    def _should_normalize_query(self) -> bool:
        """Determine if query should be normalized based on index type"""
        # Check metric_type attribute first
        metric_type = getattr(self._index, 'metric_type', None)
        if metric_type == faiss.METRIC_INNER_PRODUCT:
            return True
        
        # Fallback to metadata config
        try:
            if self._metadata.get('config', {}).get('index_type') == 'IndexFlatIP':
                return True
        except Exception:
            pass
        
        # Final fallback: class name check
        try:
            class_name = self._index.__class__.__name__
            return class_name in {'IndexFlatIP', 'IndexIVFFlat'} and metric_type in (None, faiss.METRIC_INNER_PRODUCT)
        except Exception:
            return False
    
    def _search_for_chunks_internal(self, query_text: str, top_k: int = 10) -> List[DocumentChunk]:
        """Search for chunks of documents matching the query"""
        query_vector = self._sentence_transformer.encode([query_text]).astype('float32')
        
        # Normalize query for inner-product (cosine similarity) indices
        if self._should_normalize_query():
            faiss.normalize_L2(query_vector)
        
        # Cap top_k to available vectors for safety
        safe_top_k = min(top_k, self._index.ntotal)
        
        # Search
        scores, vector_ids = self._index.search(query_vector, safe_top_k)
        
        # Get results with bounds checking
        results = []
        for score, vector_id in zip(scores[0], vector_ids[0]):
            # Skip invalid vector IDs (FAISS returns -1 for not found)
            if vector_id < 0 or vector_id not in self._metadata['vector_mapping']:
                continue
                
            try:
                mapping = self._metadata['vector_mapping'][vector_id]
                doc = self._metadata['documents'][mapping['doc_id']]
                chunk_text = doc['chunks'][mapping['chunk_index']]
                
                # Convert FAISS distance to similarity score
                similarity_score = float(score)
                
                if self._should_normalize_query():  # IP/cosine similarity case
                    # For IP on normalized vectors, score is cosine similarity in [-1,1]
                    # Map to friendlier [0,1] range: (x+1)/2
                    similarity_score = (similarity_score + 1.0) / 2.0
                elif hasattr(self._index, 'metric_type') and self._index.metric_type == faiss.METRIC_L2:
                    # Convert L2 distance to similarity score (inverse relationship)
                    similarity_score = 1.0 / (1.0 + float(score))
                
                results.append(DocumentChunk(
                    document_id=mapping['doc_id'],
                    chunk_index=mapping['chunk_index'], 
                    content=chunk_text,
                    metadata={'score': similarity_score}
                ))
            except (KeyError, IndexError) as e:
                logger.warning(f"Error processing vector_id {vector_id}: {e}")
                continue
                
        return results
        
    def search_for_chunks(self, query_text: str, top_k: int = 10) -> List[DocumentChunk]:
        return self._search_for_chunks_internal(query_text, top_k)
    
    def search_for_documents(self, query_text: str, top_k: int = 10) -> List[Document]:
        # Cap top_k to available documents for safety
        safe_top_k = min(top_k, len(self._metadata.get('documents', {})))
        
        chunks = self._search_for_chunks_internal(\
            query_text, 
            safe_top_k * self._calculate_document_search_result_multiplier(self._metadata))
        
        # sort chunks by score (higher similarity = better)
        chunks.sort(key=lambda x: x.metadata.get('score', 0), reverse=True)
        
        # remove duplicates while preserving order
        seen_doc_ids = set()
        ordered_doc_ids = []
        for chunk in chunks:
            doc_id = chunk.document_id
            if doc_id not in seen_doc_ids:
                seen_doc_ids.add(doc_id)
                ordered_doc_ids.append(doc_id)
        
        documents_meta = self._metadata['documents']
        results: List[Document] = []
        for doc_id in ordered_doc_ids[:top_k]:
            try:
                doc_meta = documents_meta[doc_id]
                
                # Handle updated_at field - convert ISO string to datetime if needed
                updated_at = doc_meta.get('updated_at')
                if isinstance(updated_at, str):
                    try:
                        updated_at = datetime.fromisoformat(updated_at)
                    except (ValueError, TypeError):
                        updated_at = None
                
                results.append(
                    Document(
                        id=doc_meta['id'],
                        name=doc_meta['name'],
                        size=doc_meta['size'],
                        content=doc_meta.get('content', ''),
                        metadata=doc_meta.get('metadata', {}),
                        updated_at=updated_at
                    )
                )
            except Exception as e:
                logger.warning(f"Failed to construct Document for id {doc_id}: {e}")
                continue
        return results
        

    def _calculate_document_search_result_multiplier(self, metadata):
        """
        Analyze your corpus to predict how much duplication to expect
        If you search for documents, internally it searches for chunks,
        so to try to honor the number of requested documents returned
        we must multiply the number of requested documents by a factor
        so that multiple chunks from the same document can be de-duplicated
        """
        total_chunks = len(metadata['vector_mapping'])
        total_docs = len(metadata['documents'])
        
        # Guard against division by zero
        if total_docs == 0:
            return 1
        
        avg_chunks_per_doc = total_chunks / total_docs
        
        # Predict multiplier based on chunk density
        if avg_chunks_per_doc <= 3:
            return 2  # Small docs, less duplication
        elif avg_chunks_per_doc <= 8:  
            return 3  # Medium docs
        else:
            return 4  # Large docs, more duplication likely
    
    def get_status(self) -> List[str]:
        """Get search engine status messages"""
        return ["Ready" if self._is_ready else "Not ready"]

    # was getting core dumps at program exit so extra logic 
    # required for exit
    def _cleanup_faiss_index(self) -> None:
        """Properly cleanup FAISS index to prevent core dumps"""
        if self._index is not None:
            try:
                # Reset the index to ensure proper cleanup
                if hasattr(self._index, 'reset'):
                    self._index.reset()
                # Force garbage collection of the index object
                del self._index
            except Exception as e:
                logger.warning(f"Error during FAISS index cleanup: {e}")
            finally:
                self._index = None

    def _cleanup_sentence_transformer(self) -> None:
        """Cleanup the embedding provider"""
        if self._sentence_transformer is not None:
            try:
                if hasattr(self._sentence_transformer, 'cleanup'):
                    self._sentence_transformer.cleanup()
                del self._sentence_transformer
            except Exception as e:
                logger.warning(f"Error during embedding provider cleanup: {e}")
            finally:
                self._sentence_transformer = None

    def cleanup(self) -> None:
        """Comprehensive cleanup of all resources"""
        try:
            self._cleanup_faiss_index()
            self._cleanup_sentence_transformer()
            
            # Clear chunks if they exist
            if hasattr(self, 'chunks') and self.chunks is not None:
                self.chunks.clear()
                
            # Force garbage collection
            import gc
            gc.collect()
            
        except Exception as e:
            logger.warning(f"Error during VectorSearchEngine cleanup: {e}")

    def __del__(self):
        """Destructor to ensure proper cleanup"""
        try:
            self.cleanup()
        except Exception:
            # Ignore errors during destruction to prevent issues during shutdown
            pass

    @property
    def doc_count(self) -> int:
        """Get the number of documents in the search engine"""
        try:
            return len(self._metadata['documents']) if self._metadata and 'documents' in self._metadata else 0
        except Exception:
            return 0
    