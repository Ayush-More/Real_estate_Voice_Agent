"""Document storage layer for Real Estate Voice Agent.

This module provides local file storage for documents (PDFs, text files, etc.)
independent of Qdrant vector database.

Documents are organized by type (brochures, floorplans, faqs) and metadata
is stored in JSON files.
"""

from storage_layer.config import DocumentType, StorageConfig
from storage_layer.models import DocumentMetadata, StorageStats
from storage_layer.manager import DocumentStorageManager, get_storage_manager

__all__ = [
    "DocumentType",
    "StorageConfig",
    "DocumentMetadata",
    "StorageStats",
    "DocumentStorageManager",
    "get_storage_manager",
]
