"""Pipeline for retrieving documents from Qdrant."""

import logging
from typing import List, Dict, Any

from rag.embeddings import get_embedding_service
from rag.qdrant_client import get_qdrant_service

logger = logging.getLogger(__name__)

class RetrievalPipeline:
    """Orchestrates the document retrieval process."""

    def __init__(self):
        self.embedding_service = get_embedding_service()
        self.qdrant_service = get_qdrant_service()

    def retrieve(self, query: str, filters: Dict[str, Any] = None, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve the most relevant text chunks for a given query.

        Args:
            query (str): The question or search term.
            filters (Dict[str, Any], optional): Metadata filters (e.g., {"project_name": "Sky Heights"}).
            top_k (int): Number of chunks to retrieve.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing 'text', 'score', and 'metadata'.
        """
        logger.info(f"Retrieving top {top_k} chunks for query: '{query}'")
        if filters:
            logger.info(f"Applying filters: {filters}")

        try:
            # 1. Generate query embedding
            query_vector = self.embedding_service.generate_embedding(query)

            # 2. Search Qdrant
            results = self.qdrant_service.search_chunks(
                query_vector=query_vector,
                top_k=top_k,
                filters=filters
            )

            logger.info(f"Retrieved {len(results)} chunks.")
            return results
        except Exception as e:
            logger.error(f"Failed to retrieve chunks: {e}")
            return []
