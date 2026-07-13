"""Document storage manager for PDFs and other files.

This layer handles local file storage independent of Qdrant.
PDFs are stored in folders, with metadata managed in JSON files.
"""

import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from loguru import logger

from storage_layer.config import DocumentType, StorageConfig
from storage_layer.models import DocumentMetadata, StorageStats


class DocumentStorageManager:
    """Manages document storage operations.

    Handles saving, retrieving, and deleting documents from local storage.
    Metadata is stored in JSON files alongside documents.
    """

    def __init__(self) -> None:
        """Initialize storage manager and ensure directories exist."""
        StorageConfig.ensure_directories_exist()
        logger.info(f"Document storage initialized at {StorageConfig.STORAGE_BASE}")

    def save_document(
        self,
        file_path: str,
        doc_type: DocumentType,
        project_id: Optional[int] = None,
        description: Optional[str] = None,
    ) -> DocumentMetadata:
        """Save a document to storage.

        Args:
            file_path: Path to the file to save (can be uploaded file path)
            doc_type: Type of document (brochure, floorplan, faq)
            project_id: Optional associated project ID
            description: Optional description of the document

        Returns:
            DocumentMetadata with storage information

        Raises:
            FileNotFoundError: If source file doesn't exist
            ValueError: If file type not allowed or size exceeds limit
        """
        source_path = Path(file_path)

        # Validate source file
        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {file_path}")

        if source_path.suffix.lower() not in StorageConfig.ALLOWED_EXTENSIONS:
            raise ValueError(
                f"File type {source_path.suffix} not allowed. "
                f"Allowed: {StorageConfig.ALLOWED_EXTENSIONS}"
            )

        file_size = source_path.stat().st_size
        if file_size > StorageConfig.MAX_FILE_SIZE:
            raise ValueError(
                f"File size {file_size} bytes exceeds limit "
                f"({StorageConfig.MAX_FILE_SIZE} bytes)"
            )

        # Get destination path
        dest_dir = StorageConfig.get_storage_path(doc_type)
        dest_path = dest_dir / source_path.name

        # Ensure unique filename if duplicate exists
        counter = 1
        original_stem = dest_path.stem
        while dest_path.exists():
            dest_path = dest_dir / f"{original_stem}_{counter}{dest_path.suffix}"
            counter += 1

        # Copy file to storage
        import shutil
        shutil.copy2(source_path, dest_path)

        logger.info(f"Document saved: {dest_path}")

        # Create metadata
        metadata = DocumentMetadata(
            doc_id=dest_path.stem,
            doc_type=doc_type,
            filename=dest_path.name,
            filepath=str(dest_path),
            file_size=file_size,
            project_id=project_id,
            description=description,
            content_type=self._get_content_type(dest_path.suffix),
        )

        # Save metadata
        self._save_metadata(metadata)

        logger.info(f"Metadata saved for document: {metadata.doc_id}")
        return metadata

    def get_document(self, doc_id: str) -> Optional[DocumentMetadata]:
        """Retrieve document metadata by ID.

        Args:
            doc_id: Document identifier (filename without extension)

        Returns:
            DocumentMetadata if found, None otherwise
        """
        try:
            for doc_type in DocumentType:
                metadata = self._load_metadata_for_doc(doc_type, doc_id)
                if metadata:
                    return metadata
        except Exception as e:
            logger.error(f"Error retrieving document {doc_id}: {e}")

        return None

    def get_documents_by_type(self, doc_type: DocumentType) -> List[DocumentMetadata]:
        """Get all documents of a specific type.

        Args:
            doc_type: Type of documents to retrieve

        Returns:
            List of DocumentMetadata objects
        """
        documents: List[DocumentMetadata] = []
        storage_path = StorageConfig.get_storage_path(doc_type)

        try:
            for file_path in storage_path.glob("*"):
                if file_path.is_file() and file_path.suffix.lower() in StorageConfig.ALLOWED_EXTENSIONS:
                    metadata = self._load_metadata_for_doc(doc_type, file_path.stem)
                    if metadata:
                        documents.append(metadata)
        except Exception as e:
            logger.error(f"Error listing documents of type {doc_type}: {e}")

        return documents

    def get_documents_by_project(self, project_id: int) -> Dict[DocumentType, List[DocumentMetadata]]:
        """Get all documents associated with a project.

        Args:
            project_id: Project ID

        Returns:
            Dictionary mapping document types to lists of metadata
        """
        documents: Dict[DocumentType, List[DocumentMetadata]] = {}

        for doc_type in DocumentType:
            all_docs = self.get_documents_by_type(doc_type)
            project_docs = [d for d in all_docs if d.project_id == project_id]
            if project_docs:
                documents[doc_type] = project_docs

        return documents

    def delete_document(self, doc_id: str) -> bool:
        """Delete a document and its metadata.

        Args:
            doc_id: Document identifier

        Returns:
            True if deleted, False if not found
        """
        metadata = self.get_document(doc_id)
        if not metadata:
            logger.warning(f"Document not found for deletion: {doc_id}")
            return False

        try:
            # Delete file
            file_path = Path(metadata.filepath)
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Document file deleted: {file_path}")

            # Delete metadata
            self._delete_metadata(metadata)
            logger.info(f"Document deleted: {doc_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")
            return False

    def get_storage_stats(self) -> StorageStats:
        """Get storage usage statistics.

        Returns:
            StorageStats with usage information
        """
        total_size = 0
        total_docs = 0
        docs_by_type: Dict[str, int] = {}

        for doc_type in DocumentType:
            docs = self.get_documents_by_type(doc_type)
            docs_by_type[doc_type.value] = len(docs)
            total_docs += len(docs)
            total_size += sum(d.file_size for d in docs)

        return StorageStats(
            total_documents=total_docs,
            total_size_bytes=total_size,
            documents_by_type=docs_by_type,
            storage_path=str(StorageConfig.STORAGE_BASE),
        )

    # ============= Private Helper Methods =============

    @staticmethod
    def _get_content_type(extension: str) -> str:
        """Get MIME type for file extension."""
        extension = extension.lower()
        mime_types = {
            ".pdf": "application/pdf",
            ".txt": "text/plain",
        }
        return mime_types.get(extension, "application/octet-stream")

    def _save_metadata(self, metadata: DocumentMetadata) -> None:
        """Save document metadata to JSON file."""
        storage_path = StorageConfig.get_storage_path(metadata.doc_type)
        metadata_file = storage_path / StorageConfig.METADATA_FILE

        # Load existing metadata
        all_metadata: Dict[str, Dict[str, Any]] = {}
        if metadata_file.exists():
            try:
                with open(metadata_file, "r", encoding="utf-8") as f:
                    all_metadata = json.load(f)
            except Exception as e:
                logger.warning(f"Error loading existing metadata: {e}")

        # Update with new metadata
        all_metadata[metadata.doc_id] = json.loads(metadata.model_dump_json())

        # Save updated metadata
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(all_metadata, f, indent=2, default=str)

    def _load_metadata_for_doc(
        self, doc_type: DocumentType, doc_id: str
    ) -> Optional[DocumentMetadata]:
        """Load metadata for a specific document."""
        storage_path = StorageConfig.get_storage_path(doc_type)
        metadata_file = storage_path / StorageConfig.METADATA_FILE

        if not metadata_file.exists():
            return None

        try:
            with open(metadata_file, "r", encoding="utf-8") as f:
                all_metadata = json.load(f)

            if doc_id in all_metadata:
                data = all_metadata[doc_id]
                # Ensure doc_type is set correctly
                data["doc_type"] = doc_type.value
                return DocumentMetadata(**data)
        except Exception as e:
            logger.error(f"Error loading metadata for {doc_id}: {e}")

        return None

    def _delete_metadata(self, metadata: DocumentMetadata) -> None:
        """Delete metadata for a document."""
        storage_path = StorageConfig.get_storage_path(metadata.doc_type)
        metadata_file = storage_path / StorageConfig.METADATA_FILE

        if not metadata_file.exists():
            return

        try:
            with open(metadata_file, "r", encoding="utf-8") as f:
                all_metadata = json.load(f)

            if metadata.doc_id in all_metadata:
                del all_metadata[metadata.doc_id]

                with open(metadata_file, "w", encoding="utf-8") as f:
                    json.dump(all_metadata, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error deleting metadata for {metadata.doc_id}: {e}")


# Singleton instance
_storage_manager: Optional[DocumentStorageManager] = None


def get_storage_manager() -> DocumentStorageManager:
    """Get or create the document storage manager (singleton)."""
    global _storage_manager
    if _storage_manager is None:
        _storage_manager = DocumentStorageManager()
    return _storage_manager
