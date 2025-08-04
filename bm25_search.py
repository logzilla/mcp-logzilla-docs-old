#!/usr/bin/env python3
"""
BM25 Search Engine Implementation
================================

A pure BM25-based search engine that inherits from the base SearchEngine class.
Provides keyword-based search using the BM25 ranking algorithm.
"""

import logging
import re
from typing import Dict, List, Optional, Iterable, Any, Callable
from datetime import datetime
from pathlib import Path

from rank_bm25 import BM25Okapi
from nltk.stem import PorterStemmer

try:
    from .models import Document, DocumentChunk, SearchResult, SearchEngine
    from .document_cache import DocumentCache
except ImportError:
    # Fallback for direct execution
    from models import Document, DocumentChunk, SearchResult, SearchEngine
    from document_cache import DocumentCache

logger = logging.getLogger(__name__)


class BM25SearchEngine(SearchEngine):
    """BM25-based search engine for keyword matching"""
    
    def __init__(self, document_cache: DocumentCache, chunk_size: int = 512, chunk_overlap: int = 50):
        """Initialize BM25 search engine
        
        Args:
            document_cache: DocumentCache instance for accessing cached documents
            chunk_size: Maximum tokens per chunk
            chunk_overlap: Token overlap between chunks
        """
        super().__init__(document_cache)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize BM25-specific tokenizer with stemming
        self._initialize_nltk()
        self.stemmer = PorterStemmer()
        self.tokenizer = self._create_bm25_tokenizer()
        
        # BM25 specific attributes
        self.index: Optional[BM25Okapi] = None
        self.chunks: List[DocumentChunk] = []
        self.vocabulary: set = set()
        
        # Statistics
        self.doc_count = 0
        self.chunk_count = 0
        self.last_updated: Optional[datetime] = None
        
        self._status = "uninitialized"
    
    def _initialize_nltk(self):
        """Download required NLTK data if not already present"""
        try:
            import nltk
            nltk.data.find('tokenizers/punkt')
        except (ImportError, LookupError):
            logger.info("NLTK 'punkt' tokenizer not found. Downloading...")
            try:
                import nltk
                nltk.download('punkt', quiet=True)
                logger.info("'punkt' downloaded successfully.")
            except Exception as e:
                logger.error(f"Failed to download NLTK 'punkt' tokenizer: {e}")
                raise

    def _create_bm25_tokenizer(self):
        """Create BM25-specific tokenizer using regex plus stemming"""
        def tokenize(text: str) -> List[str]:
            # Regex to capture words, including hyphenated, dot, underscore segments
            base_tokens = re.findall(r'\w+(?:[-._]\w+)*|\w+', text.lower())
            enriched: List[str] = []
            for tok in base_tokens:
                enriched.append(tok)
                # Add sub-parts split by delimiters to improve matching
                if '-' in tok or '_' in tok or '.' in tok:
                    enriched.extend(re.split('[-._]', tok))

            # Stem each token
            return [self.stemmer.stem(t) for t in enriched if len(t) > 1 or t.isalnum()]
        return tokenize
    
    async def initialize(self, on_ready_fn: Optional[Callable[[bool], None]] = None) -> None:
        """Initialize the BM25 search engine"""
        await self._load_documents_from_cache()
        await self._build_index()
        self._index_ready = True
        logger.info("BM25 search engine initialized")
        if on_ready_fn:
            on_ready_fn(True)
    
    async def _build_index(self) -> None:
        """Rebuild BM25 index from current chunks"""
        if not self.chunks:
            self.index = None
            self.vocabulary = set()
            self._index_ready = False
            return
        
        self._status = "building index"
        # Rebuild BM25 index
        corpus_tokens = [chunk.tokens for chunk in self.chunks]
        self.index = BM25Okapi(corpus_tokens)
        
        # Build vocabulary set for fast lookup during search
        self.vocabulary = set(token for doc_tokens in corpus_tokens for token in doc_tokens)
        
        self._index_ready = True
        logger.info(f"Built BM25 index: {len(self.chunks)} chunks, {len(self.vocabulary)} unique tokens")
        self._status = "index built, search engine ready"
    
    async def _load_documents_from_cache(self) -> int:
        """Load all documents from the document cache
        
        Returns:
            Number of documents loaded
        """
        if not self.document_cache:
            logger.warning("No document cache available")
            return 0
        
        # Clear existing index
        self.clear_index()
        
        # Process each cached document directly
        count = 0
        for cached_doc in self.document_cache._documents.values():
            chunks_added = self._add_document(
                cached_doc.id, 
                cached_doc.content, 
                {"file_modified": cached_doc.file_modified}
            )
            if chunks_added > 0:
                count += 1
        
        logger.info(f"Loaded {count} documents from cache into BM25 index")
        
        return count
    
    def refresh_from_cache(self) -> int:
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
        return self._load_documents_from_cache()
        
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
        new_chunks = self.chunk_document(document_id, content, metadata)
        if not new_chunks:
            logger.warning(f"No chunks created for document {document_id}")
            return 0
        
        # Add chunks to index (BM25 doesn't need embeddings)
        self.chunks.extend(new_chunks)
        self.doc_count += 1
        self.chunk_count += len(new_chunks)
        self.last_updated = datetime.now()
        
        logger.info(f"Added document {document_id} with {len(new_chunks)} chunks")
        return len(new_chunks)

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

            chunk = DocumentChunk(
                document_id=document_id,
                chunk_index=len(chunks),
                chunk_id=f"{document_id}:{len(chunks)}",
                content=chunk_text,
                tokens=self.tokenizer(chunk_text),
                metadata=metadata or {}
            )
            chunks.append(chunk)
        
        return chunks

    def search(self, query: str, top_k: int = 10) -> List[SearchResult]:
        """Search documents using BM25 ranking
        
        Args:
            query: Search query string
            top_k: Maximum number of results to return
            
        Returns:
            List of SearchResult objects sorted by BM25 score
        """
        if not self._index_ready or not self.index:
            logger.warning("Index not ready for search")
            return []
        
        # Get query tokens for BM25
        query_tokens = self.tokenizer(query)
        if not query_tokens:
            logger.warning("No valid tokens in query")
            return []
        
        logger.debug(f"Query tokens: {query_tokens}")
        
        # Get BM25 scores for all chunks
        bm25_scores = self.index.get_scores(query_tokens)
        
        # Create results with chunk information
        chunk_results = []
        for i, score in enumerate(bm25_scores):
            if i < len(self.chunks) and score > 0:  # Only include non-zero scores
                chunk = self.chunks[i]
                chunk_results.append(SearchResult(
                    document_id=chunk.document_id,
                    score=float(score)
                ))
        
        # Sort chunk results by score (descending)
        chunk_results.sort(key=lambda x: x.score, reverse=True)
        
        # Deduplicate at document level - keep only the highest scoring chunk per document
        seen_docs = set()
        deduped_results = []
        
        for result in chunk_results:
            if result.document_id not in seen_docs:
                deduped_results.append(result)
                seen_docs.add(result.document_id)
                
                # Stop when we have enough unique documents
                if len(deduped_results) >= top_k:
                    break
        
        logger.debug(f"BM25 search: {len(chunk_results)} chunk results -> {len(deduped_results)} unique documents")
        return deduped_results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get search engine statistics
        
        Returns:
            Dictionary with engine statistics
        """
        stats = {
            "engine_type": "BM25",
            "index_ready": self._index_ready,
            "doc_count": self.doc_count,
            "chunk_count": self.chunk_count,
            "vocabulary_size": len(self.vocabulary),
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap
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
        self.chunks.clear()
        self.index = None
        self.vocabulary.clear()
        self.doc_count = 0
        self.chunk_count = 0
        self.last_updated = None
        self._index_ready = False
        logger.info("Cleared BM25 search index")

    def get_status(self) -> List[str]:
        """Get search engine status messages"""
        return [self._status]

    @classmethod
    def get_name(cls) -> str:
        """Get search engine name"""
        return "exact search"
    
    def cleanup(self) -> None:
        """Cleanup resources (for consistency with VectorSearchEngine)"""
        try:
            self.chunks.clear()
            self.index = None
            self.vocabulary.clear()
            
            # Force garbage collection
            import gc
            gc.collect()
            
        except Exception as e:
            logger.warning(f"Error during BM25SearchEngine cleanup: {e}")
