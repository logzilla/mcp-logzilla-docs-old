#!/usr/bin/env python3
"""
Vector Search Engine Implementation
==================================

A pure vector-based search engine that inherits from the base SearchEngine class.
Provides semantic search using dense vector embeddings and FAISS indexing.
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Iterable, Any, Union, Protocol, Callable
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass

import faiss

try:
    from .models import Document, DocumentChunk, SearchResult, SearchEngine
    from .document_cache import DocumentCache
except ImportError:
    # Fallback for direct execution
    from models import Document, DocumentChunk, SearchResult, SearchEngine
    from document_cache import DocumentCache

logger = logging.getLogger(__name__)


# Vector search specific types
EmbeddingVector = np.ndarray


# Embedding provider protocol
class EmbeddingProvider(Protocol):
    """Protocol for embedding providers (sentence-transformers, OpenAI, etc.)"""
    
    def encode(self, texts: Union[str, List[str]]) -> Union[EmbeddingVector, List[EmbeddingVector]]:
        """Encode text(s) into vector embeddings"""
        ...
    
    @property
    def dimension(self) -> int:
        """Embedding vector dimension"""
        ...
    
    @property
    def model_name(self) -> str:
        """Name of the embedding model"""
        ...
    
    @property
    def provider_name(self) -> str:
        """Name of the embedding provider"""
        ...


class SentenceTransformerProvider:
    """HuggingFace sentence-transformers provider for local embeddings"""
    
    SUPPORTED_MODELS = {
        "sentence-transformers/all-MiniLM-L6-v2": {
            "dimension": 384,
            "description": "Fast, lightweight model for general use"
        },
        "BAAI/bge-small-en-v1.5": {
            "dimension": 384,
            "description": "High-quality small model, good balance of speed and accuracy"
        },
        "thenlper/gte-large": {
            "dimension": 1024,
            "description": "Large model with excellent performance on technical content"
        },
        "sentence-transformers/all-mpnet-base-v2": {
            "dimension": 768,
            "description": "High-quality model, good for semantic search"
        }
    }
    
    def __init__(self, model_name: str = "thenlper/gte-large", device: str = "auto"):
        """Initialize SentenceTransformer provider
        
        Args:
            model_name: Name of the model to load
            device: Device to use. Options:
                - "cpu": Force CPU usage (recommended for avoiding CUDA issues)
                - "cuda": Use default GPU
                - "mps": Use Apple Silicon GPU (Mac M1/M2)
                - "auto": Auto-detect best available device
        """
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError("sentence-transformers not available. Install with: pip install sentence-transformers")
        
        self._model_name = self._resolve_model_name(model_name)
        
        # Handle auto-detection
        actual_device = None if device == "auto" else device
        
        self.model = SentenceTransformer(self._model_name, device=actual_device)
        self._dimension = self.model.get_sentence_embedding_dimension() or 384
        
        # Log the actual device being used
        device_used = str(self.model.device) if hasattr(self.model, 'device') else 'unknown'
        logger.info(f"Initialized SentenceTransformer: {self._model_name} (requested: {device}, actual: {device_used}, dimension: {self._dimension})")
    
    def encode(self, texts: Union[str, List[str]]) -> Union[EmbeddingVector, List[EmbeddingVector]]:
        """Encode text(s) using sentence transformers"""
        if self.model is None:
            raise ValueError("SentenceTransformer model is not initialized")
            
        if isinstance(texts, str):
            # Single text
            embedding = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
            return embedding.astype(np.float32)
        else:
            # List of texts
            embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
            return [emb.astype(np.float32) for emb in embeddings]
    
    @property
    def dimension(self) -> int:
        return self._dimension
    
    @property
    def model_name(self) -> str:
        return self._model_name
    
    @property
    def provider_name(self) -> str:
        return "sentence_transformers"
    
    def _resolve_model_name(self, model_name: str) -> str:
        """Resolve model name to full HuggingFace repository name"""
        if model_name in self.SUPPORTED_MODELS:
            return model_name
        
        # Check if it's a short name that maps to a supported model
        for full_name in self.SUPPORTED_MODELS:
            if model_name in full_name:
                logger.info(f"Resolved '{model_name}' to '{full_name}'")
                return full_name
        
        # If not found in supported models, try to use it as-is
        logger.warning(f"Model '{model_name}' not in supported list. Will try to load anyway.")
        return model_name
    
    @classmethod
    def list_supported_models(cls) -> Dict[str, Dict[str, Any]]:
        """Get list of supported models with metadata"""
        return cls.SUPPORTED_MODELS.copy()
    
    def cleanup(self) -> None:
        """Clean up the SentenceTransformer model to prevent memory issues"""
        if hasattr(self, 'model') and self.model is not None:
            try:
                # Clear PyTorch cache if available
                if hasattr(self.model, 'eval'):
                    self.model.eval()
                # Delete the model
                del self.model
                self.model = None
                
                # Clear PyTorch CUDA cache if available
                try:
                    import torch
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                except ImportError:
                    pass
                    
            except Exception as e:
                logger.warning(f"Error during SentenceTransformer cleanup: {e}")
    
    def __del__(self):
        """Destructor to ensure proper cleanup"""
        try:
            self.cleanup()
        except Exception:
            # Ignore errors during destruction to prevent issues during shutdown
            pass





@dataclass
class EmbeddedDocumentChunk(DocumentChunk):
    """DocumentChunk with embedding vector"""
    embedding: Optional[np.ndarray] = None


class VectorSearchEngine(SearchEngine):
    """Vector-based search engine for semantic similarity matching"""
    
    def __init__(self, document_cache: DocumentCache, provider: str = "sentence_transformers", 
                 model: str = "BAAI/bge-small-en-v1.5", api_key: Optional[str] = None,
                 tokenizer=None, chunk_size: int = 512, chunk_overlap: int = 50, 
                 device: str = "auto"):
        """Initialize vector search engine
        
        Args:
            document_cache: DocumentCache instance for accessing cached documents
            provider: Embedding provider name ("sentence_transformers", "openai", etc.)
            model: Model name for the embedding provider
            api_key: API key for cloud providers (if needed)
            tokenizer: Optional tokenizer function
            chunk_size: Maximum tokens per chunk
            chunk_overlap: Token overlap between ch`unks
            device: Device to use for computations ("cpu", "cuda", "mps", "auto")
        """
        logger.info(f"Initializing VectorSearchEngine with provider: {provider}, model: {model}, device: {device}")
        super().__init__(document_cache)
        logger.info(f"VectorSearchEngine.__init__(): after super()")
        self.provider = provider
        self.model = model
        self.api_key = api_key
        self.tokenizer = tokenizer
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.device = device
        self._status = "uninitialized"
        
        # Create embedding provider based on configuration
        logger.info(f"VectorSearchEngine.__init__(): creating embedding provider()")
        self.embedding_provider = self._create_embedding_provider()
        if self.embedding_provider is None:
            logger.error(f"VectorSearchEngine.__init__(): Failed to create embedding provider - got None")
        else:
            logger.info(f"VectorSearchEngine.__init__(): created embedding provider: {type(self.embedding_provider).__name__}")
        
        # Vector search specific attributes
        self.index: Optional[faiss.Index] = None
        self.chunks: List[EmbeddedDocumentChunk] = []
        self.dimension: Optional[int] = None
        
        # Statistics
        self.doc_count = 0
        self.chunk_count = 0
        self.last_updated: Optional[datetime] = None
        logger.info(f"VectorSearchEngine.__init__(): done")

    
    async def initialize(self, on_ready_fn: Optional[Callable[[bool], None]] = None) -> None:
        """Initialize the vector search engine"""
        logger.info("Initializing vector search engine")
        try:
            logger.info("VectorSearchEngine.initialize(): Loading documents from cache")
            await self.load_documents_from_cache()
            self._index_ready = True
            logger.info("Vector search engine initialized")
            if on_ready_fn:
                on_ready_fn(True)
        except Exception as e:
            logger.error(f"Vector search engine initialization failed: {e}")
            self._index_ready = False
            if on_ready_fn:
                on_ready_fn(False)
                
    async def add_documents(self, documents: Iterable[Document]) -> int:
        """Add multiple documents to the index
        
        Args:
            documents: Iterable of Document objects
            
        Returns:
            Number of documents added
        """
        count = 0
        for document in documents:
            chunks_added = self._add_document(document.id, document.content, document.metadata)
            if chunks_added > 0:
                count += 1
        
        # Rebuild index after adding all documents
        if count > 0:
            await self.build_index()
            
        return count
    
    async def build_index(self) -> None:
        """Rebuild FAISS vector index from current chunks"""
        if not self.chunks:
            self._cleanup_faiss_index()
            self.dimension = None
            self._index_ready = False
            return
        
        self._status = "building index"
        # Stack all embeddings
        embeddings_list = [chunk.embedding for chunk in self.chunks if chunk.embedding is not None]
        if not embeddings_list:
            self._cleanup_faiss_index()
            self.dimension = None
            self._index_ready = False
            return
            
        embeddings = np.vstack(embeddings_list)
        self.dimension = embeddings.shape[1]
        
        # Clean up any existing index before creating a new one
        self._cleanup_faiss_index()
        
        # Use inner product similarity (cosine similarity for normalized vectors)
        self.index = faiss.IndexFlatIP(self.dimension)
        
        # Normalize embeddings for cosine similarity
        embeddings_copy = embeddings.copy().astype(np.float32)
        faiss.normalize_L2(embeddings_copy)
        if self.index is not None:
            self.index.add(embeddings_copy)
        self._status = "index built, search engine ready"
        
        self._index_ready = True
        logger.info(f"Built FAISS index: {len(self.chunks)} chunks, {self.dimension}D vectors")
    
    async def load_documents_from_cache(self) -> int:
        """Load all documents from the document cache and build the vector index
        
        Returns:
            Number of documents loaded and indexed
        """
        if not self.document_cache:
            logger.warning("No document cache available")
            return 0
        
        # Clear existing index
        self.clear_index()
        
        # Convert cached documents to Document objects
        documents = []
        for cached_doc in self.document_cache._documents.values():
            # Convert CachedDocument to Document
            document = Document(
                id=cached_doc.id,
                name=cached_doc.name,
                path=cached_doc.path,
                size=cached_doc.size,
                content=cached_doc.content,
                created_at=cached_doc.created_at,
                updated_at=cached_doc.updated_at,
                metadata={"file_modified": cached_doc.file_modified}
            )
            documents.append(document)
        
        # Add documents to index
        count = await self.add_documents(documents)
        logger.info(f"Loaded {count} documents from cache into vector index")
        
        return count
    
    async def refresh_from_cache(self) -> int:
        """Refresh the index from the document cache if cache has been updated
        
        Returns:
            Number of documents loaded, or 0 if no refresh needed
        """
        if not self.document_cache:
            return 0
        
        # Check if cache has been updated since our last index build
        cache_last_scan = getattr(self.document_cache, 'last_scan', None)
        if cache_last_scan and self.last_updated and cache_last_scan <= self.last_updated:
            # Cache hasn't been updated since our last build
            logger.debug("Document cache hasn't changed, skipping refresh")
            return 0
        
        # Reload from cache
        return await self.load_documents_from_cache()
        
    def search(self, query: str, top_k: int = 10) -> List[SearchResult]:
        """Search documents using vector similarity
        
        Args:
            query: Search query string
            top_k: Maximum number of results to return
            
        Returns:
            List of SearchResult objects sorted by similarity score
        """
        if not self._index_ready or not self.index:
            logger.warning("Index not ready for search")
            return []
        
        if not self.embedding_provider:
            logger.error("No embedding provider available")
            return []
        
        try:
            # Generate embedding for query
            query_embedding = self.embedding_provider.encode([query])
            if isinstance(query_embedding, np.ndarray) and len(query_embedding.shape) == 1:
                query_embedding = query_embedding.reshape(1, -1)
            elif isinstance(query_embedding, list):
                query_embedding = np.array(query_embedding).reshape(1, -1)
            
            # Normalize query embedding for cosine similarity
            query_embedding_copy = query_embedding.astype(np.float32).copy()
            faiss.normalize_L2(query_embedding_copy)
            query_embedding = query_embedding_copy
            
            # Search in FAISS index
            if self.index is not None:
                scores, indices = self.index.search(query_embedding, top_k)
            else:
                return []
            
            # Create results
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx >= 0 and idx < len(self.chunks):  # Valid index
                    chunk = self.chunks[idx]
                    results.append(SearchResult(
                        document_id=chunk.document_id,
                        score=float(score)
                    ))
            
            return results
            
        except Exception as e:
            logger.error(f"Error during vector search: {e}")
            return []

    def _add_document(self, document_id: str, content: str, metadata: Optional[Dict] = None) -> int:
        """
        Add document to the index
        
        Args:
            document_id: Unique document identifier
            content: Document text content
            metadata: Optional document metadata
            
        Returns:
            Number of chunks created
        """
        # Remove existing chunks for this document
        self.chunks = [chunk for chunk in self.chunks if chunk.document_id != document_id]
        
        # Create new chunks
        new_chunks: List[DocumentChunk] = self.chunk_document(document_id, content, metadata)
        if not new_chunks:
            logger.warning(f"No chunks created for document {document_id}")
            return 0
        
        # Generate embeddings for chunks
        chunk_texts = [chunk.content for chunk in new_chunks]
        try:
            if self.embedding_provider is None:
                logger.error(f"Cannot generate embeddings for {document_id}: embedding_provider is None")
                return 0
            
            embeddings = self.embedding_provider.encode(chunk_texts)
            if isinstance(embeddings, np.ndarray) and len(embeddings.shape) == 1:
                embeddings = embeddings.reshape(1, -1)
            
            # Convert to EmbeddedDocumentChunk and add embeddings
            embedded_chunks = []
            for chunk, embedding in zip(new_chunks, embeddings):
                embedded_chunk = EmbeddedDocumentChunk(
                    document_id=chunk.document_id,
                    chunk_index=chunk.chunk_index,
                    chunk_id=chunk.chunk_id,
                    content=chunk.content,
                    tokens=chunk.tokens,
                    metadata=chunk.metadata,
                    embedding=embedding.astype(np.float32)
                )
                embedded_chunks.append(embedded_chunk)
                
        except Exception as e:
            logger.error(f"Failed to generate embeddings for {document_id}: {e}")
            return 0
        
        # Add chunks to index
        self.chunks.extend(embedded_chunks)
        self.doc_count += 1
        self.chunk_count += len(embedded_chunks)
        self.last_updated = datetime.now()
        
        logger.info(f"Added document {document_id} with {len(embedded_chunks)} chunks")
        return len(embedded_chunks)


    def chunk_document(self, document_id: str, content: str, metadata: Optional[Dict] = None) -> List[DocumentChunk]:
        """
        Split document content into overlapping chunks
        
        Args:
            document_id: Document identifier
            content: Full document text
            metadata: Optional metadata for chunks
            
        Returns:
            List of DocumentChunk objects
        """
        if not content.strip():
            return []
        
        # Simple word-based chunking (can be enhanced with spaCy sentence boundaries)
        words = content.split()
        chunks: List[DocumentChunk] = []
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i : i + self.chunk_size]
            chunk_text = ' '.join(chunk_words)
            if not chunk_text.strip():
                continue

            # Generate tokens if tokenizer is available
            tokens = self.tokenizer(chunk_text) if self.tokenizer else chunk_text.split()
            
            chunk = DocumentChunk(
                document_id=document_id,
                chunk_index=len(chunks),
                chunk_id=f"{document_id}:{len(chunks)}",
                content=chunk_text,
                tokens=tokens,
                metadata=metadata or {}
            )
            chunks.append(chunk)
        
        return chunks
    
    def get_stats(self) -> Dict[str, Any]:
        """Get search engine statistics
        
        Returns:
            Dictionary with engine statistics
        """
        stats = {
            "engine_type": "Vector",
            "index_ready": self._index_ready,
            "doc_count": self.doc_count,
            "chunk_count": self.chunk_count,
            "dimension": self.dimension,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "embedding_provider": str(type(self.embedding_provider).__name__) if self.embedding_provider else None
        }
        
        # Add document cache statistics if available
        if self.document_cache:
            cache_stats = self.document_cache.get_stats()
            stats["document_cache"] = {
                "total_docs": cache_stats.get("total_documents", 0),
                "total_size_mb": cache_stats.get("total_size_mb", 0),
                "cache_last_scan": cache_stats.get("last_scan")
            }
        
        return stats
    
    def clear_index(self) -> None:
        """Clear all documents and reset the index"""
        # Only cleanup the FAISS index, NOT the embedding provider
        self._cleanup_faiss_index()
        
        # Clear chunks
        if hasattr(self, 'chunks'):
            self.chunks.clear()
        
        # Reset stats but keep embedding provider
        self.dimension = None
        self.doc_count = 0
        self.chunk_count = 0
        self.last_updated = None
        self._index_ready = False
        logger.info("Cleared vector search index")
    
    def get_chunk_by_id(self, chunk_id: str) -> Optional[EmbeddedDocumentChunk]:
        """Get a specific chunk by its ID
        
        Args:
            chunk_id: The chunk identifier
            
        Returns:
            EmbeddedDocumentChunk if found, None otherwise
        """
        for chunk in self.chunks:
            if chunk.chunk_id == chunk_id:
                return chunk
        return None
    
    def get_chunks_by_document_id(self, document_id: str) -> List[EmbeddedDocumentChunk]:
        """Get all chunks for a specific document
        
        Args:
            document_id: Document identifier
            
        Returns:
            List of EmbeddedDocumentChunk objects for the document
        """
        return [chunk for chunk in self.chunks if chunk.document_id == document_id]
    
    def _create_embedding_provider(self):
        """Create embedding provider based on configuration
        
        Returns:
            Embedding provider instance
        """
        try:
            if self.provider == "sentence_transformers":
                provider = SentenceTransformerProvider(model_name=self.model, device=self.device)
                logger.info(f"Successfully created embedding provider: {type(provider).__name__}")
                return provider
            else:
                raise ValueError(f"Unsupported embedding provider: {self.provider}. Only 'sentence_transformers' is supported.")
        except Exception as e:
            logger.error(f"Failed to create embedding provider '{self.provider}': {e}")
            logger.info("Falling back to sentence_transformers with default model")
            try:
                fallback_provider = SentenceTransformerProvider(model_name="sentence-transformers/all-MiniLM-L6-v2", device=self.device)
                logger.info(f"Successfully created fallback embedding provider: {type(fallback_provider).__name__}")
                return fallback_provider
            except Exception as fallback_e:
                logger.error(f"Failed to create fallback embedding provider: {fallback_e}")
                return None

    def get_status(self) -> List[str]:
        """Get search engine status messages"""
        return [self._status]

    @classmethod
    def get_name(cls) -> str:
        """Get search engine name"""
        return "fuzzy search"

    def _cleanup_faiss_index(self) -> None:
        """Properly cleanup FAISS index to prevent core dumps"""
        if self.index is not None:
            try:
                # Reset the index to ensure proper cleanup
                if hasattr(self.index, 'reset'):
                    self.index.reset()
                # Force garbage collection of the index object
                del self.index
            except Exception as e:
                logger.warning(f"Error during FAISS index cleanup: {e}")
            finally:
                self.index = None
    
    def _cleanup_embedding_provider(self) -> None:
        """Cleanup the embedding provider"""
        if self.embedding_provider is not None:
            try:
                if hasattr(self.embedding_provider, 'cleanup'):
                    self.embedding_provider.cleanup()
                del self.embedding_provider
            except Exception as e:
                logger.warning(f"Error during embedding provider cleanup: {e}")
            finally:
                self.embedding_provider = None

    def cleanup(self) -> None:
        """Comprehensive cleanup of all resources"""
        try:
            self._cleanup_faiss_index()
            self._cleanup_embedding_provider()
            
            # Clear chunks
            if hasattr(self, 'chunks'):
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
