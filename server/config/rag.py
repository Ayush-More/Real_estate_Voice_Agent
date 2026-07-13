"""Configuration for the RAG pipeline."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class RAGSettings(BaseSettings):
    """RAG-specific configuration settings."""

    # Qdrant settings
    qdrant_url: str = ":memory:"
    qdrant_api_key: str | None = None
    collection_name: str = "real_estate_docs"

    # Embedding and chunking settings
    embedding_model: str = "all-MiniLM-L6-v2"
    chunk_size: int = 1000
    chunk_overlap: int = 200

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_rag_settings() -> RAGSettings:
    """Get cached RAG settings instance."""
    return RAGSettings()
