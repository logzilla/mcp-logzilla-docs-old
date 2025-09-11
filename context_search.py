#!/usr/bin/env python3
"""
Context-Enhanced Search Implementation
====================================

Extends the existing search engines to return contextual windows around matching chunks,
providing users with more complete information surrounding their search results.
"""

import logging
import numpy as np
import faiss
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field

try:
    from .models import Document, DocumentChunk, SearchResult, SearchRequest
    from .bm25_search import BM25SearchEngine
    from .vector_search import VectorSearchEngine, EmbeddedDocumentChunk
    from .search_tools import SearchTools
except ImportError:
    # Fallback for direct execution
    from models import Document, DocumentChunk, SearchResult, SearchRequest
    from bm25_search import BM25SearchEngine
    from vector_search import VectorSearchEngine, EmbeddedDocumentChunk
    from search_tools import SearchTools

logger = logging.getLogger(__name__)


@dataclass
class ChunkSearchResult(SearchResult):
    """Extended search result with chunk information"""
    chunk_index: int
    chunk_id: str
    global_chunk_index: int  # Index in the engine's chunks list


@dataclass
class ContextualSearchResult:
    """Search result with contextual window around the matching chunk"""
    document_id: str
    score: float
    matching_chunk: DocumentChunk
    context_before: List[DocumentChunk] = field(default_factory=list)
    context_after: List[DocumentChunk] = field(default_factory=list)
    full_context_text: str = ""
    
    def __post_init__(self):
        """Generate full context text from all chunks"""
        all_chunks = self.context_before + [self.matching_chunk] + self.context_after
        self.full_context_text = "\n\n".join(chunk.content for chunk in all_chunks)


class ContextualSearchMixin:
    """Mixin to add contextual search capabilities to existing search engines"""
    
    def search_with_context(self, query: str, top_k: int = 10, 
                          context_size: int = 2, 
                          return_chunk_details: bool = False) -> List[Union[ContextualSearchResult, ChunkSearchResult]]:
        """
        Search and return results with contextual windows
        
        Args:
            query: Search query string
            top_k: Maximum number of results to return
            context_size: Number of chunks before/after to include as context
            return_chunk_details: If True, return chunk-level details; if False, return context windows
            
        Returns:
            List of ContextualSearchResult or ChunkSearchResult objects
        """
        # Get chunk-level results first
        chunk_results = self._search_chunks(query, top_k * 3)  # Get more to account for deduplication
        
        if return_chunk_details:
            return chunk_results[:top_k]
        
        # Convert to contextual results
        contextual_results = []
        seen_docs = set()
        
        for chunk_result in chunk_results:
            # Deduplicate at document level if needed
            if chunk_result.document_id in seen_docs:
                continue
            seen_docs.add(chunk_result.document_id)
            
            # Get the matching chunk and its context
            matching_chunk = self.chunks[chunk_result.global_chunk_index]
            context_chunks = self._get_chunk_context(
                chunk_result.document_id, 
                chunk_result.chunk_index,
                context_size
            )
            
            # Split context into before/after
            target_pos = None
            for i, chunk in enumerate(context_chunks):
                if chunk.chunk_index == chunk_result.chunk_index:
                    target_pos = i
                    break
            
            if target_pos is not None:
                context_before = context_chunks[:target_pos]
                context_after = context_chunks[target_pos + 1:]
                
                contextual_results.append(ContextualSearchResult(
                    document_id=chunk_result.document_id,
                    score=chunk_result.score,
                    matching_chunk=matching_chunk,
                    context_before=context_before,
                    context_after=context_after
                ))
            
            if len(contextual_results) >= top_k:
                break
                
        return contextual_results
    
    def _search_chunks(self, query: str, top_k: int) -> List[ChunkSearchResult]:
        """
        Perform chunk-level search (to be implemented by each engine)
        
        Returns:
            List of ChunkSearchResult objects with chunk details
        """
        raise NotImplementedError("Subclasses must implement _search_chunks")
    
    def _get_chunk_context(self, document_id: str, target_chunk_index: int, 
                          context_size: int) -> List[DocumentChunk]:
        """
        Get chunks around a target chunk within the same document
        
        Args:
            document_id: Document identifier
            target_chunk_index: Index of the target chunk within the document
            context_size: Number of chunks before/after to include
            
        Returns:
            List of chunks including context around the target
        """
        # Get all chunks for this document, sorted by chunk_index
        doc_chunks = [chunk for chunk in self.chunks if chunk.document_id == document_id]
        doc_chunks.sort(key=lambda x: x.chunk_index)
        
        # Find the target chunk position in the sorted list
        target_pos = None
        for i, chunk in enumerate(doc_chunks):
            if chunk.chunk_index == target_chunk_index:
                target_pos = i
                break
        
        if target_pos is None:
            return doc_chunks  # Return all if target not found
        
        # Get context window
        start_idx = max(0, target_pos - context_size)
        end_idx = min(len(doc_chunks), target_pos + context_size + 1)
        
        return doc_chunks[start_idx:end_idx]


class ContextualBM25SearchEngine(BM25SearchEngine, ContextualSearchMixin):
    """BM25 search engine with contextual search capabilities"""
    
    def _search_chunks(self, query: str, top_k: int) -> List[ChunkSearchResult]:
        """
        Perform chunk-level BM25 search
        
        Returns:
            List of ChunkSearchResult objects with chunk details
        """
        if not self._index_ready or not self.index:
            logger.warning("Index not ready for search")
            return []
        
        # Get query tokens for BM25
        query_tokens = self.tokenizer(query)
        if not query_tokens:
            logger.warning("No valid tokens in query")
            return []
        
        # Get BM25 scores for all chunks
        bm25_scores = self.index.get_scores(query_tokens)
        
        # Create chunk-level results
        chunk_results = []
        for i, score in enumerate(bm25_scores):
            if i < len(self.chunks) and score > 0:  # Only include non-zero scores
                chunk = self.chunks[i]
                chunk_results.append(ChunkSearchResult(
                    document_id=chunk.document_id,
                    score=float(score),
                    chunk_index=chunk.chunk_index,
                    chunk_id=chunk.chunk_id,
                    global_chunk_index=i
                ))
        
        # Sort by score (descending) and return top results
        chunk_results.sort(key=lambda x: x.score, reverse=True)
        return chunk_results[:top_k]


class ContextualVectorSearchEngine(VectorSearchEngine, ContextualSearchMixin):
    """Vector search engine with contextual search capabilities"""
    
    def _search_chunks(self, query: str, top_k: int) -> List[ChunkSearchResult]:
        """
        Perform chunk-level vector search
        
        Returns:
            List of ChunkSearchResult objects with chunk details
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
            if isinstance(query_embedding, list):
                query_embedding = query_embedding[0].reshape(1, -1)
            elif len(query_embedding.shape) == 1:
                query_embedding = query_embedding.reshape(1, -1)
            
            # Normalize query embedding for cosine similarity
            query_embedding_copy = query_embedding.astype(np.float32).copy()
            faiss.normalize_L2(query_embedding_copy)
            
            # Search in FAISS index
            scores, indices = self.index.search(query_embedding_copy, top_k)
            
            # Create chunk-level results
            chunk_results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx >= 0 and idx < len(self.chunks):  # Valid index
                    chunk = self.chunks[idx]
                    chunk_results.append(ChunkSearchResult(
                        document_id=chunk.document_id,
                        score=float(score),
                        chunk_index=chunk.chunk_index,
                        chunk_id=chunk.chunk_id,
                        global_chunk_index=idx
                    ))
            
            return chunk_results
            
        except Exception as e:
            logger.error(f"Error during vector search: {e}")
            return []


class ContextualSearchTools(SearchTools):
    """Enhanced SearchTools with contextual search capabilities"""
    
    def __init__(self, *args, **kwargs):
        # Initialize with contextual engines instead of regular ones
        super().__init__(*args, **kwargs)
        
        # Replace engines with contextual versions
        document_cache = self.document_cache
        device = self.device
        
        self.bm25_engine = ContextualBM25SearchEngine(
            document_cache=document_cache,
            chunk_size=512,
            chunk_overlap=50
        )
        
        if device != "none" and device is not None:
            self.vector_engine = ContextualVectorSearchEngine(
                document_cache=document_cache,
                provider=self.default_provider,
                model=self.default_model,
                chunk_size=512,
                chunk_overlap=50,
                device=device
            )
    
    def search_with_context(self, search_request: SearchRequest, 
                          context_size: int = 2,
                          engine: str = "hybrid") -> Dict[str, Any]:
        """
        Search for documents and return contextual windows around matches
        
        Args:
            search_request: Standard search request
            context_size: Number of chunks before/after to include as context
            engine: Which engine to use ("bm25", "vector", or "hybrid")
            
        Returns:
            Dictionary with contextual search results
        """
        if not self.is_ready:
            return {
                "results": [],
                "total_count": 0,
                "message": "Search engines are still initializing"
            }
        
        try:
            if engine == "bm25":
                results = self.bm25_engine.search_with_context(
                    search_request.query, 
                    search_request.top_k,
                    context_size
                )
            elif engine == "vector" and self.vector_engine:
                results = self.vector_engine.search_with_context(
                    search_request.query,
                    search_request.top_k, 
                    context_size
                )
            else:  # hybrid
                # Get results from both engines and combine
                bm25_results = self.bm25_engine.search_with_context(
                    search_request.query,
                    search_request.top_k,
                    context_size
                )
                
                vector_results = []
                if self.vector_engine and self.vector_engine.is_ready:
                    vector_results = self.vector_engine.search_with_context(
                        search_request.query,
                        search_request.top_k,
                        context_size
                    )
                
                # Simple fusion - interleave results (could use RRF here too)
                results = self._fuse_contextual_results(bm25_results, vector_results, search_request.top_k)
            
            # Convert to dictionary format
            formatted_results = []
            for i, result in enumerate(results):
                formatted_results.append({
                    "rank": i + 1,
                    "document_id": result.document_id,
                    "score": result.score,
                    "matching_chunk": {
                        "index": result.matching_chunk.chunk_index,
                        "id": result.matching_chunk.chunk_id,
                        "content": result.matching_chunk.content
                    },
                    "context_before": [
                        {"index": chunk.chunk_index, "content": chunk.content}
                        for chunk in result.context_before
                    ],
                    "context_after": [
                        {"index": chunk.chunk_index, "content": chunk.content}
                        for chunk in result.context_after
                    ],
                    "full_context": result.full_context_text
                })
            
            return {
                "query": search_request.query,
                "top_k": search_request.top_k,
                "context_size": context_size,
                "engine": engine,
                "results": formatted_results,
                "total_count": len(formatted_results)
            }
            
        except Exception as e:
            logger.error(f"Failed contextual search: {e}")
            return {"error": f"Failed contextual search: {str(e)}"}
    
    def _fuse_contextual_results(self, bm25_results: List[ContextualSearchResult], 
                               vector_results: List[ContextualSearchResult],
                               limit: int) -> List[ContextualSearchResult]:
        """
        Simple fusion of contextual results from both engines
        
        Args:
            bm25_results: Results from BM25 contextual search
            vector_results: Results from vector contextual search
            limit: Maximum number of results to return
            
        Returns:
            Fused list of contextual results
        """
        # Simple interleaving strategy
        fused = []
        seen_docs = set()
        
        # Interleave results, prioritizing unique documents
        max_len = max(len(bm25_results), len(vector_results))
        for i in range(max_len):
            # Try BM25 result
            if i < len(bm25_results) and bm25_results[i].document_id not in seen_docs:
                fused.append(bm25_results[i])
                seen_docs.add(bm25_results[i].document_id)
                if len(fused) >= limit:
                    break
            
            # Try Vector result
            if i < len(vector_results) and vector_results[i].document_id not in seen_docs:
                fused.append(vector_results[i])
                seen_docs.add(vector_results[i].document_id)
                if len(fused) >= limit:
                    break
        
        return fused