"""Demo script to run the Phase 4 RAG Indexing Pipeline."""

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

from rag.indexing import IndexingPipeline
from rag.qdrant_client import get_qdrant_service

def main():
    """Run the indexing demo."""
    logger = logging.getLogger("demo_indexing")
    logger.info("Starting RAG Indexing Pipeline (Phase 4)")
    
    # Optional: Create a dummy PDF in storage/brochures for testing if it doesn't exist
    storage_dir = Path("storage")
    brochures_dir = storage_dir / "brochures"
    brochures_dir.mkdir(parents=True, exist_ok=True)
    
    dummy_pdf_path = brochures_dir / "sky_heights_brochure.pdf"
    if not dummy_pdf_path.exists():
        logger.info(f"Creating dummy PDF at {dummy_pdf_path}")
        try:
            from reportlab.pdfgen import canvas
            c = canvas.Canvas(str(dummy_pdf_path))
            c.drawString(100, 750, "Sky Heights Project Brochure")
            c.drawString(100, 730, "Located in Pune. Offers 2 BHK and 3 BHK apartments.")
            c.drawString(100, 710, "Amenities include swimming pool, gym, and clubhouse.")
            c.save()
        except ImportError:
            logger.warning("reportlab not installed. Creating a dummy text file instead.")
            with open(dummy_pdf_path.with_suffix(".txt"), "w") as f:
                f.write("Sky Heights Project Brochure\nLocated in Pune. Offers 2 BHK and 3 BHK apartments.")
                
    # Initialize and run pipeline
    pipeline = IndexingPipeline()
    
    logger.info("--- First Run (Should index new documents) ---")
    pipeline.run_pipeline("storage")
    
    logger.info("--- Second Run (Should skip already indexed documents) ---")
    pipeline.run_pipeline("storage")
    
    # Verify in Qdrant
    qdrant = get_qdrant_service()
    try:
        count = qdrant.client.count(collection_name=qdrant.collection_name).count
        logger.info(f"Total points in Qdrant collection '{qdrant.collection_name}': {count}")
    except Exception as e:
        logger.error(f"Failed to query Qdrant count: {e}")
        
    logger.info("Demo completed.")

if __name__ == "__main__":
    main()
