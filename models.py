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
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field

import logging

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
        document_id: Parent document identifier (string or integer key)
        chunk_index: Index of chunk within document
        content: Raw text content of chunk
        metadata: Additional chunk metadata (e.g., scores)
    """
    document_id: Union[str, int]
    chunk_index: int
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "document_id": self.document_id,
            "chunk_index": self.chunk_index,
            "content": self.content,
            "metadata": self.metadata,
        }

class Document:
    """Document model for search system"""
    
    def __init__(self, id: str, name: str, size: int, content: str = "", 
                 metadata: Optional[Dict[str, Any]] = None,
                 updated_at: Optional[datetime] = None):
        self.id = id
        self.name = name
        self.size = size
        self.content = content
        self.metadata = metadata or {}
        self.updated_at = updated_at

    def __str__(self) -> str:
        return f"Document(id={self.id}, name={self.name}, size={self.size})"

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
        updated_at = datetime.fromtimestamp(stat.st_mtime)
        
        return cls(
            id=document_id,
            name=file_path.stem,
            size=stat.st_size,
            content=content,
            updated_at=updated_at,
            metadata={"file_extension": file_path.suffix}
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "size": self.size,
            "content": self.content,
            "metadata": self.metadata,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
        }


class SearchEngine(ABC):
    """Abstract base class for search engines"""
   
    @property
    def is_ready(self) -> bool:
        """Check if the search engine is ready"""
        return getattr(self, "_is_ready", False)
        
    @abstractmethod
    def initialize(self, on_ready_fn: Optional[Callable[[bool], None]] = None) -> None:
        """Read documents into engine and build index"""
        pass
    
    @abstractmethod
    def search_for_chunks(self, query: str, top_k: int = 10) -> List[DocumentChunk]:
        """
        Search for chunks of documents matching the query
        """
        pass
    
    @abstractmethod
    def search_for_documents(self, query: str, top_k: int = 10) -> List['Document']:
        """
        Search for full documents matching the query
        """
        pass

    @abstractmethod
    def get_status(self) -> List[str]:
        """Get search engine status messages"""
        pass

    @classmethod
    def get_name(cls) -> str:
        """Get search engine name"""
        return cls.__name__
