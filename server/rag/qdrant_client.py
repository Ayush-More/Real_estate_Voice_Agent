"""Qdrant client and vector database operations."""

import logging
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from config.rag import get_rag_settings

logger = logging.getLogger(__name__)

class QdrantService:
    """Service to interact with Qdrant vector database."""
    
    def __init__(self):
        self.settings = get_rag_settings()
        
        # Initialize client
        if self.settings.qdrant_url == ":memory:":
            self.client = QdrantClient(location=":memory:")
            logger.info("Initialized Qdrant in-memory client.")
        else:
            self.client = QdrantClient(
                url=self.settings.qdrant_url,
                api_key=self.settings.qdrant_api_key
            )
            logger.info(f"Initialized Qdrant client at {self.settings.qdrant_url}")
            
        self.collection_name = self.settings.collection_name
        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        """Create the collection if it doesn't exist."""
        try:
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.collection_name not in collection_names:
                # Based on sentence-transformers all-MiniLM-L6-v2, dimension is 384
                # We can make this dynamic if needed, but hardcoding for now
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=qmodels.VectorParams(
                        size=384,
                        distance=qmodels.Distance.COSINE
                    )
                )
                logger.info(f"Created Qdrant collection: {self.collection_name}")
            else:
                logger.info(f"Qdrant collection {self.collection_name} already exists.")
                
            # Ensure payload index exists for project_name to allow filtering
            try:
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="project_name",
                    field_schema=qmodels.PayloadSchemaType.KEYWORD
                )
            except Exception as e:
                # Might already exist
                logger.debug(f"Payload index creation note (might already exist): {e}")
        except Exception as e:
            logger.error(f"Error ensuring collection exists: {e}")
            raise

    def is_file_indexed(self, filename: str) -> bool:
        """Check if a file has already been indexed."""
        # Check if we can find any point with this filename
        # We use a filter on the payload (metadata)
        try:
            response = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=qmodels.Filter(
                    must=[
                        qmodels.FieldCondition(
                            key="filename",
                            match=qmodels.MatchValue(value=filename)
                        )
                    ]
                ),
                limit=1,
                with_payload=False,
                with_vectors=False
            )
            points, _ = response
            return len(points) > 0
        except Exception as e:
            logger.error(f"Error checking if file {filename} is indexed: {e}")
            return False

    def insert_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]):
        """Insert text chunks and their embeddings into Qdrant."""
        if not chunks or not embeddings:
            return
            
        if len(chunks) != len(embeddings):
            raise ValueError(f"Number of chunks ({len(chunks)}) and embeddings ({len(embeddings)}) must match.")

        points = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            import uuid
            # Generate a deterministic ID or random UUID
            # For simplicity, using a random UUID
            point_id = str(uuid.uuid4())
            
            payload = chunk["metadata"].copy()
            payload["text"] = chunk["text"]
            
            points.append(
                qmodels.PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload
                )
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        logger.info(f"Successfully inserted {len(points)} chunks into {self.collection_name}.")

    def search_chunks(self, query_vector: List[float], top_k: int = 3, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Search for the most relevant text chunks."""
        query_filter = None
        if filters:
            must_conditions = []
            for key, value in filters.items():
                must_conditions.append(
                    qmodels.FieldCondition(
                        key=key,
                        match=qmodels.MatchValue(value=value)
                    )
                )
            if must_conditions:
                query_filter = qmodels.Filter(must=must_conditions)

        try:
            search_result = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                query_filter=query_filter,
                limit=top_k,
                with_payload=True
            ).points
            
            # Format results
            results = []
            for point in search_result:
                if point.payload:
                    results.append({
                        "score": point.score,
                        "text": point.payload.get("text", ""),
                        "metadata": {k: v for k, v in point.payload.items() if k != "text"}
                    })
            return results
        except Exception as e:
            logger.error(f"Error during Qdrant search: {e}")
            return []
# Singleton instance
_qdrant_service = None

def get_qdrant_service() -> QdrantService:
    """Get or create the Qdrant service singleton."""
    global _qdrant_service
    if _qdrant_service is None:
        _qdrant_service = QdrantService()
    return _qdrant_service
