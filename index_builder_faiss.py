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
import sys
import tiktoken
import time
from typing import Dict, List, Optional, Union

DEBUG = True
if DEBUG:
    import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Constants:
    DEFAULT_SENTENCE_TRANSFORMER_MODEL = "thenlper/gte-large"
    DEFAULT_CHUNK_SIZE = 512  # in tokens
    DEFAULT_CHUNK_OVERLAP = 50  # in tokens (10% overlap)
    DEFAULT_ENCODING = "cl100k_base"  # GPT-4 encoding


class DocumentIndexBuilder:
    """Builds FAISS index and metadata from source documents"""
    
    def __init__(self, 
                 model_name: str = Constants.DEFAULT_SENTENCE_TRANSFORMER_MODEL,
                 chunk_size: int = Constants.DEFAULT_CHUNK_SIZE,
                 overlap: int = Constants.DEFAULT_CHUNK_OVERLAP,
                 device: str = "auto",
                 encoding_name: str = Constants.DEFAULT_ENCODING):
        """
        Initialize the index builder
        
        Args:
            model_name: Sentence transformer model to use
            chunk_size: Size of text chunks in tokens
            overlap: Overlap between chunks in tokens
            device: Device for model inference ("cpu", "cuda", "mps", "auto")
            encoding_name: Tokenizer encoding to use (e.g., "cl100k_base")
        """
        self.model_name = model_name
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.device = device
        self.encoding_name = encoding_name
        
        # Initialize tokenizer if available
        self.tokenizer = tiktoken.get_encoding(encoding_name)
        logger.info(f"Using tiktoken tokenizer: {encoding_name}")
        
        # Initialize model
        actual_device = None if device == "auto" else device
        self.model = SentenceTransformer(model_name, device=actual_device)
        self.dimension = self.model.get_sentence_embedding_dimension() or 384
        
        logger.info(f"Initialized builder with model: {model_name}")
        logger.info(f"Embedding dimension: {self.dimension}")
        logger.info(f"Chunk size: {chunk_size} tokens, overlap: {overlap} tokens")
    
    def clean_html_content(self, html_content: str) -> str:
        """General-purpose HTML cleaning for optimal LLM indexing
        
        Designed to work with any HTML content, not just specific frameworks.
        Extracts semantic content while removing presentation markup and noise.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find main content using common patterns (fallback to body if none found)
        main_content = None
        content_selectors = [
            'main', 'article', '[role="main"]',  # Semantic HTML5
            '.content', '.main-content', '.post-content', '.entry-content',  # Common classes
            '#content', '#main-content', '#post-content',  # Common IDs
            'article.md-content__inner',  # Material/MkDocs
            '.container .row .col',  # Bootstrap patterns
        ]
        
        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content and len(main_content.get_text().strip()) > 100:  # Ensure substantial content
                break
        
        if not main_content:
            main_content = soup.find('body') or soup
        
        soup = BeautifulSoup(str(main_content), 'html.parser')
        
        # Remove noise elements that never contain useful content
        noise_tags = ['script', 'style', 'noscript', 'iframe', 'embed', 'object', 
                     'svg', 'canvas', 'audio', 'video', 'source', 'track']
        for tag in noise_tags:
            for element in soup.find_all(tag):
                element.decompose()
        
        # Remove navigation and UI elements by common patterns
        ui_patterns = [
            # Navigation
            r'nav', r'menu', r'breadcrumb', r'pagination',
            # Headers/Footers  
            r'header', r'footer', r'banner',
            # Sidebars
            r'sidebar', r'aside', r'widget',
            # Social/Sharing
            r'social', r'share', r'follow', r'subscribe',
            # Ads/Tracking
            r'ad', r'advertisement', r'sponsor', r'tracking', r'analytics',
            # UI Controls
            r'button', r'control', r'toggle', r'dropdown', r'modal',
            # Comments (often noisy)
            r'comment', r'discussion'
        ]
        
        for pattern in ui_patterns:
            # Remove by class
            for element in soup.find_all(attrs={'class': re.compile(pattern, re.I)}):
                element.decompose()
            # Remove by ID
            for element in soup.find_all(attrs={'id': re.compile(pattern, re.I)}):
                element.decompose()
            # Remove by role
            for element in soup.find_all(attrs={'role': re.compile(pattern, re.I)}):
                element.decompose()
        
        # Convert semantic HTML to markdown-like format
        # Headings
        for i in range(1, 7):
            for heading in soup.find_all(f'h{i}'):
                text = heading.get_text().strip()
                if text:
                    heading.string = f"{'#' * i} {text}\n"
                    heading.name = 'p'
        
        # Lists
        for ul in soup.find_all('ul'):
            items = []
            for li in ul.find_all('li', recursive=False):  # Only direct children
                item_text = li.get_text().strip()
                if item_text:
                    items.append(f"- {item_text}")
            if items:
                ul.string = '\n'.join(items) + '\n'
                ul.name = 'p'
        
        for ol in soup.find_all('ol'):
            items = []
            for i, li in enumerate(ol.find_all('li', recursive=False), 1):
                item_text = li.get_text().strip()
                if item_text:
                    items.append(f"{i}. {item_text}")
            if items:
                ol.string = '\n'.join(items) + '\n'
                ol.name = 'p'
        
        # Tables - convert to simple text format
        for table in soup.find_all('table'):
            rows = []
            for tr in table.find_all('tr'):
                cells = [td.get_text().strip() for td in tr.find_all(['td', 'th'])]
                if cells and any(cells):  # Skip empty rows
                    rows.append(' | '.join(cells))
            if rows:
                table.string = '\n'.join(rows) + '\n'
                table.name = 'p'
        
        # Links - preserve external, convert internal to text
        for link in soup.find_all('a'):
            href = link.get('href', '').strip()
            text = link.get_text().strip()
            
            if not text:  # Skip empty links
                link.decompose()
                continue
                
            if href.startswith(('http://', 'https://')):
                # Keep external links as markdown
                link.string = f"[{text}]({href})"
            elif href.startswith(('mailto:', 'tel:')):
                # Keep contact links
                link.string = f"[{text}]({href})"
            else:
                # Convert internal/relative links to plain text
                link.string = text
            link.name = 'span'
        
        # Emphasis
        for strong in soup.find_all(['strong', 'b']):
            text = strong.get_text().strip()
            if text:
                strong.string = f"**{text}**"
            strong.name = 'span'
        
        for em in soup.find_all(['em', 'i']):
            text = em.get_text().strip()
            if text:
                em.string = f"*{text}*"
            em.name = 'span'
        
        # Code blocks
        for code in soup.find_all(['code', 'pre']):
            text = code.get_text().strip()
            if text:
                if '\n' in text:  # Multi-line code block
                    code.string = f"```\n{text}\n```"
                else:  # Inline code
                    code.string = f"`{text}`"
            code.name = 'span'
        
        # Remove remaining structural elements but preserve content
        for tag in soup.find_all():
            if tag.name not in ['p', 'span', 'br']:
                tag.unwrap()
        
        # Convert to text and clean up
        text = str(soup)
        
        # Remove HTML entities
        import html
        text = html.unescape(text)
        
        # Simple approach: just add space after every HTML tag removal
        text = re.sub(r'<br\s*/?>', '\n', text)    # Convert <br> to newlines
        text = re.sub(r'</?[^>]+>', ' ', text)     # Remove HTML tags and replace with space
        
        # Only fix obvious punctuation issues, avoid breaking proper nouns
        text = re.sub(r'([.!?:;])([A-Z])', r'\1 \2', text)  # Space after punctuation before capitals
        
        # Normalize whitespace - but preserve newlines as spaces for word boundaries
        text = re.sub(r'[ \t]+', ' ', text)                  # Collapse multiple spaces
        text = re.sub(r'\n', ' ', text)                      # Convert ALL newlines to spaces to prevent compound words
        text = re.sub(r'[ ]+', ' ', text)                    # Collapse multiple spaces again after newline conversion
        text = re.sub(r'^\s+|\s+$', '', text)                # Trim start and end
        
        return text.strip()

    def _split_by_structure(self, text: str) -> List[str]:
        """
        Split text by structural elements (paragraphs, headings) first
        """
        # Split by double newlines (paragraphs)
        paragraphs = re.split(r'\n\s*\n', text)
        
        # Further split very long paragraphs by single newlines
        sections = []
        for para in paragraphs:
            p = para.strip()
            if not p:
                continue
            if self._count_tokens(p) > self.chunk_size * 2:  # Use token-based threshold
                # Split by sentences or newlines
                sentences = re.split(r'(?<=[.!?])\s+|\n', p)
                for s in sentences:
                    s = s.strip()
                    if s:
                        sections.append(s)
            else:
                sections.append(p)
        
        return [s for s in sections if s]
    
    def _count_tokens(self, text: str) -> int:
        """
        Count tokens in text using tiktoken or estimate from characters
        """
        return len(self.tokenizer.encode(text))
    
    def _last_tokens(self, text: str, n: int) -> str:
        """Get the last n tokens from text as a string"""
        ids = self.tokenizer.encode(text)
        if not ids: 
            return ""
        tail = ids[-n:]
        return self.tokenizer.decode(tail)
    
    def _split_sentence_by_tokens(self, text: str, max_tokens: int) -> List[str]:
        """Split a sentence into parts that fit within max_tokens"""
        if not text.strip():
            return []
        
        tokens = self.tokenizer.encode(text)
        if len(tokens) <= max_tokens:
            return [text]
        
        parts = []
        start = 0
        
        while start < len(tokens):
            end = min(start + max_tokens, len(tokens))
            chunk_tokens = tokens[start:end]
            chunk_text = self.tokenizer.decode(chunk_tokens)
            parts.append(chunk_text)
            start = end
        
        return parts
    
    def _create_chunk(self, text: str, doc_id: int, chunk_index: int) -> Dict:
        """Helper to reduce repetition in chunk creation"""
        return {
            'text': text,
            'token_count': self._count_tokens(text),
            'chunk_index': chunk_index,
            'doc_id': doc_id
        }
    
    def _process_large_section(self, section: str, chunks: List[Dict], doc_id: int) -> None:
        """Process sections that are too large for a single chunk"""
        # Split large section by sentences first
        sentences = re.split(r'(?<=[.!?])\s+', section)
        current_chunk_text = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Handle sentences that are too large for any chunk by splitting them
            if self._count_tokens(sentence) > self.chunk_size:
                # Save current chunk if it has content
                if current_chunk_text:
                    chunks.append(self._create_chunk(current_chunk_text, doc_id, len(chunks)))
                    overlap = self._last_tokens(current_chunk_text, self.overlap) if self.overlap > 0 else ""
                    current_chunk_text = overlap
                
                # Split the sentence into token-sized pieces
                sentence_parts = self._split_sentence_by_tokens(sentence, self.chunk_size)
                for part in sentence_parts:
                    # If adding this part would exceed chunk size, save current chunk first
                    test_text = (current_chunk_text + "\n\n" + part) if current_chunk_text else part
                    if self._count_tokens(test_text) > self.chunk_size and current_chunk_text:
                        chunks.append(self._create_chunk(current_chunk_text, doc_id, len(chunks)))
                        overlap = self._last_tokens(current_chunk_text, self.overlap) if self.overlap > 0 else ""
                        current_chunk_text = (overlap + "\n\n" + part) if overlap else part
                    else:
                        current_chunk_text = test_text
            else:
                # Normal sentence processing
                test_text = (current_chunk_text + "\n\n" + sentence) if current_chunk_text else sentence
                if self._count_tokens(test_text) <= self.chunk_size:
                    current_chunk_text = test_text
                else:
                    # Current chunk is full, save it and start new one
                    chunks.append(self._create_chunk(current_chunk_text, doc_id, len(chunks)))
                    overlap = self._last_tokens(current_chunk_text, self.overlap) if self.overlap > 0 else ""
                    current_chunk_text = (overlap + "\n\n" + sentence) if overlap else sentence
        
        # Save any remaining content
        if current_chunk_text:
            chunks.append(self._create_chunk(current_chunk_text, doc_id, len(chunks)))

    def _token_aware_chunk(self, sections: List[str], doc_id: int) -> List[Dict]:
        """
        Create chunks respecting token limits and semantic boundaries with token-accurate overlap
        """
        chunks = []
        current_chunk_text = ""
        
        for section in sections:
            # Handle sections that are too large on their own
            if self._count_tokens(section) > self.chunk_size:
                # If there's a pending chunk, save it first
                if current_chunk_text:
                    chunks.append(self._create_chunk(current_chunk_text, doc_id, len(chunks)))
                    # Start the next chunk with overlap from the one we just saved
                    overlap = self._last_tokens(current_chunk_text, self.overlap) if self.overlap > 0 else ""
                    current_chunk_text = overlap
                
                # Now, process the oversized section
                self._process_large_section(section, chunks, doc_id)
                current_chunk_text = ""  # Reset after processing
                continue

            # If adding the next section fits, append it
            test_text = (current_chunk_text + "\n\n" + section) if current_chunk_text else section
            if self._count_tokens(test_text) <= self.chunk_size:
                current_chunk_text = test_text
            # Otherwise, the current chunk is full. Save it and start a new one.
            else:
                chunks.append(self._create_chunk(current_chunk_text, doc_id, len(chunks)))
                overlap = self._last_tokens(current_chunk_text, self.overlap) if self.overlap > 0 else ""
                current_chunk_text = (overlap + "\n\n" + section) if overlap else section

        # Add the final pending chunk
        if current_chunk_text:
            chunks.append(self._create_chunk(current_chunk_text, doc_id, len(chunks)))

        return chunks
    
    def chunk_document(self, text: str, doc_id: int) -> List[Dict]:
        """
        Split document into overlapping chunks using token-aware semantic boundaries
        
        Returns list of chunk dictionaries with metadata
        """
        if not text.strip():
            return []
        
        # First, split by structural elements
        sections = self._split_by_structure(text)
        
        # Then create token-aware chunks
        chunks = self._token_aware_chunk(sections, doc_id)
        
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
                            'updated_at': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
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
                'updated_at': doc.get('updated_at', datetime.now()).isoformat() if isinstance(doc.get('updated_at'), datetime) else doc.get('updated_at', datetime.now().isoformat())
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
        
        # Guard against empty chunks
        if not all_chunks:
            raise ValueError("No chunks were produced from the input documents; check cleaners/filters.")
        
        # Create embeddings
        logger.info("Creating embeddings...")
        start_time = time.time()
        
        # Use SentenceTransformer's built-in batching instead of manual batching
        embeddings = self.model.encode(
            all_chunks, 
            convert_to_numpy=True, 
            show_progress_bar=True, 
            batch_size=32
        ).astype(np.float32)
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
                'created_at': datetime.now().isoformat(),
                'index_type': 'IndexFlatIP'
            }
        }
        
        # Save files
        index_file = output_dir / f"{index_name}.faiss"
        metadata_file = output_dir / f"{index_name}.pkl"
        if DEBUG:
            with open(f"{index_name}.yaml", "w") as f:
                yaml.dump(metadata, f)
        
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
        help=f"Size of text chunks in tokens (default: {Constants.DEFAULT_CHUNK_SIZE})"
    )
    
    parser.add_argument(
        "--overlap",
        type=int,
        default=Constants.DEFAULT_CHUNK_OVERLAP,
        help=f"Overlap between chunks in tokens (default: {Constants.DEFAULT_CHUNK_OVERLAP})"
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
            logger.info("Supported file extensions: .txt, .md, .text, .htm, .html")
            return 1
        
        # Build the index
        logger.info(f"Building index '{args.index_name}' in: {args.output_directory}")
        builder.build_index(documents, args.output_directory, args.index_name)
        
        print(f"\n✅ Index building completed successfully!")
        print(f"Files created:")
        print(f"  - Index: {Path(args.output_directory) / f'{args.index_name}.faiss'}")
        print(f"  - Metadata: {Path(args.output_directory) / f'{args.index_name}.pkl'}")
        print(f"\nThese files can now be used with FAISS search in the MCP Docs Server:")
        print(f"  - embedding_path: '{args.output_directory}'")
        print(f"  - embedding_name: '{args.index_name}'")
        
        return 0
        
    except Exception as e:
        logger.error(f"Failed to build index: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())