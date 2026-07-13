"""Embedding generation for RAG pipeline."""

import logging
from typing import List
from sentence_transformers import SentenceTransformer
from config.rag import get_rag_settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service to generate embeddings using sentence-transformers."""

    def __init__(self):
        settings = get_rag_settings()
        self.model_name = settings.embedding_model
        logger.info(f"Loading embedding model: {self.model_name}")
        # Load the model on initialization
        self.model = SentenceTransformer(self.model_name)
        logger.info(f"Successfully loaded embedding model: {self.model_name}")

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        if not texts:
            return []
        
        # sentence-transformers encode returns a numpy array or tensor, we convert to list of floats
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text string."""
        return self.generate_embeddings([text])[0]

# Singleton instance
_embedding_service = None

def get_embedding_service() -> EmbeddingService:
    """Get or create the embedding service singleton."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
