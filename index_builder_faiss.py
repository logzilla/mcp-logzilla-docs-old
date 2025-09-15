#!/usr/bin/env python3
"""
FAISS Index Builder
===================

Creates FAISS index and metadata files from source documents.
This script processes documents, chunks them, creates embeddings, and saves
the FAISS index and metadata files needed by FaissSearchEngine.
"""

import argparse
from bs4 import BeautifulSoup
from datetime import datetime
import faiss
import logging
import numpy as np
import os
from pathlib import Path
import pickle
import re
from sentence_transformers import SentenceTransformer
import time
from typing import Dict, List, Optional, Union


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Constants:
    DEFAULT_SENTENCE_TRANSFORMER_MODEL = "thenlper/gte-large"
    DEFAULT_CHUNK_SIZE = 800
    DEFAULT_CHUNK_OVERLAP = 150


class DocumentIndexBuilder:
    """Builds FAISS index and metadata from source documents"""
    
    def __init__(self, 
                 model_name: str = Constants.DEFAULT_SENTENCE_TRANSFORMER_MODEL,
                 chunk_size: int = Constants.DEFAULT_CHUNK_SIZE,
                 overlap: int = Constants.DEFAULT_CHUNK_OVERLAP,
                 device: str = "auto"):
        """
        Initialize the index builder
        
        Args:
            model_name: Sentence transformer model to use
            chunk_size: Size of text chunks in characters
            overlap: Overlap between chunks in characters
            device: Device for model inference ("cpu", "cuda", "mps", "auto")
        """
        self.model_name = model_name
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.device = device
        
        # Initialize model
        actual_device = None if device == "auto" else device
        self.model = SentenceTransformer(model_name, device=actual_device)
        self.dimension = self.model.get_sentence_embedding_dimension() or 384
        
        logger.info(f"Initialized builder with model: {model_name}")
        logger.info(f"Embedding dimension: {self.dimension}")
        logger.info(f"Chunk size: {chunk_size}, overlap: {overlap}")
    
    def clean_html_content(self, html_content: str) -> str:
        """Intelligently extract valuable content from HTML
        
        Benefits of preserving HTML-derived content over markdown for LLM indexing:
        - Preserves semantic structure (h1/h2 hierarchy, section/article containers)
        - Maintains link context and relationships (href, title attributes, anchor targets)
        - Enables content classification (table structure, definition lists, figures)
        - Retains essential metadata (id for anchors, alt text for images)
        - Removes presentation noise (CSS classes, tracking attributes, style tags)
        - Filters out navigation/UI elements while keeping content structure
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove noise elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 
                            'aside', 'advertisement']):
            element.decompose()
        
        # Remove elements with noise-indicating classes/IDs
        noise_patterns = ['nav', 'menu', 'sidebar', 'footer', 'header', 
                        'advertisement', 'social', 'share']
        for pattern in noise_patterns:
            for element in soup.find_all(attrs={'class': re.compile(pattern, re.I)}):
                element.decompose()
        
        # Preserve valuable structure but clean attributes
        for tag in soup.find_all():
            # Keep only semantic attributes
            semantic_attrs = ['href', 'title', 'alt', 'id'] 
            tag.attrs = {k: v for k, v in tag.attrs.items() if k in semantic_attrs}
        
        return str(soup)

    def chunk_document(self, text: str, doc_id: int) -> List[Dict]:
        """
        Split document into overlapping chunks
        
        Returns list of chunk dictionaries with metadata
        """
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            
            # Try to break at sentence boundaries
            if end < len(text):
                # Look for sentence endings within the last 100 characters
                last_period = text.rfind('.', start + self.chunk_size - 100, end)
                if last_period > start + self.chunk_size * 0.7:  # Don't make chunks too small
                    end = last_period + 1
            
            chunk_text = text[start:end].strip()
            if chunk_text:  # Only add non-empty chunks
                chunks.append({
                    'text': chunk_text,
                    'start_pos': start,
                    'end_pos': end,
                    'chunk_index': chunk_index,
                    'doc_id': doc_id
                })
                chunk_index += 1
            
            if end >= len(text):
                break
                
            start += self.chunk_size - self.overlap
        
        return chunks
    
    def load_documents_from_directory(self, source_dir: Union[str, Path]) -> List[Dict]:
        """
        Load documents from a directory
        
        Supports .txt, .md, .html files. Extend this method for other formats.
        """
        source_path = Path(source_dir)
        if not source_path.exists():
            raise FileNotFoundError(f"Source directory not found: {source_path}")
        
        documents = []
        doc_id = 0
        
        # Supported file extensions
        supported_extensions = {'.txt', '.md', '.text', '.htm', '.html'}
        
        for file_path in source_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        if file_path.suffix.lower() in ['.htm', '.html']:
                            content = self.clean_html_content(content)
                    
                    if content.strip():  # Only process non-empty files
                        documents.append({
                            'id': doc_id,
                            'name': file_path.name,
                            'path': str(file_path),
                            'size': len(content),
                            'content': content,
                            # no metadata for now
                            'metadata': {},
                            'updated_at': datetime.fromtimestamp(file_path.stat().st_mtime)
                        })
                        doc_id += 1
                        
                except Exception as e:
                    logger.warning(f"Failed to load file {file_path}: {e}")
                    continue
        
        logger.info(f"Loaded {len(documents)} documents from {source_path}")
        return documents
    
    def load_documents_from_list(self, documents: List[Dict]) -> List[Dict]:
        """
        Load documents from a list of dictionaries
        
        Expected format:
        [
            {
                'name': 'document1.txt',
                'content': 'Document content here...',
                'metadata': {...}  # optional
            },
            ...
        ]
        """
        processed_docs = []
        
        for doc_id, doc in enumerate(documents):
            if 'content' not in doc or not doc['content'].strip():
                logger.warning(f"Skipping document {doc_id}: no content")
                continue
            
            processed_doc = {
                'id': doc_id,
                'name': doc.get('name', f'document_{doc_id}'),
                'size': len(doc['content']),
                'content': doc['content'],
                'metadata': doc.get('metadata', {}),
                'updated_at': doc.get('updated_at', datetime.now())
            }
            processed_docs.append(processed_doc)
        
        logger.info(f"Processed {len(processed_docs)} documents from list")
        return processed_docs
    
    def build_index(self, 
                   documents: List[Dict],
                   output_path: Union[str, Path],
                   index_name: str) -> None:
        """
        Build FAISS index and metadata from documents
        
        Args:
            documents: List of document dictionaries
            output_path: Directory to save index and metadata files
            index_name: Base name for output files (will create {index_name}.faiss and {index_name}.pkl)
        """
        if not documents:
            raise ValueError("No documents provided for indexing")
        
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Prepare data structures
        all_chunks = []
        vector_mapping = {}
        documents_metadata = {}
        
        logger.info("Processing documents and creating chunks...")
        
        # Process each document
        for doc in documents:
            doc_id = doc['id']
            
            # Chunk the document
            chunks = self.chunk_document(doc['content'], doc_id)
            
            # Store document metadata
            documents_metadata[doc_id] = {
                'id': doc_id,
                'name': doc['name'],
                'size': doc['size'],
                'content': doc['content'],  # Store full content for retrieval
                'chunks': [chunk['text'] for chunk in chunks],  # Store chunk texts
                'metadata': doc.get('metadata', {}),
                'updated_at': doc.get('updated_at')
            }
            
            # Add chunks to processing list
            for chunk in chunks:
                vector_id = len(all_chunks)
                all_chunks.append(chunk['text'])
                
                # Map vector ID to document and chunk
                vector_mapping[vector_id] = {
                    'doc_id': doc_id,
                    'chunk_index': chunk['chunk_index']
                }
        
        logger.info(f"Created {len(all_chunks)} chunks from {len(documents)} documents")
        
        # Create embeddings
        logger.info("Creating embeddings...")
        start_time = time.time()
        
        # Process in batches to avoid memory issues
        batch_size = 32
        all_embeddings = []
        
        for i in range(0, len(all_chunks), batch_size):
            batch = all_chunks[i:i + batch_size]
            batch_embeddings = self.model.encode(batch, convert_to_numpy=True, show_progress_bar=True)
            all_embeddings.append(batch_embeddings)
            
            if (i // batch_size + 1) % 10 == 0:
                logger.info(f"Processed {i + len(batch)}/{len(all_chunks)} chunks")
        
        # Combine all embeddings
        embeddings = np.vstack(all_embeddings).astype(np.float32)
        embedding_time = time.time() - start_time
        logger.info(f"Created embeddings in {embedding_time:.2f} seconds")
        
        # Build FAISS index
        logger.info("Building FAISS index...")
        
        # Use IndexFlatIP for cosine similarity (after L2 normalization)
        index = faiss.IndexFlatIP(self.dimension)
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add vectors to index
        index.add(embeddings)
        
        logger.info(f"Built FAISS index with {index.ntotal} vectors")
        
        # Create metadata structure
        metadata = {
            'vector_mapping': vector_mapping,
            'documents': documents_metadata,
            'config': {
                'model_name': self.model_name,
                'dimension': self.dimension,
                'chunk_size': self.chunk_size,
                'overlap': self.overlap,
                'total_vectors': len(all_chunks),
                'total_documents': len(documents),
                'created_at': datetime.now(),
                'index_type': 'IndexFlatIP'
            }
        }
        
        # Save files
        index_file = output_dir / f"{index_name}.faiss"
        metadata_file = output_dir / f"{index_name}.pkl"
        
        logger.info(f"Saving FAISS index to {index_file}")
        faiss.write_index(index, str(index_file))
        
        logger.info(f"Saving metadata to {metadata_file}")
        with open(metadata_file, 'wb') as f:
            pickle.dump(metadata, f)
        
        logger.info("Index building completed successfully!")
        logger.info(f"Files created:")
        logger.info(f"  - Index: {index_file}")
        logger.info(f"  - Metadata: {metadata_file}")
        
        # Print statistics
        avg_chunks_per_doc = len(all_chunks) / len(documents)
        logger.info(f"Statistics:")
        logger.info(f"  - Documents: {len(documents)}")
        logger.info(f"  - Chunks: {len(all_chunks)}")
        logger.info(f"  - Average chunks per document: {avg_chunks_per_doc:.1f}")
        logger.info(f"  - Index file size: {index_file.stat().st_size / 1024 / 1024:.1f} MB")
        logger.info(f"  - Metadata file size: {metadata_file.stat().st_size / 1024 / 1024:.1f} MB")


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="Build FAISS index from source documents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  %(prog)s -i ./documents -o ./indexes -n my_docs
  %(prog)s --input-directory /path/to/docs --output-directory /path/to/output --index-name technical_docs

Supported file formats: .txt, .md, .text, .html"""
    )
    
    parser.add_argument(
        "-i", "--input-directory",
        type=str,
        required=True,
        help="Directory containing source documents to index"
    )
    
    parser.add_argument(
        "-o", "--output-directory",
        type=str,
        required=True,
        help="Directory where index files will be saved"
    )
    
    parser.add_argument(
        "-n", "--index-name",
        type=str,
        required=True,
        help="Base name for the index files (creates {name}.faiss and {name}.pkl)"
    )
    
    parser.add_argument(
        "--model-name",
        type=str,
        default=Constants.DEFAULT_SENTENCE_TRANSFORMER_MODEL,
        help=f"Sentence transformer model to use (default: {Constants.DEFAULT_SENTENCE_TRANSFORMER_MODEL})"
    )
    
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=Constants.DEFAULT_CHUNK_SIZE,
        help=f"Size of text chunks in characters (default: {Constants.DEFAULT_CHUNK_SIZE})"
    )
    
    parser.add_argument(
        "--overlap",
        type=int,
        default=Constants.DEFAULT_CHUNK_OVERLAP,
        help=f"Overlap between chunks in characters (default: {Constants.DEFAULT_CHUNK_OVERLAP})"
    )
    
    parser.add_argument(
        "--device",
        type=str,
        default="auto",
        choices=["auto", "cpu", "cuda", "mps"],
        help="Device for model inference (default: auto)"
    )
    
    return parser.parse_args()


def main() -> int:
    """Main function with command-line argument support"""
    
    # Parse command-line arguments
    args = parse_arguments()
    
    # Validate input directory exists
    input_path = Path(args.input_directory)
    if not input_path.exists():
        logger.error(f"Input directory does not exist: {input_path}")
        return 1
    
    if not input_path.is_dir():
        logger.error(f"Input path is not a directory: {input_path}")
        return 1
    
    # Initialize builder with arguments
    builder = DocumentIndexBuilder(
        model_name=args.model_name,
        chunk_size=args.chunk_size,
        overlap=args.overlap,
        device=args.device
    )
    
    try:
        # Load documents from the specified directory
        logger.info(f"Loading documents from: {args.input_directory}")
        documents = builder.load_documents_from_directory(args.input_directory)
        
        if not documents:
            logger.error(f"No supported documents found in {args.input_directory}")
            logger.info("Supported file extensions: .txt, .md, .text")
            return 1
        
        # Build the index
        logger.info(f"Building index '{args.index_name}' in: {args.output_directory}")
        builder.build_index(documents, args.output_directory, args.index_name)
        
        print(f"\n✅ Index building completed successfully!")
        print(f"Files created:")
        print(f"  - Index: {Path(args.output_directory) / f'{args.index_name}.faiss'}")
        print(f"  - Metadata: {Path(args.output_directory) / f'{args.index_name}.pkl'}")
        print(f"\nYou can now use these files with your FaissSearchEngine:")
        print(f"  - embedding_path: '{args.output_directory}'")
        print(f"  - embedding_name: '{args.index_name}'")
        
        return 0
        
    except Exception as e:
        logger.error(f"Failed to build index: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())