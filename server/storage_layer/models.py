"""Document metadata models for storage layer."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from storage_layer.config import DocumentType


class DocumentMetadata(BaseModel):
    """Metadata for a stored document."""

    doc_id: str = Field(
        description="Unique document identifier (filename without extension)"
    )
    doc_type: DocumentType = Field(description="Type of document (brochure, floorplan, faq)")
    filename: str = Field(description="Original filename with extension")
    filepath: str = Field(description="Full path to the document in storage")
    file_size: int = Field(description="File size in bytes")
    created_at: datetime = Field(default_factory=datetime.now, description="Upload timestamp")
    project_id: Optional[int] = Field(None, description="Associated project ID (optional)")
    content_type: str = Field(
        default="application/pdf", description="MIME type of the document"
    )
    description: Optional[str] = Field(
        None, description="Human-readable description of the document"
    )

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class StorageStats(BaseModel):
    """Statistics about storage usage."""

    total_documents: int = Field(description="Total number of documents stored")
    total_size_bytes: int = Field(description="Total storage used in bytes")
    documents_by_type: dict = Field(description="Count of documents by type")
    storage_path: str = Field(description="Base storage directory path")

    @property
    def total_size_mb(self) -> float:
        """Total storage size in megabytes."""
        return self.total_size_bytes / (1024 * 1024)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
