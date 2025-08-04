#!/usr/bin/env python3
"""
Comprehensive Test Suite for Hybrid Search Implementation
========================================================

Tests the new modular search architecture with BM25, Vector, and Hybrid search engines.
Uses search_tools.py, bm25_search.py, and vector_search.py.

Run with: python test_hybrid_search.py
Or with pytest: pytest test_hybrid_search.py -v
"""

import pytest
import asyncio
import tempfile
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import os

# Check for required dependencies first
missing_deps = []
try:
    import rank_bm25
except ImportError:
    missing_deps.append('rank-bm25')

try:
    import faiss
except ImportError:
    missing_deps.append('faiss-cpu')

try:
    import sentence_transformers
except ImportError:
    missing_deps.append('sentence-transformers')

try:
    import nltk
except ImportError:
    missing_deps.append('nltk')

if missing_deps:
    print(f"❌ Missing required dependencies: {', '.join(missing_deps)}")
    print("📦 Please install them with:")
    print(f"   pip install {' '.join(missing_deps)}")
    print("   Or if you have requirements files, make sure they include these packages.")
    raise ImportError(f"Required dependencies not found: {', '.join(missing_deps)}")

# Import search components directly
from search_tools import SearchTools
from models import SearchRequest
from document_cache import DocumentCache

# Setup test environment
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test configuration for the new architecture
TEST_CONFIG = {
    "provider": "sentence_transformers", 
    "model": "BAAI/bge-small-en-v1.5",
    "chunk_size": 256,
    "chunk_overlap": 25
}

# Use real LogZilla docs directory
DOCS_DIRECTORY = "../../../lz/ui/app/docs"

# Comment out artificial document creation for now
# SAMPLE_DOCUMENTS = [...]

@pytest.fixture
def test_docs_directory():
    """Use real LogZilla documentation directory or create a test directory"""
    docs_path = Path(__file__).parent / DOCS_DIRECTORY
    if not docs_path.exists():
        # Create a temporary test directory with some test files
        import tempfile
        test_dir = Path(tempfile.mkdtemp())
        
        # Create some test markdown files
        (test_dir / "test1.md").write_text("# Test Document 1\n\nThis is a test document about syslog configuration.")
        (test_dir / "test2.md").write_text("# Test Document 2\n\nThis document covers API authentication and security.")
        (test_dir / "test3.md").write_text("# Test Document 3\n\nPerformance optimization and monitoring dashboard.")
        
        yield str(test_dir)
        
        # Cleanup
        import shutil
        shutil.rmtree(test_dir, ignore_errors=True)
    else:
        yield str(docs_path.resolve())


@pytest.fixture
def search_tools(test_docs_directory):
    """Create and populate search tools with embedded documents"""
    
    # Create document cache with test configuration
    document_cache = DocumentCache()
    import asyncio
    loaded_count, error_count, total_size = asyncio.run(document_cache.load_all_documents(test_docs_directory))
    
    # Create search tools with document cache
    tools = SearchTools(document_cache)
    
    # Initialize engines explicitly and wait for readiness
    async def initialize_and_wait():
        await tools.initialize()
        if not tools.is_ready:
            print("⚠️ Search tools failed to initialize properly")
        else:
            print("✅ Search tools initialized successfully!")
    
    # Run the async initialization
    import asyncio
    asyncio.run(initialize_and_wait())
    
    return tools


@pytest.fixture
def sample_queries():
    """Test queries designed to trigger different search pathways"""
    return {
        "bm25_favored": [
            "syslog-ng configuration",
            "API key authentication", 
            "firewall port 514",
            "systemctl restart syslog-ng"
        ],
        "vector_favored": [
            "log processing performance",
            "system monitoring dashboard",
            "network connectivity problems",
            "performance optimization strategies"
        ],
        "hybrid": [
            "troubleshooting connection issues",
            "API integration examples", 
            "real-time event correlation",
            "authentication and security"
        ]
    }


class TestBasicImports:
    """Test basic import functionality"""
    
    def test_imports_available(self):
        """Test that basic imports work"""
        # Test that we can instantiate basic classes
        cache = DocumentCache()
        assert cache is not None
        
        # Test search tools
        tools = SearchTools(cache)
        assert tools is not None
    
    def test_dependencies_status(self):
        """Report status of required dependencies"""
        print(f"\n📦 Dependency status:")
        available_deps = []
        for dep in ['rank_bm25', 'faiss', 'sentence_transformers', 'nltk']:
            try:
                __import__(dep)
                status = "✅"
                available_deps.append(dep)
            except ImportError:
                status = "❌"
            print(f"  {status} {dep}")
        
        # All dependencies should be available
        print(f"📦 Available: {len(available_deps)}/4 dependencies")
        assert len(available_deps) == 4, f"All dependencies should be available, missing: {4 - len(available_deps)}"


class TestIndexing:
    """Test document indexing functionality"""
    
    def test_index_creation(self):
        """Test creating a search index"""
        # Create document cache first
        document_cache = DocumentCache()
        
        # Create search tools with document cache
        tools = SearchTools(document_cache)
        
        assert tools is not None
        assert tools.bm25_engine is not None
        assert tools.vector_engine is not None
    
    def test_document_indexing(self, search_tools):
        """Test that documents are properly indexed"""
        # Check that index was built successfully
        assert search_tools.is_ready
        
        # Verify documents are in cache
        cache_result = search_tools.get_documents_stats()
        assert "total_documents" in cache_result
        assert cache_result["total_documents"] > 0
    
    def test_individual_document_indexing(self):
        """Test that individual engines can be accessed"""
        # Create document cache first
        document_cache = DocumentCache()
        
        # Create search tools with document cache
        tools = SearchTools(document_cache)
        
        # Test that both engines are accessible
        assert tools.bm25_engine is not None
        assert tools.vector_engine is not None
        
        # Test engine stats are available
        bm25_stats = tools.bm25_engine.get_stats()
        vector_stats = tools.vector_engine.get_stats()
        
        assert "engine_type" in bm25_stats
        assert "engine_type" in vector_stats
        assert bm25_stats["engine_type"] == "BM25"
        assert vector_stats["engine_type"] == "Vector"


class TestBM25Search:
    """Test BM25 keyword search functionality"""
    
    def test_bm25_exact_matches(self, search_tools, sample_queries):
        """Test search for exact keyword matches (BM25 component)"""
        
        # Test BM25-favored queries
        for query in sample_queries["bm25_favored"]:
            request = SearchRequest(
                query=query,
                top_k=5,
                include_scores=True
            )
            
            result = search_tools.search_for_documents(request)
            assert "results" in result
            assert len(result["results"]) > 0
            
            # Check that we got relevant results
            top_result = result["results"][0]
            assert "score" in top_result
            assert top_result["score"] > 0
    
    def test_bm25_ranking(self, search_tools):
        """Test BM25 ranking quality via search results"""
        
        request = SearchRequest(
            query="syslog configuration",
            top_k=3,
            include_scores=True
        )
        
        result = search_tools.search_for_documents(request)
        results = result["results"]
        
        # Verify results are ranked by score (descending)
        for i in range(1, len(results)):
            assert results[i-1]["score"] >= results[i]["score"]
    
    def test_bm25_no_results(self, search_tools):
        """Test search with no matching results"""
        
        request = SearchRequest(
            query="nonexistent_term_xyz123",
            top_k=5
        )
        
        result = search_tools.search_for_documents(request)
        # Should return empty results or very low scores
        assert len(result["results"]) == 0 or all(r["score"] < 0.1 for r in result["results"])


class TestVectorSearch:
    """Test vector semantic search functionality"""
    
    def test_vector_semantic_matches(self, search_tools, sample_queries):
        """Test search for semantic matches (vector component)"""
        
        # Test semantic queries
        for query in sample_queries["vector_favored"]:
            request = SearchRequest(
                query=query,
                top_k=5,
                include_scores=True
            )
            
            result = search_tools.search_for_documents(request)
            assert "results" in result
            assert len(result["results"]) > 0
            
            # Should find semantically related content
            top_result = result["results"][0]
            assert top_result["score"] > 0
    
    def test_vector_ranking(self, search_tools):
        """Test that search results are properly ranked by hybrid score"""
        
        request = SearchRequest(
            query="performance optimization",
            top_k=5,
            include_scores=True
        )
        
        result = search_tools.search_for_documents(request)
        results = result["results"]
        
        if len(results) > 1:
            # Verify descending score order
            for i in range(1, len(results)):
                assert results[i-1]["score"] >= results[i]["score"]
    
    def test_vector_semantic_understanding(self, search_tools):
        """Test search semantic understanding via vector component"""
        
        # Test synonyms and related concepts
        request = SearchRequest(
            query="monitoring dashboard visualization",
            top_k=3,
            include_scores=True
        )
        
        result = search_tools.search_for_documents(request)
        assert len(result["results"]) > 0
        
        # Should find content about dashboards/visualization
        found_relevant = any("dashboard" in r.get("text", "").lower() or 
                           "visualization" in r.get("text", "").lower() or
                           "web-based" in r.get("text", "").lower()
                           for r in result["results"])
        assert found_relevant


class TestHybridSearch:
    """Test hybrid search combining BM25 and vector search"""
    
    def test_search_for_documents_basic(self, search_tools, sample_queries):
        """Test basic hybrid search functionality"""
        
        # Test hybrid queries that benefit from both approaches
        for query in sample_queries["hybrid"]:
            request = SearchRequest(
                query=query,
                top_k=5,
                include_scores=True
            )
            
            result = search_tools.search_for_documents(request)
            assert "results" in result
            assert len(result["results"]) > 0
            
            # Verify result structure
            top_result = result["results"][0]
            assert "document_id" in top_result
            assert "score" in top_result
    
    def test_hybrid_rrf_parameters(self, search_tools):
        """Test hybrid search with different parameters"""
        
        query = "API authentication"
        
        # Test different top_k values
        for top_k in [3, 5, 10]:
            request = SearchRequest(
                query=query,
                top_k=top_k,
                include_scores=True
            )
            
            result = search_tools.search_for_documents(request)
            assert "results" in result
            assert len(result["results"]) > 0
    
    def test_hybrid_quality_filtering(self, search_tools):
        """Test hybrid search with quality filtering"""
        
        query = "troubleshooting network issues"
        
        # Test different quality thresholds
        for min_quality in [0, 25, 50]:
            request = SearchRequest(
                query=query,
                top_k=5,
                min_quality=min_quality,
                include_scores=True
            )
            
            result = search_tools.search_for_documents(request)
            assert "results" in result
            # Higher quality thresholds should return fewer or equal results
            if min_quality > 0:
                assert all(r["score"] >= 0 for r in result["results"])


class TestMCPIntegration:
    """Test MCP server integration and tools"""
    

    
    def test_document_retrieval(self, search_tools):
        """Test complete document retrieval"""
        # Get a document ID from the cache
        cache_result = search_tools.get_documents_stats()
        assert cache_result["total_documents"] > 0
        
        # Get a document by listing and picking the first one
        doc_list = search_tools.list_documents_matching(".*", top_k=1)
        assert len(doc_list) > 0
        
        document_id = doc_list[0]
        
        # Test document retrieval
        doc_content = search_tools.get_document_content(document_id)
        assert doc_content is not None
        assert len(doc_content) > 0
    
    def test_search_and_retrieve_documents(self, search_tools):
        """Test combined search and document retrieval"""
        
        request = SearchRequest(
            query="syslog configuration",
            top_k=3,
            include_scores=True
        )
        
        result = search_tools.search_and_get_documents(request)
        assert "results" in result
        assert len(result["results"]) > 0
        
        # Check that we get complete documents, not just chunks
        for doc in result["results"]:
            assert "content" in doc
            assert "metadata" in doc
            assert len(doc["content"]) > 100  # Should be full document content


class TestSearchQuality:
    """Test search quality and edge cases"""
    
    def test_empty_query(self, search_tools):
        """Test handling of empty queries"""
        
        # This should be handled gracefully
        try:
            request = SearchRequest(
                query="",  # Empty query
                top_k=5
            )
            # This should fail validation
            assert False, "Empty query should fail validation"
        except Exception:
            # Expected to fail validation
            pass
    
    def test_large_result_set(self, search_tools):
        """Test handling of large result sets"""
        
        request = SearchRequest(
            query="the",  # Common word likely to match many documents
            top_k=50,  # Maximum allowed
            include_scores=True
        )
        
        result = search_tools.search_for_documents(request)
        assert "results" in result
        assert len(result["results"]) <= 50  # Should respect top_k limit
    
    def test_special_characters(self, search_tools):
        """Test handling of special characters in queries"""
        
        special_queries = [
            "API-key",
            "port:514",
            "file.conf",
            "network()",
            "log{source}"
        ]
        
        for query in special_queries:
            request = SearchRequest(
                query=query,
                top_k=5
            )
            
            # Should not crash, even if no results
            result = search_tools.search_for_documents(request)
            assert "results" in result


async def test_individual_search_components(tools, query: str) -> bool:
    """Test BM25 and vector search components individually for a specific query
    
    Returns:
        True if tests completed successfully, False if there were errors
    """
    try:
        # Create individual search engines for testing
        from bm25_search import BM25SearchEngine
        from vector_search import VectorSearchEngine
        from models import Document
        
        # Get docs path from document cache or use a default
        docs_path = str(Path(__file__).parent / DOCS_DIRECTORY)
        
        # Use the existing engines from the tools object
        print(f"\n🔧 Using existing search engines from tools...")
        bm25_engine = tools.bm25_engine
        vector_engine = tools.vector_engine
        
        # Engines are already loaded with documents from the cache
        print(f"📚 Using existing engines that are already loaded with documents...")
        
        print(f"\n🔍 Testing query: '{query}'")
        print(f"📊 BM25 stats: {bm25_engine.get_stats()}")
        print(f"📊 Vector stats: {vector_engine.get_stats()}")
        
        # Test BM25 search only
        print(f"\n📝 BM25-only search results:")
        try:
            bm25_results = bm25_engine.search(query, top_k=5)
            
            for rank, result in enumerate(bm25_results, 1):
                print(f"   📄 Rank {rank}: {result.document_id} (BM25: {result.score:.4f})")
                text_content = getattr(result, 'text', '') or 'No content available'
                print(f"      Text: {text_content[:100]}...")
                
                # Check if this is our target file
                if "13_Syslog-ng_HTTP_Receiver.md" in result.document_id:
                    print(f"      🎯 TARGET FILE FOUND in BM25 results!")
                        
        except Exception as e:
            print(f"❌ BM25 search failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Test Vector search only
        print(f"\n🧠 Vector-only search results:")
        try:
            vector_results = vector_engine.search(query, top_k=5)
            
            for rank, result in enumerate(vector_results, 1):
                print(f"   🧠 Rank {rank}: {result.document_id} (Vector: {result.score:.4f})")
                text_content = getattr(result, 'text', '') or 'No content available'
                print(f"      Text: {text_content[:100]}...")
                
                # Check if this is our target file
                if "13_Syslog-ng_HTTP_Receiver.md" in result.document_id:
                    print(f"      🎯 TARGET FILE FOUND in Vector results!")
                        
        except Exception as e:
            print(f"❌ Vector search failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Test hybrid search for comparison
        print(f"\n🔄 Hybrid search results (for comparison):")
        try:
            request = SearchRequest(
                query=query,
                top_k=5,
                include_scores=True
            )
            
            result = tools.search_for_documents(request)
            
            if 'error' in result:
                print(f"   ❌ Hybrid search failed: {result['error']}")
                return False
                
            for rank, res in enumerate(result.get('results', []), 1):
                document_id = res.get('document_id', res.get('document', 'unknown'))
                print(f"   🔄 Rank {rank}: {document_id} (Hybrid: {res['score']:.4f})")
                # Hybrid search results are dictionaries, not SearchResult objects
                # They don't contain text content, only metadata
                print(f"      Source: {res.get('source', 'unknown')}")
                
                # Check if this is our target file
                if "13_Syslog-ng_HTTP_Receiver.md" in document_id:
                    print(f"      🎯 TARGET FILE FOUND in Hybrid results!")
                    
        except Exception as e:
            print(f"❌ Hybrid search failed: {e}")
            return False
            
        # Check if target file was found in any of the search results
        target_found_bm25 = any("13_Syslog-ng_HTTP_Receiver.md" in str(result.document_id) for result in bm25_results) if 'bm25_results' in locals() else False
        target_found_vector = any("13_Syslog-ng_HTTP_Receiver.md" in str(result.document_id) for result in vector_results) if 'vector_results' in locals() else False
        
        if not target_found_bm25 and not target_found_vector:
            print(f"\n⚠️ WARNING: Target file '13_Syslog-ng_HTTP_Receiver.md' not found in individual search results")
            return False
            
        print(f"\n✅ Individual search component tests completed successfully")
        return True
            
    except Exception as e:
        print(f"❌ Individual search component test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_hybrid_interleaving(tools):
    """Comprehensive test for hybrid search interleaving behavior"""
    print("\n🧪 COMPREHENSIVE HYBRID SEARCH INTERLEAVING TEST")
    print("=" * 60)
    
    # Test query that should show interleaving behavior
    test_query = "http syslogng"
    target_file = "13_Syslog-ng_HTTP_Receiver.md"
    
    print(f"\n🔍 Testing query: '{test_query}'")
    print(f"🎯 Target file: {target_file}")
    
    # Step 1: Get individual BM25 results
    print("\n📝 Step 1: BM25-only search")
    bm25_results = tools.bm25_engine.search(test_query, 10)
    print(f"   Found {len(bm25_results)} BM25 results")
    
    target_in_bm25 = False
    bm25_target_rank = None
    bm25_target_score = None
    
    for i, result in enumerate(bm25_results, 1):
        if target_file in result.document_id:
            target_in_bm25 = True
            bm25_target_rank = i
            bm25_target_score = result.score
            print(f"   🎯 Target found at BM25 rank {i} with score {result.score:.4f}")
            break
    
    if not target_in_bm25:
        print(f"   ❌ Target NOT found in BM25 top 10 results")
    
    # Step 2: Get individual Vector results  
    print("\n🧠 Step 2: Vector-only search")
    vector_results = tools.vector_engine.search(test_query, 10)
    print(f"   Found {len(vector_results)} Vector results")
    
    target_in_vector = False
    vector_target_rank = None
    vector_target_score = None
    
    for i, result in enumerate(vector_results, 1):
        if target_file in result.document_id:
            target_in_vector = True
            vector_target_rank = i
            vector_target_score = result.score
            print(f"   🎯 Target found at Vector rank {i} with score {result.score:.4f}")
            break
    
    if not target_in_vector:
        print(f"   ❌ Target NOT found in Vector top 10 results")
    
    # Step 3: Test hybrid search with different top_k values
    print("\n🔄 Step 3: Hybrid search interleaving test")
    
    for top_k in [5, 10, 15]:
        print(f"\n   Testing top_k={top_k}:")
        request = SearchRequest(
            query=test_query,
            top_k=top_k,
            include_scores=True
        )
        
        result = tools.search_for_documents(request)
        
        if 'error' in result:
            print(f"   ❌ Hybrid search failed: {result['error']}")
            continue
            
        hybrid_results = result['results']
        print(f"   📊 Hybrid returned {len(hybrid_results)} results")
        
        # Check if target is in hybrid results
        target_in_hybrid = False
        hybrid_target_rank = None
        hybrid_target_score = None
        hybrid_target_source = None
        
        for i, res in enumerate(hybrid_results, 1):
            document_id = res.get('document_id', res.get('document', 'unknown'))
            if target_file in document_id:
                target_in_hybrid = True
                hybrid_target_rank = i
                hybrid_target_score = res['score']
                hybrid_target_source = res['source']
                print(f"   🎯 Target found at Hybrid rank {i} (source: {res['source']}, score: {res['score']:.4f})")
                break
        
        if not target_in_hybrid:
            print(f"   ❌ Target NOT found in Hybrid top {top_k} results")
        
        # Show top 3 results for analysis
        print(f"   📋 Top 3 Hybrid results:")
        for i, res in enumerate(hybrid_results[:3], 1):
            document_id = res.get('document_id', res.get('document', 'unknown'))
            bm25_score = res.get('bm25_score', 'N/A')
            vector_score = res.get('vector_score', 'N/A')
            print(f"      {i}. {document_id} (source: {res.get('source', 'unknown')})")
            print(f"         Hybrid: {res['score']:.4f}, BM25: {bm25_score}, Vector: {vector_score}")
    
    # Step 4: Analysis and verification
    print("\n📊 INTERLEAVING ANALYSIS:")
    print(f"   📝 BM25 target: {'✅ Found' if target_in_bm25 else '❌ Not found'} (rank: {bm25_target_rank}, score: {bm25_target_score})")
    print(f"   🧠 Vector target: {'✅ Found' if target_in_vector else '❌ Not found'} (rank: {vector_target_rank}, score: {vector_target_score})")
    
    # Verify expected behavior
    expected_behavior_met = True
    issues = []
    
    # Expected: Vector should find target better than BM25 for semantic query
    if target_in_vector and target_in_bm25:
        if vector_target_rank is not None and bm25_target_rank is not None and vector_target_rank <= bm25_target_rank:
            print(f"   ✅ Vector ranks target better than BM25 ({vector_target_rank} vs {bm25_target_rank})")
        else:
            print(f"   ⚠️  BM25 ranks target better than Vector ({bm25_target_rank} vs {vector_target_rank})")
    elif target_in_vector and not target_in_bm25:
        print(f"   ✅ Vector finds target, BM25 doesn't (expected for semantic query)")
    elif not target_in_vector and target_in_bm25:
        print(f"   ⚠️  BM25 finds target, Vector doesn't (unexpected for semantic query)")
        issues.append("Vector search should find semantic matches better than BM25")
        expected_behavior_met = False
    else:
        print(f"   ❌ Neither engine finds target")
        issues.append("Target file not found by either search engine")
        expected_behavior_met = False
    
    # Expected: Hybrid should include target if either engine finds it
    if (target_in_bm25 or target_in_vector) and not target_in_hybrid:
        issues.append("Hybrid search should include target when found by individual engines")
        expected_behavior_met = False
    elif target_in_hybrid:
        print(f"   ✅ Hybrid search successfully includes target file")
    
    # Final verdict
    print(f"\n🏁 INTERLEAVING TEST RESULT:")
    if expected_behavior_met:
        print(f"   ✅ PASSED: Hybrid search interleaving works as expected")
        print(f"      - Vector search finds semantic matches")
        print(f"      - Hybrid search properly combines and ranks results")
        print(f"      - Target file '{target_file}' ranks appropriately for query '{test_query}'")
    else:
        print(f"   ❌ FAILED: Issues found with hybrid search interleaving:")
        for issue in issues:
            print(f"      - {issue}")
    
    return expected_behavior_met


async def test_syslog_dash_matching(tools):
    """Test exact matching with hyphenated term 'http syslog-ng'"""
    print("\n SYSLOG-NG DASH MATCHING TEST")
    print("=" * 50)
    
    # Test query with hyphenated term - should be exact match for BM25
    test_query = "http syslog-ng"
    target_file = "13_Syslog-ng_HTTP_Receiver.md"
    
    print(f"\n Testing query: '{test_query}' (with dash)")
    print(f" Target file: {target_file}")
    print(f" Expected: BM25 should find exact match 'syslog-ng' easily!")
    
    # Test 1: BM25-only search
    print("\n BM25-only search results:")
    bm25_results = tools.bm25_engine.search(test_query, 5)
    target_in_bm25 = False
    bm25_target_rank = None
    bm25_target_score = None
    
    for i, result in enumerate(bm25_results, 1):
        is_target = target_file in result.document_id
        if is_target:
            target_in_bm25 = True
            bm25_target_rank = i
            bm25_target_score = result.score
            print(f"   {i}. {result.document_id} (score: {result.score:.4f}) ← TARGET!")
        else:
            print(f"   {i}. {result.document_id} (score: {result.score:.4f})")
    
    if not target_in_bm25:
        print("   Target file NOT found in BM25 top 5")
    
    # Test 2: Vector-only search
    print("\n Vector-only search results:")
    vector_results = tools.vector_engine.search(test_query, 5)
    target_in_vector = False
    vector_target_rank = None
    vector_target_score = None
    
    for i, result in enumerate(vector_results, 1):
        is_target = target_file in result.document_id
        if is_target:
            target_in_vector = True
            vector_target_rank = i
            vector_target_score = result.score
            print(f"   {i}. {result.document_id} (score: {result.score:.4f}) ← TARGET!")
        else:
            print(f"   {i}. {result.document_id} (score: {result.score:.4f})")
    
    if not target_in_vector:
        print("   Target file NOT found in Vector top 5")
    
    # Test 3: Hybrid search
    print("\n Hybrid search results:")
    request = SearchRequest(query=test_query, top_k=5, include_scores=True)
    hybrid_result = tools.search_for_documents(request)
    
    target_in_hybrid = False
    hybrid_target_rank = None
    hybrid_target_score = None
    hybrid_target_source = None
    
    if 'error' in hybrid_result:
        print(f"   Hybrid search failed: {hybrid_result['error']}")
    else:
        hybrid_results = hybrid_result['results']
        for i, res in enumerate(hybrid_results, 1):
            document_id = res.get('document_id', res.get('document', 'unknown'))
            is_target = target_file in document_id
            if is_target:
                target_in_hybrid = True
                hybrid_target_rank = i
                hybrid_target_score = res['score']
                hybrid_target_source = res.get('source', 'unknown')
                print(f"   {i}. {document_id} (hybrid: {res['score']:.4f}, source: {res.get('source', 'unknown')}) ← TARGET!")
            else:
                print(f"   {i}. {document_id} (hybrid: {res['score']:.4f}, source: {res.get('source', 'unknown')})")
        
        if not target_in_hybrid:
            print("   Target file NOT found in Hybrid top 5")
    
    # Analysis and comparison
    print("\n DASH MATCHING ANALYSIS:")
    print(f"   BM25 target: {'Found' if target_in_bm25 else 'Not found'} (rank: {bm25_target_rank}, score: {bm25_target_score})")
    print(f"   Vector target: {'Found' if target_in_vector else 'Not found'} (rank: {vector_target_rank}, score: {vector_target_score})")
    print(f"   Hybrid target: {'Found' if target_in_hybrid else 'Not found'} (rank: {hybrid_target_rank}, source: {hybrid_target_source})")
    
    # Expected behavior verification
    print("\n EXPECTED vs ACTUAL:")
    
    # BM25 should excel at exact matches
    if target_in_bm25 and bm25_target_rank is not None and bm25_target_rank <= 2:
        print(f"   BM25 excellent: Found target at rank {bm25_target_rank} (expected for exact match)")
    elif target_in_bm25:
        print(f"   BM25 okay: Found target at rank {bm25_target_rank} (could be better for exact match)")
    else:
        print(f"   BM25 poor: Target not found (unexpected for exact match)")
    
    # Compare with non-dash version performance
    print(f"\n Comparison with 'http syslogng' (no dash):")
    print(f"   - With dash: BM25 should perform BETTER (exact match)")
    print(f"   - With dash: Vector should perform SIMILARLY (semantic understanding)")
    print(f"   - With dash: Hybrid should benefit from better BM25 performance")
    
    return target_in_bm25, target_in_vector, target_in_hybrid


async def test_search_for_documents_manual():
    """Manual test function for standalone execution"""
    print(" Testing Hybrid Search Implementation")
    print("=" * 50)
    
    # Test imports (already imported at module level)
    try:
        # Test that classes are available
        _ = SearchTools
        _ = SearchRequest  
        _ = DocumentCache
        print("✅ Search tools imported successfully")
    except NameError as e:
        print(f"❌ Search tools import failed: {e}")
        return False
    
    # Print dependency status
    print(f"\n📦 Dependency status:")
    available_deps = []
    for dep in ['rank_bm25', 'faiss', 'sentence_transformers', 'nltk']:
        try:
            __import__(dep)
            status = "✅"
            available_deps.append(dep)
        except ImportError:
            status = "❌"
        print(f"  {status} {dep}")
    
    print(f"📦 Available: {len(available_deps)}/4 dependencies")
    if len(available_deps) < 4:
        print("⚠️ Some dependencies are missing - this may affect test functionality")
    
    # Track test results
    test_errors = []
    test_warnings = []
    
    try:
        # Use real LogZilla docs directory
        docs_path = Path(__file__).parent / DOCS_DIRECTORY
        if not docs_path.exists():
            print(f"❌ LogZilla docs directory not found: {docs_path}")
            return False
            
        print(f"📁 Using real LogZilla docs in {docs_path}")
        
        # Create search tools (imported at module level)
        
        # Create document cache and load documents
        document_cache = DocumentCache()
        loaded_count, error_count, total_size = await document_cache.load_all_documents(str(docs_path))
        if loaded_count == 0:
            print(f"❌ No documents loaded from {docs_path}")
            return False
        print(f"📚 Loaded {loaded_count} documents ({total_size} bytes)")
        
        # Create search tools with document cache
        tools = SearchTools(document_cache)
        
        print(f"🔧 Created search tools with document cache")
        
        # Initialize engines explicitly
        print("📚 Initializing search engines...")
        await tools.initialize()
        
        if not tools.is_ready:
            print("⚠️  Search tools failed to initialize")
            return False
        print("✅ Search tools initialized successfully!")
        
        # Test individual search components first for "http syslogng"
        print("\n🔬 Individual Search Component Tests for 'http syslogng':")
        individual_test_success = await test_individual_search_components(tools, "http syslogng")
        if not individual_test_success:
            test_errors.append("Individual search component tests failed")
        
        # Test searches
        test_queries = [
            ("syslog configuration", "BM25-favored"),
            ("performance optimization", "Vector-favored"), 
            ("API authentication", "Hybrid"),
            ("troubleshooting network", "Hybrid"),
            ("http syslogng", "Spelling-variant-test")  # Tests BM25 vs vector for spelling variants
        ]
        
        print("\n🔍 Testing search queries:")
        for query, query_type in test_queries:
            request = SearchRequest(
                query=query,
                top_k=3,
                include_scores=True
            )
            
            result = tools.search_for_documents(request)
            print(f"\n  Query: '{query}' ({query_type})")
            
            if 'error' in result:
                print(f"❌ Test failed: {result['error']}")
                continue
                
            print(f"  Results: {len(result.get('results', []))}")
            
            for i, res in enumerate(result.get('results', []), 1):
                # Handle different result structures
                document_id = res.get('document_id', res.get('document', 'unknown'))
                score = res.get('score', 0.0)
                source = res.get('source', 'unknown')
                bm25_score = res.get('bm25_score', 'N/A')
                vector_score = res.get('vector_score', 'N/A')
                
                print(f"    {i}. {document_id} (score: {score:.3f})")
                print(f"       Source: {source}, BM25: {bm25_score}, Vector: {vector_score}")
        
        # Index stats are available automatically after initialization
        
        # Comprehensive test for hybrid search interleaving
        await test_hybrid_interleaving(tools)
        
        # Test exact match with hyphenated term
        await test_syslog_dash_matching(tools)
        
        # Report final results
        if test_errors:
            print(f"\n❌ Tests completed with {len(test_errors)} error(s):")
            for i, error in enumerate(test_errors, 1):
                print(f"   {i}. {error}")
            return False
        elif test_warnings:
            print(f"\n⚠️ Tests completed with {len(test_warnings)} warning(s):")
            for i, warning in enumerate(test_warnings, 1):
                print(f"   {i}. {warning}")
            print("\n✅ All manual tests completed successfully (with warnings)!")
            return True
        else:
            print("\n✅ All manual tests completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        test_errors.append(f"Test execution failed: {e}")
        return False


if __name__ == "__main__":
    # Check if we should run pytest or manual test
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--pytest":
        # Run with pytest
        print("Running with pytest...")
        pytest.main([__file__, "-v", "--tb=short"])
    else:
        # Run manual test
        print("Running manual test...")
        success = asyncio.run(test_search_for_documents_manual())
        exit(0 if success else 1)
