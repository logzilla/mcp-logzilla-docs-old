#!/usr/bin/env python3
"""
MCP Server Tools with Hybrid Search Integration
==============================================

Integrates HybridSearchIndex with the MCP Documentation Server,
providing advanced search capabilities through MCP tools.

Features:
- Hybrid search combining BM25 + vector embeddings
- Document search and retrieval
- Search statistics and analytics
- Integration with existing Document class
"""

from abc import abstractmethod
import asyncio
from dataclasses import dataclass
import logging
from pathlib import Path
import sys
from typing import Dict, List, Optional, Any, Union, Iterable, Callable
from datetime import datetime
import time

from pydantic import BaseModel, Field

# Import our components
try:
    from .bm25_search import BM25SearchEngine
    from .vector_search import VectorSearchEngine, SentenceTransformerProvider
    from .models import Document, DocumentChunk, SearchResult, SearchRequest, SearchEngine
    from .document_cache import DocumentCache, CachedDocument
except ImportError:
    # Fallback for direct execution
    from bm25_search import BM25SearchEngine
    from vector_search import VectorSearchEngine, SentenceTransformerProvider
    from models import Document, DocumentChunk, SearchResult, SearchRequest, SearchEngine
    from document_cache import DocumentCache, CachedDocument

logger = logging.getLogger(__name__)

def get_logger():
    """Get logger instance"""
    return logging.getLogger(__name__)

class SearchTools:
    """
    Search tools for hybrid search functionality - search and retrieval only
    """
    
    default_provider = "sentence_transformers"
    default_model = "thenlper/gte-large"
    
    def __init__(self, document_cache: DocumentCache, wait_for_vector_engine: bool = True, device: str = "auto"):
        self.document_cache = document_cache
        self.device = device
        self.bm25_engine = BM25SearchEngine(
            document_cache=document_cache,
            chunk_size=512,
            chunk_overlap=50
        )
        
        if device != None and device != "none":
            self.vector_engine = VectorSearchEngine(
                document_cache=document_cache,
                provider=self.default_provider,
                model=self.default_model,
                chunk_size=512,
                chunk_overlap=50,
                device=device
            )
        else:
            self.vector_engine = None
        
        # Track engine readiness: None=not started, False=failed, True=ready
        self._bm25_ready = None
        self._vector_ready = None  
        self._wait_for_vector_engine = wait_for_vector_engine
        self._pending_on_ready_fn = None
        
        # Note: Engines are created but need explicit initialize() call
        logger.info("SearchTools.__init__(): Created engines, call initialize() to make them ready")
        
        
    
    @property
    def is_ready(self) -> bool:
        """Check if search index is ready"""
        return self._bm25_ready is True and (self.vector_engine is None or self._vector_ready is True or not self._wait_for_vector_engine)
    
    async def initialize(self, on_ready_fn: Optional[Callable[[bool], None]] = None) -> None:
        """Initialize both search engines and call on_ready_fn when both are ready"""
        self._pending_on_ready_fn = on_ready_fn
        
        # Check if engines are already ready (from previous initialization)
        if self._bm25_ready is True and (self.vector_engine is None or self._vector_ready is True or not self._wait_for_vector_engine):
            logger.info("SearchTools.initialize(): Engines already ready, calling callback immediately")
            if on_ready_fn:
                on_ready_fn(True)
            return
        
        # Reset readiness flags for fresh initialization  
        # None = not started, False = failed, True = ready
        self._bm25_ready = None
        self._vector_ready = None
        
        # Initialize engines with internal callbacks
        logger.info("SearchTools.initialize(): Initializing BM25 engine")
        await self.bm25_engine.initialize(self._on_bm25_ready)
        if self.vector_engine is not None:
            logger.info("SearchTools.initialize(): Initializing vector engine")
            await self.vector_engine.initialize(self._on_vector_ready)
        else:
            logger.info("SearchTools.initialize(): Vector engine disabled")
            # If vector engine is disabled, mark it as "ready" since it's not needed
            self._vector_ready = True
            self._check_both_ready()
    
    def _on_bm25_ready(self, ready: bool) -> None:
        """Callback when BM25 engine is ready"""
        self._bm25_ready = ready
        self._check_both_ready()
    
    def _on_vector_ready(self, ready: bool) -> None:
        """Callback when vector engine is ready"""
        self._vector_ready = ready
        self._check_both_ready()
    
    def _check_both_ready(self) -> None:
        """Check if both engines are ready and call pending callback
        
        States: None=not started, False=failed, True=ready
        """
        # Check for success: BM25 ready AND (vector not used OR vector ready)
        if self._bm25_ready is True and (self.vector_engine is None or self._vector_ready is True or not self._wait_for_vector_engine):
            # Both engines are ready - success!
            if self._pending_on_ready_fn:
                self._pending_on_ready_fn(True)
                self._pending_on_ready_fn = None
                
        # Check for failure: any engine explicitly failed (False)
        elif self._pending_on_ready_fn \
            and (self._bm25_ready is False \
                or (self.vector_engine is not None \
                    and self._wait_for_vector_engine \
                    and self._vector_ready is False)):
            self._pending_on_ready_fn(False)
            self._pending_on_ready_fn = None
    
    def search_for_documents(self, search_request: SearchRequest) -> Dict[str, Any]:
        """
        Search for documents using hybrid BM25 + vector search.
        Returns document IDs and match scores without full content.
        
        Parameters:
        - query: Search query string
        - top_k: Maximum results (1-50, default 10)
        - minimum_score: Minimum score threshold (0.0-1.0)
        
        Returns document IDs, match scores, and chunk content snippets.
        """
        logger = get_logger()
        logger.debug(f"\n[SEARCH] Hybrid Search Debug for '{search_request.query}':")
        
        # Check if search engines are ready
        if not self.is_ready:
            logger.warning("Search engines are not ready yet")
            return {
                "results": [],
                "total_count": 0,
                "message": "Search engines are still initializing"
            }

        try:
            # Perform hybrid search
            bm25_results = self.bm25_engine.search(search_request.query, search_request.top_k)
            logger.debug(f"   [BM25] BM25 results: {len(bm25_results)}")
            if bm25_results:
                logger.debug(f"   [BM25] Top BM25: {bm25_results[0].document_id} (score: {bm25_results[0].score:.4f})")
                
            if self.vector_engine is not None and self.vector_engine.is_ready:
                vector_results = self.vector_engine.search(search_request.query, search_request.top_k)
                logger.debug(f"   [VECTOR] Vector results: {len(vector_results)}")
                if vector_results:
                    logger.debug(f"   [VECTOR] Top Vector: {vector_results[0].document_id} (score: {vector_results[0].score:.4f})")
            else:
                if self.vector_engine is None:
                    logger.debug("   [VECTOR] Vector engine disabled")
                else:
                    logger.debug("   [VECTOR] Vector engine not yet ready")
                vector_results = []
    
            # RRF (Reciprocal Rank Fusion) - combines results based on rank positions
            final_results = self._rrf_fusion(bm25_results, vector_results, search_request.top_k)
            logger.debug(f"   [RRF] RRF results: {len(final_results)}")
            if final_results:
                logger.debug(f"   [RRF] Top RRF: {final_results[0]['document_id']} (score: {final_results[0]['score']:.4f})")

            
            # Return results as dictionary
            return {
                "query": search_request.query,
                "top_k": search_request.top_k,
                "min_quality": search_request.min_quality,
                "results": final_results
            }
        except Exception as e:
            logger.error(f"Failed to search for documents: {e}")
            return {"error": f"Failed to search for documents: {str(e)}"}
        

    def search_and_get_documents(self, search_request: SearchRequest) -> Dict[str, Any]:
        """
        Search for documents and return complete document contents.
        
        Combines hybrid search to find relevant documents with fast in-memory retrieval
        of complete document contents. This is the primary tool for getting full documents
        that match search criteria.
        
        Parameters:
        - query: Search query string
        - top_k: Maximum results (1-50, default 10) 
        - min_quality: Quality cutoff 0-100 (0=return all, 100=exact matches only)
        
        Returns complete documents (not chunks) that match the search query.
        """
        # Check if search engines are ready
        if not self.is_ready:
            logger.warning("Search engines are not ready yet")
            return {
                "results": [],
                "total_count": 0,
                "message": "Search engines are still initializing"
            }

        try:
            search_results = self.search_for_documents(search_request)
            
            # Get document contents for each result
            final_results = []
            for result_dict in search_results.get('results', []):
                document_id = result_dict['document_id']
                doc = self.document_cache.get_document(document_id)
                if doc:
                    # Create a new result dict with content added
                    result_with_content = result_dict.copy()
                    result_with_content['content'] = doc.content
                    final_results.append(result_with_content)
            
            # Return results as dictionary
            return {
                "query": search_request.query,
                "top_k": search_request.top_k,
                "min_quality": search_request.min_quality,
                "results": final_results
            }
        except Exception as e:
            logger.error(f"Failed to search for documents: {e}")
            return {"error": f"Failed to search for documents: {str(e)}"}


    def _rrf_fusion(self, bm25_results, vector_results, limit: int, k: int = 60):
        """Reciprocal Rank Fusion - combines results based on rank positions.
        
        Args:
            bm25_results: BM25 search results
            vector_results: Vector search results  
            limit: Maximum number of results to return
            k: RRF constant (typically 60)
            
        Returns:
            List of fused results sorted by RRF score
        """
        if not bm25_results and not vector_results:
            return []
        if not bm25_results:
            return [{"document_id": r.document_id, "score": r.score, "source": "vector", "rank_in_source": i+1} 
                    for i, r in enumerate(vector_results[:limit])]
        if not vector_results:
            return [{"document_id": r.document_id, "score": r.score, "source": "bm25", "rank_in_source": i+1} 
                    for i, r in enumerate(bm25_results[:limit])]
        
        # Build document score map with RRF scores
        doc_scores = {}
        doc_sources = {}  # Track which engine(s) found each doc
        doc_original_scores = {}  # Keep original scores for reporting
        
        # Add BM25 results with RRF scoring
        for rank, result in enumerate(bm25_results, 1):
            document_id = result.document_id
            rrf_score = 1.0 / (rank + k)
            
            if document_id not in doc_scores:
                doc_scores[document_id] = 0.0
                doc_sources[document_id] = []
                doc_original_scores[document_id] = {}
            
            doc_scores[document_id] += rrf_score
            doc_sources[document_id].append('bm25')
            doc_original_scores[document_id]['bm25'] = result.score
            doc_original_scores[document_id]['bm25_rank'] = rank
        
        # Add Vector results with RRF scoring
        for rank, result in enumerate(vector_results, 1):
            document_id = result.document_id
            rrf_score = 1.0 / (rank + k)
            
            if document_id not in doc_scores:
                doc_scores[document_id] = 0.0
                doc_sources[document_id] = []
                doc_original_scores[document_id] = {}
            
            doc_scores[document_id] += rrf_score
            doc_sources[document_id].append('vector')
            doc_original_scores[document_id]['vector'] = result.score
            doc_original_scores[document_id]['vector_rank'] = rank
        
        # Sort by RRF score and return top results
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        
        final_results = []
        for document_id, rrf_score in sorted_docs[:limit]:
            # Determine primary source (the one with better rank)
            sources = doc_sources[document_id]
            if len(sources) == 1:
                primary_source = sources[0]
            else:
                # Both engines found it - use the one with better rank
                bm25_rank = doc_original_scores[document_id].get('bm25_rank', float('inf'))
                vector_rank = doc_original_scores[document_id].get('vector_rank', float('inf'))
                primary_source = 'vector' if vector_rank < bm25_rank else 'bm25'
            
            # Use the original score from the primary source
            original_score = doc_original_scores[document_id].get(primary_source, rrf_score)
            rank_in_source = doc_original_scores[document_id].get(f'{primary_source}_rank', 1)
            
            final_results.append({
                "document_id": document_id,
                "score": original_score,  # Keep original score for compatibility
                "rrf_score": rrf_score,   # Add RRF score for analysis
                "source": primary_source,
                "rank_in_source": rank_in_source,
                "found_in": sources  # Show which engines found this doc
            })
        
        return final_results

    def get_document_content(self, document_id: str) -> Optional[str]:
        """
        Get document content by ID from cache
        
        Args:
            document_id: Document identifier (relative path)
            
        Returns:
            Document content string if found, None otherwise
        """
        return self.document_cache.get_document_content(document_id)

    def get_status(self) -> Dict[str, Any]:
        """Get search engine status messages"""
        if self.vector_engine is None:
            return {
                self.bm25_engine.get_name(): self.bm25_engine.get_status(),
                VectorSearchEngine.get_name(): "engine disabled"
            }
        elif self.vector_engine.is_ready:
            return {
                self.bm25_engine.get_name(): self.bm25_engine.get_status(),
                self.vector_engine.get_name(): self.vector_engine.get_status()
            } 
        elif not self.wait_for_vector_engine:
            return {
                self.bm25_engine.get_name(): self.bm25_engine.get_status(),
                self.vector_engine.get_name(): [ self.vector_engine.get_status(), "engine bypassed until ready" ]
            }
        else:
            return {
                self.bm25_engine.get_name(): self.bm25_engine.get_status(),
                self.vector_engine.get_name(): self.vector_engine.get_status()
            }

    @property
    def wait_for_vector_engine(self) -> bool:
        """Check if we should wait for vector engine"""
        return self._wait_for_vector_engine


# Example usage
if __name__ == "__main__":
    async def demo():
        """Demonstrate hybrid search tools"""
        # Create tools (index will be built automatically during
        # initialization)
        
        document_cache = DocumentCache()
        
        
        tools = SearchTools(document_cache)
        
        # Initialize and wait for engines to be ready
        def on_search_tools_ready(ready: bool):
            if ready:
                print("Search tools are ready!")
            else:
                print("Search tools failed to initialize!")
        
        await tools.initialize(on_search_tools_ready)
        
        print("Note: Index is automatically built during SearchTools initialization")
        
        # Perform searches
        queries = [
            "syslog configuration setup",
            "log analysis patterns",
            "real-time processing"
        ]
        
        for query in queries:
            search_result = tools.search_for_documents(SearchRequest(
                query=query,
                top_k=3,
                include_scores=True
            ))
            print(f"\nQuery: {query}")
            print(f"Results: {len(search_result.get('results', []))}")
            
            for result in search_result.get('results', [])[:2]:
                print(f"  {result['rank']}. {result['document_id']} (score: {result['hybrid_score']})")
                print(f"     {result['text'][:100]}...")
    
    asyncio.run(demo())
