"""Demo script to test search_documents tool from Phase 6."""

import os
import sys
from pathlib import Path
import logging
from dotenv import load_dotenv

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

from tools import search_documents

def main():
    """Run the tools demo."""
    logger = logging.getLogger("demo_tools")
    logger.info("Starting Search Documents Tool Test (Phase 6)")
    
    query = "Does it have a clubhouse?"
    logger.info(f"\nSearching for: '{query}'")
    
    results = search_documents(query=query)
    
    for i, res in enumerate(results):
        logger.info(f"\nResult {i+1} (Score: {res['score']:.4f}):")
        logger.info(f"Project Name: {res['metadata'].get('project_name')}")
        logger.info(f"Text Snippet: {res['text'][:150]}...")
        
    logger.info("\nDemo completed.")

if __name__ == "__main__":
    main()
