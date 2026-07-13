"""Pipeline for indexing documents into Qdrant."""

import os
import logging
from typing import Dict, Any, List
from pathlib import Path
from pypdf import PdfReader

from rag.chunking import chunk_text
from rag.embeddings import get_embedding_service
from rag.qdrant_client import get_qdrant_service

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file."""
    try:
        reader = PdfReader(file_path)
        text = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
        return "\n\n".join(text)
    except Exception as e:
        logger.error(f"Failed to extract text from {file_path}: {e}")
        return ""

class IndexingPipeline:
    """Orchestrates the document indexing process."""
    
    def __init__(self):
        self.qdrant_service = get_qdrant_service()
        self.embedding_service = get_embedding_service()
        
    def process_file(self, file_path: Path, project_id: str, project_name: str, document_type: str):
        """Process a single file and index it if it hasn't been indexed yet."""
        filename = file_path.name
        
        # 1. Check for incremental updates
        if self.qdrant_service.is_file_indexed(filename):
            logger.info(f"Skipping already indexed file: {filename}")
            return
            
        logger.info(f"Processing new file: {filename} (Type: {document_type})")
        
        # 2. Extract text
        if file_path.suffix.lower() == ".pdf":
            text = extract_text_from_pdf(str(file_path))
        else:
            # Fallback for simple text files if needed
            try:
                text = file_path.read_text(encoding="utf-8")
            except Exception as e:
                logger.error(f"Unsupported file type or failed to read {filename}: {e}")
                return
                
        if not text.strip():
            logger.warning(f"No text extracted from {filename}")
            return
            
        # 3. Create metadata
        metadata = {
            "project_id": project_id,
            "project_name": project_name,
            "document_type": document_type,
            "filename": filename
        }
        
        # 4. Chunk text
        chunks = chunk_text(text, metadata)
        if not chunks:
            logger.warning(f"No chunks created for {filename}")
            return
            
        # 5. Generate embeddings
        texts = [c["text"] for c in chunks]
        embeddings = self.embedding_service.generate_embeddings(texts)
        
        # 6. Store in Qdrant
        self.qdrant_service.insert_chunks(chunks, embeddings)
        logger.info(f"Successfully indexed {filename}")

    def run_pipeline(self, storage_dir: str = "storage"):
        """Run the indexing pipeline for all documents in the storage directory."""
        storage_path = Path(storage_dir)
        if not storage_path.exists():
            logger.warning(f"Storage directory {storage_dir} does not exist.")
            return

        # Expected structure: storage/{document_type}
        # In a real scenario, we might have metadata files or deduce project info from DB.
        # For this pipeline, we will deduce project_name from the filename or mock it.
        # Example: project_id="1", project_name="Sky Heights" based on filename or just dummy data
        
        document_types = ["brochures", "floorplans", "faqs"]
        
        for doc_type in document_types:
            type_dir = storage_path / doc_type
            if not type_dir.exists():
                continue
                
            for file_path in type_dir.glob("*"):
                if file_path.is_file():
                    # For phase 4 demonstration, we'll assign a dummy project_id/name if we can't infer it.
                    # Usually, the API uploading the file would pass this, or we parse from name.
                    # e.g. "sky_heights_brochure.pdf" -> Sky Heights
                    filename_stem = file_path.stem.replace("_", " ").title()
                    
                    self.process_file(
                        file_path=file_path,
                        project_id="unknown_id",
                        project_name=filename_stem,
                        document_type=doc_type
                    )
