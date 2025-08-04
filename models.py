#!/usr/bin/env python3
"""
Shared models and data structures for the MCP Documentation Server
================================================================

This module contains shared Pydantic models and data classes used across
the server, search tools, and other components.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Protocol, Callable
from pydantic import BaseModel, Field
from dataclasses import dataclass, field

try:
    from .document_cache import DocumentCache
except ImportError:
    # Fallback for direct execution
    from document_cache import DocumentCache

import os
import logging
import numpy as np

logger = logging.getLogger(__name__)

# Type aliases
PathLike = Union[str, Path]
DocumentDict = Dict[str, Union[str, int, List[str]]]


# Search-related data classes
@dataclass
class DocumentChunk:
    """
    Document chunk for search indexing
    
    Attributes:
        document_id: Parent document identifier
        chunk_index: Index of chunk within document
        chunk_id: Unique chunk identifier (document_id:chunk_index)
        content: Raw text content of chunk
        tokens: Tokenized text for BM25 indexing
        metadata: Additional chunk metadata
    """
    document_id: str
    chunk_index: int
    chunk_id: str
    content: str
    tokens: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class DocumentRequest(BaseModel):
    """Document request model with validation and type hints"""
    document_id: str = Field(
        ..., 
        description="Document identifier (relative path)",
        min_length=1,
        max_length=500
    )
    format: str = Field(
        default="markdown", 
        description="Output format for document content",
        pattern=r"^(markdown|plain|html)$"
    )

    class Config:
        """Pydantic configuration"""
        extra = "forbid"
        validate_assignment = True

class Document:
    """Document model for hybrid search system"""
    
    def __init__(self, id: str, name: str, path: str, size: int, content: str = "", 
                 created_at: Optional[datetime] = None, updated_at: Optional[datetime] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        self.id = id
        self.name = name
        self.path = path
        self.size = size
        self.content = content
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.metadata = metadata or {}

    def __str__(self) -> str:
        return f"Document(id={self.id}, name={self.name}, path={self.path}, size={self.size})"

    def __repr__(self) -> str:
        return self.__str__()
    
    @classmethod
    def from_file(cls, file_path: PathLike, document_id: Optional[str] = None) -> 'Document':
        """Create Document from file path"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Use provided document_id or derive from file path
        if document_id is None:
            document_id = str(file_path.relative_to(file_path.parent.parent)).replace("\\", "/")
        
        # Read file content
        try:
            content = file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            # Fallback for non-UTF8 files
            content = file_path.read_text(encoding='latin-1')
        
        # Get file stats
        stat = file_path.stat()
        created_at = datetime.fromtimestamp(stat.st_ctime)
        updated_at = datetime.fromtimestamp(stat.st_mtime)
        
        return cls(
            id=document_id,
            name=file_path.stem,
            path=str(file_path),
            size=stat.st_size,
            content=content,
            created_at=created_at,
            updated_at=updated_at,
            metadata={"file_extension": file_path.suffix}
        )

class SearchRequest(BaseModel):
    """Request model for search with advanced parameters"""
    query: str = Field(
        ..., 
        description="Search query string",
        min_length=1,
        max_length=1000
    )
    top_k: int = Field(
        default=10,
        description="Maximum number of results to return",
        ge=1,
        le=50
    )
    min_quality: int = Field(
        default=0,
        description="Quality cutoff 0-100 (0=return all, 100=exact matches only)",
        ge=0,
        le=100
    )
    include_scores: bool = Field(
        default=True,
        description="Include detailed scoring information"
    )

    class Config:
        """Pydantic configuration"""
        extra = "forbid"
        validate_assignment = True

@dataclass
class SearchResult:
    """
    Search result with score
    
    Attributes:
        document_id: Document identifier
        score: Relevance score (0.0 to 1.0)
    """
    document_id: str
    score: float

class SearchEngine(ABC):
    """Abstract base class for search engines"""
    
    def __init__(self, document_cache: DocumentCache):
        self._index_ready = False
        self.document_cache = document_cache
    
    @property
    def is_ready(self) -> bool:
        """Check if the search engine is ready"""
        return self._index_ready
        
    @abstractmethod
    def initialize(self, on_ready_fn: Optional[Callable[[bool], None]] = None) -> None:
        """Read documents into engine and build index"""
        pass
    
    @abstractmethod
    def _build_index(self) -> None:
        """Build the search index"""
        pass
        
    @abstractmethod
    def search(self, query: str, top_k: int = 10) -> List[SearchResult]:
        """Search for documents matching the query"""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get search engine statistics"""
        pass
    
    @abstractmethod
    def get_status(self) -> List[str]:
        """Get search engine status messages"""
        pass

    @classmethod
    @abstractmethod
    def get_name(cls) -> str:
        """Get search engine name"""
        pass
