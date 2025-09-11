#!/usr/bin/env python3
"""
Example: Using Contextual Search
===============================

Demonstrates how to use the contextual search functionality to get
expanded text windows around matching chunks.
"""

import asyncio
from context_search import ContextualSearchTools
from document_cache import DocumentCache
from models import SearchRequest


async def demo_contextual_search():
    """Demonstrate contextual search capabilities"""
    
    # Initialize document cache and contextual search tools
    document_cache = DocumentCache()
    search_tools = ContextualSearchTools(document_cache, device="cpu")
    
    # Initialize the search engines
    print("Initializing search engines...")
    await search_tools.initialize()
    
    if not search_tools.is_ready:
        print("Failed to initialize search engines")
        return
    
    # Example search query
    query = "configuration setup"
    
    print(f"\nSearching for: '{query}'")
    print("=" * 50)
    
    # Regular search (document-level results)
    regular_results = search_tools.search_for_documents(SearchRequest(
        query=query,
        top_k=3
    ))
    
    print(f"\nRegular Search Results ({len(regular_results.get('results', []))} documents):")
    for i, result in enumerate(regular_results.get('results', [])[:2]):
        print(f"  {i+1}. {result['document_id']} (score: {result['score']:.4f})")
    
    # Contextual search (chunk-level with surrounding context)
    contextual_results = search_tools.search_with_context(
        SearchRequest(query=query, top_k=3),
        context_size=2,  # 2 chunks before and after
        engine="bm25"    # or "vector" or "hybrid"
    )
    
    print(f"\nContextual Search Results ({len(contextual_results.get('results', []))} chunks with context):")
    print("-" * 50)
    
    for i, result in enumerate(contextual_results.get('results', [])[:2]):
        print(f"\nResult {i+1}: {result['document_id']} (score: {result['score']:.4f})")
        print(f"Matching chunk index: {result['matching_chunk']['index']}")
        
        # Show context structure
        print(f"\nContext structure:")
        print(f"  - Before: {len(result['context_before'])} chunks")
        print(f"  - Matching: 1 chunk")
        print(f"  - After: {len(result['context_after'])} chunks")
        
        # Show the expanded context (first 500 chars)
        print(f"\nExpanded context text:")
        print(f"{'─' * 30}")
        print(result['full_context'][:500] + "..." if len(result['full_context']) > 500 else result['full_context'])
        print(f"{'─' * 30}")


async def demo_chunk_level_search():
    """Demonstrate chunk-level search without context expansion"""
    
    document_cache = DocumentCache()
    search_tools = ContextualSearchTools(document_cache, device="cpu")
    
    await search_tools.initialize()
    
    if not search_tools.is_ready:
        print("Failed to initialize search engines")
        return
    
    query = "error handling"
    
    # Get chunk-level results with details
    chunk_results = search_tools.bm25_engine.search_with_context(
        query=query,
        top_k=5,
        context_size=1,
        return_chunk_details=True  # Return ChunkSearchResult instead of ContextualSearchResult
    )
    
    print(f"\nChunk-level Search Results for '{query}':")
    print("=" * 50)
    
    for i, result in enumerate(chunk_results[:3]):
        print(f"\nChunk {i+1}:")
        print(f"  Document: {result.document_id}")
        print(f"  Chunk Index: {result.chunk_index}")
        print(f"  Chunk ID: {result.chunk_id}")
        print(f"  Score: {result.score:.4f}")
        print(f"  Global Index: {result.global_chunk_index}")


def demo_manual_context_expansion():
    """Show how to manually get context around a specific chunk"""
    
    # This would work with initialized engines
    print("\nManual Context Expansion Example:")
    print("=" * 40)
    print("""
    # Get context around a specific chunk
    engine = search_tools.bm25_engine
    
    # Method 1: Get chunks around a document-specific chunk index
    context_chunks = engine._get_chunk_context(
        document_id="my_doc.md",
        target_chunk_index=5,  # 6th chunk in the document
        context_size=2         # 2 chunks before and after
    )
    
    # Method 2: Access chunks directly by global index
    matching_chunk = engine.chunks[42]  # Global chunk index 42
    adjacent_chunks = engine.chunks[40:45]  # Get chunks 40-44
    
    # Method 3: Get all chunks for a document
    doc_chunks = [chunk for chunk in engine.chunks 
                  if chunk.document_id == "my_doc.md"]
    doc_chunks.sort(key=lambda x: x.chunk_index)
    
    # Find specific chunk and get neighbors
    for i, chunk in enumerate(doc_chunks):
        if "search term" in chunk.content:
            context_start = max(0, i - 2)
            context_end = min(len(doc_chunks), i + 3)
            context_window = doc_chunks[context_start:context_end]
            break
    """)


if __name__ == "__main__":
    print("Contextual Search Demo")
    print("=" * 30)
    
    # Run the contextual search demo
    asyncio.run(demo_contextual_search())
    
    print("\n" + "=" * 50)
    
    # Run the chunk-level search demo
    asyncio.run(demo_chunk_level_search())
    
    # Show manual context expansion examples
    demo_manual_context_expansion()