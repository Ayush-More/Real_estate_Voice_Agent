"""Storage layer configuration."""

from pathlib import Path
from typing import Dict
from enum import Enum


class DocumentType(str, Enum):
    """Supported document types for storage organization."""

    BROCHURE = "brochures"
    FLOORPLAN = "floorplans"
    FAQ = "faqs"


class StorageConfig:
    """Configuration for document storage layer."""

    # Base storage directory
    STORAGE_BASE: Path = Path(__file__).parent.parent / "storage"

    # Subdirectories for different document types
    STORAGE_PATHS: Dict[DocumentType, Path] = {
        DocumentType.BROCHURE: STORAGE_BASE / "brochures",
        DocumentType.FLOORPLAN: STORAGE_BASE / "floorplans",
        DocumentType.FAQ: STORAGE_BASE / "faqs",
    }

    # File size limits (in bytes)
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50 MB

    # Allowed file extensions
    ALLOWED_EXTENSIONS: set = {".pdf", ".txt"}

    # Metadata storage filename
    METADATA_FILE: str = ".metadata.json"

    @classmethod
    def get_storage_path(cls, doc_type: DocumentType) -> Path:
        """Get storage path for document type."""
        path = cls.STORAGE_PATHS[doc_type]
        path.mkdir(parents=True, exist_ok=True)
        return path

    @classmethod
    def ensure_directories_exist(cls) -> None:
        """Create all storage directories if they don't exist."""
        for path in cls.STORAGE_PATHS.values():
            path.mkdir(parents=True, exist_ok=True)
