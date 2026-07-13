"""Text chunking for RAG pipeline using LangChain."""

import logging
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config.rag import get_rag_settings

logger = logging.getLogger(__name__)

def chunk_text(text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Split text into chunks and attach metadata to each chunk.
    
    Args:
        text (str): The raw text to split.
        metadata (Dict[str, Any]): Base metadata to include in all chunks (e.g. project_id, filename).
        
    Returns:
        List[Dict[str, Any]]: A list of chunks, each represented as a dict with 'text' and 'metadata'.
    """
    settings = get_rag_settings()
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        length_function=len,
        is_separator_regex=False,
    )
    
    # Split text into strings
    chunks = splitter.split_text(text)
    
    result = []
    for i, chunk in enumerate(chunks):
        # Create a new metadata dict for each chunk and add the chunk number
        chunk_meta = metadata.copy()
        chunk_meta["chunk_number"] = i
        
        result.append({
            "text": chunk,
            "metadata": chunk_meta
        })
        
    logger.debug(f"Split text into {len(result)} chunks.")
    return result
