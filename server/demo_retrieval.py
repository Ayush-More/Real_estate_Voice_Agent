"""Demo script to run the Phase 5 RAG Retrieval Pipeline."""

import os
import sys
from pathlib import Path
import logging
from dotenv import load_dotenv
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

# Load environment variables
load_dotenv()

# Ensure we can import from server/ directory
sys.path.insert(0, str(Path(__file__).parent))

from rag.retrieval import RetrievalPipeline

def main():
    """Run the retrieval demo."""
    logger = logging.getLogger("demo_retrieval")
    logger.info("Starting RAG Retrieval Pipeline (Phase 5)")
    
    pipeline = RetrievalPipeline()
    
    # Example 1: Basic Search
    query_1 = "What amenities does Sky Heights offer?"
    logger.info(f"\n--- Example 1: Basic Search ---")
    logger.info(f"Query: '{query_1}'")
    results_1 = pipeline.retrieve(query=query_1, top_k=2)
    
    for i, res in enumerate(results_1):
        logger.info(f"\nResult {i+1} (Score: {res['score']:.4f}):")
        logger.info(f"Metadata: {json.dumps(res['metadata'], indent=2)}")
        logger.info(f"Text Snippet: {res['text'][:150]}...")
        
    # Example 2: Search with Metadata Filter
    query_2 = "Tell me about the apartments."
    # For testing, we use a filter. Adjust depending on the dummy files indexed.
    filters = {"project_name": "Sky Heights Brochure"} 
    
    logger.info(f"\n--- Example 2: Metadata Filtering ---")
    logger.info(f"Query: '{query_2}'")
    logger.info(f"Filters: {filters}")
    
    results_2 = pipeline.retrieve(query=query_2, filters=filters, top_k=2)
    for i, res in enumerate(results_2):
        logger.info(f"\nResult {i+1} (Score: {res['score']:.4f}):")
        logger.info(f"Metadata: {json.dumps(res['metadata'], indent=2)}")
        logger.info(f"Text Snippet: {res['text'][:150]}...")
        
    logger.info("\nDemo completed.")

if __name__ == "__main__":
    main()
