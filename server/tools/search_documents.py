"""Search documents tool for Real Estate Voice Agent.

This tool provides semantic search across indexed marketing documents (brochures, floorplans, FAQs)
using the RAG retrieval pipeline and Qdrant vector database.
"""

from typing import List, Dict, Any, Optional
from loguru import logger

from rag.retrieval import RetrievalPipeline


def search_documents(
    query: str,
    project_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Search marketing documents using semantic matching.

    Args:
        query: The question or search term (e.g. "Does it have a clubhouse?").
        project_id: Optional project_id to filter the documents by a specific project.

    Returns:
        List of chunks with structure:
        [
            {
                "score": float,
                "text": str,
                "metadata": dict
            },
            ...
        ]
        
    Example:
        >>> results = search_documents(query="Is there a gym?", project_id="123")
    """
    try:
        logger.info(f"Searching documents for query: '{query}' (project_id={project_id})")
        
        # Build filters
        filters = {}
        if project_id:
            filters["project_id"] = project_id
            
        pipeline = RetrievalPipeline()
        results = pipeline.retrieve(query=query, filters=filters, top_k=3)
        
        logger.info(f"Document search completed: returned {len(results)} chunks")
        return results
        
    except Exception as e:
        logger.error(f"Document search failed: {e}", exc_info=True)
        return []
