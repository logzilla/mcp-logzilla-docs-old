#!/usr/bin/env python3
"""
In-Memory Document Cache for Fast Retrieval
==========================================

Stores complete document contents in memory for fast access during search operations.
Optimized for documentation servers where memory usage is acceptable for performance gains.
"""

import logging
import uuid
import fnmatch
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any, Callable
from dataclasses import dataclass
from datetime import datetime
import os

logger = logging.getLogger(__name__)


@dataclass
class CachedDocument:
    """Complete document stored in memory for fast retrieval"""
    id: str
    name: str
    path: str
    content: str
    size: int
    created_at: datetime
    updated_at: datetime
    file_modified: float  # os.path.getmtime for staleness detection
    
    @property
    def word_count(self) -> int:
        """Get word count of document"""
        return len(self.content.split())
    
    @property
    def line_count(self) -> int:
        """Get line count of document"""
        return len(self.content.splitlines())
    
    def __str__(self) -> str:
        """Human-readable string representation"""
        return f"CachedDocument(id='{self.id}', name='{self.name}', size={self.size}, created_at={self.created_at.strftime('%Y-%m-%d %H:%M:%S')}, updated_at={self.updated_at.strftime('%Y-%m-%d %H:%M:%S')})"
    
    def __repr__(self) -> str:
        """Developer-friendly string representation"""
        return f"CachedDocument(id={self.id!r}, name={self.name!r}, size={self.size}, created_at={self.created_at!r}, updated_at={self.updated_at!r})"
    


class DocumentCache:
    """
    In-memory cache of complete document contents for fast retrieval
    
    Features:
    - Loads all documents into memory at startup
    - Detects file changes and updates cache
    - Provides fast document lookup by ID
    - Memory-efficient storage with configurable limits
    """
    
    def __init__(self):
        """
        Initialize document cache
        
        Args:
            docs_path: Path to documentation directory
            max_file_size: Maximum file size to cache (default 10MB)
        """
        self._documents: Dict[str, CachedDocument] = {}
        self._total_size = 0
        self._last_scan = None
        self._loaded_count = 0
        self._error_count = 0
        self._loaded_paths = []
        
        logger.info(f"Initialized new DocumentCache")
        
   
    @property
    def documents(self) -> Dict[str, CachedDocument]:
        """Access to the documents dictionary"""
        return self._documents
    
    @property 
    def total_size(self) -> int:
        """Total size of cached documents in bytes"""
        return self._total_size
    
    @property
    def last_scan(self) -> Optional[datetime]:
        """Timestamp of last document scan"""
        return self._last_scan
    
    @last_scan.setter
    def last_scan(self, value: datetime) -> None:
        """Set the last scan timestamp"""
        self._last_scan = value
    
    
    def _generate_document_id(self, doc_attributes: Dict[str, Any]) -> str:
        """
        Generate document ID from document attributes
        
        Args:
            doc_attributes: Dictionary containing document metadata including 'name'
            
        Returns:
            Unique document ID in format: name-uuid
        """
        doc_name = doc_attributes.get("name", "unknown")
        return f"{doc_name}-{str(uuid.uuid4())}"
    
    def get_loaded_paths(self) -> List[Tuple[str, List[str]]]:
        """
        Get list of loaded paths
        """
        return self._loaded_paths
    
    def remove_loaded_path(self, tuple: Tuple[str, List[str]]) -> None:
        """
        Remove documents from cache that match the specified path and file patterns
        
        Args:
            tuple: (docs_path, file_patterns) - path and list of wildcard patterns to match
        """
        if tuple not in self._loaded_paths:
            return
        
        file_patterns = tuple[1]
        docs_path = tuple[0]
        
        # Collect document IDs to remove (avoid modifying dict while iterating)
        docs_to_remove = []
        
        for document_id, document in self._documents.items():
            # Check if document path matches the target path
            if document.path == docs_path:
                # Check if document name matches any of the file patterns
                for pattern in file_patterns:
                    if fnmatch.fnmatch(document.name, pattern):
                        docs_to_remove.append(document_id)
                        break  # Found a match, no need to check other patterns
        
        # Remove the documents and update totals
        for document_id in docs_to_remove:
            document = self._documents[document_id]
            del self._documents[document_id]
            self._total_size -= document.size
        
        # Remove from loaded paths
        self._loaded_paths.remove((docs_path, file_patterns))
    
    async def load_all_documents(self, 
                           docs_path: str, 
                           file_patterns: List[str] = ['*.md', '*.txt', '*.html', '*.htm', '*.rst'], 
                           max_file_size: int = 10 * 1024 * 1024,
                           on_load_fn: Optional[Callable[[int, int], None]] = None) -> tuple[int, int, int]:
        """
        Load all documents from the docs directory into memory
        
        Args:
            docs_path: Path to the documents directory
            file_patterns: List of file patterns to match (e.g., ['*.md', '*.txt'])
            max_file_size: Maximum file size in bytes to load
        
        Returns:
            Tuple of (loaded_count, total_size, error_count)
        """
        # Convert string path to Path object
        docs_path_obj = Path(docs_path)
        
        if not docs_path_obj.exists():
            logger.warning(f"Documents directory not found: {docs_path}")
            raise FileNotFoundError(f"Documents directory not found: {docs_path}")
        
        # Initialize counters
        loaded_count = 0
        error_count = 0
        
        # Find all text files
        all_files = []
        for pattern in file_patterns:
            all_files.extend(docs_path_obj.rglob(pattern))
        
        logger.info(f"Found {len(all_files)} files to cache from {docs_path}")
        
        for file_path in all_files:
            try:
                # Check file size
                file_stat = file_path.stat()
                if file_stat.st_size > max_file_size:
                    logger.warning(f"Skipping large file: {file_path} ({file_stat.st_size} bytes)")
                    continue
                
                # Read file content
                content = file_path.read_text(encoding='utf-8', errors='replace')
                
                doc_attributes = {
                    "name": file_path.name,  # filename with extension
                    "path": str(file_path.parent),  # directory portion only
                    "content": content,
                    "size": len(content.encode('utf-8')),
                    "created_at": datetime.fromtimestamp(file_stat.st_ctime),
                    "updated_at": datetime.fromtimestamp(file_stat.st_mtime),
                    "file_modified": file_stat.st_mtime
                }
                # Generate document ID (name + uuid)
                document_id = self._generate_document_id(doc_attributes)
                doc_attributes["id"] = document_id
                
                # Create cached document
                cached_doc = CachedDocument(**doc_attributes)

                # Store in cache
                self._documents[document_id] = cached_doc
                self._total_size += cached_doc.size
                loaded_count += 1
                
            except Exception as e:
                logger.error(f"Failed to cache document {file_path}: {e}")
                error_count += 1
        
        # Update scan timestamp and track loaded paths
        self._last_scan = datetime.now()
        loaded_paths_key = (docs_path, file_patterns)
        self._loaded_paths.append(loaded_paths_key)
        
        
        # Log summary
        size_mb = self._total_size / (1024 * 1024)
        logger.info(f"Cached {loaded_count} documents ({size_mb:.1f} MB total)")
        
        if on_load_fn:
            on_load_fn(loaded_count, error_count)
        
        return loaded_count, self._total_size, error_count
    
    def get_document(self, document_id: str) -> Optional[CachedDocument]:
        """
        Get document by ID from cache
        
        Args:
            document_id: Document identifier (relative path)
            
        Returns:
            CachedDocument if found, None otherwise
        """
        return self._documents.get(document_id)
    
    def get_document_content(self, document_id: str) -> Optional[str]:
        """
        Get document content by ID
        
        Args:
            document_id: Document identifier
            
        Returns:
            Document content string if found, None otherwise
        """
        doc = self.get_document(document_id)
        return doc.content if doc else None
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache statistics
        """
        return {
            "document_count": len(self._documents),
            "total_size_bytes": self._total_size,
            "total_size_mb": round(self._total_size / (1024 * 1024), 2),
            "last_scan": self._last_scan.isoformat() if self._last_scan else None,
        }

