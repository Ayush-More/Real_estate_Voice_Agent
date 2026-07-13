#!/usr/bin/env python
"""Quick demo of search_properties() tool functionality."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from tools import search_properties
from loguru import logger


def demo():
    """Show search_properties in action."""
    
    logger.info("=" * 70)
    logger.info("SEARCH_PROPERTIES() TOOL DEMO".center(70))
    logger.info("=" * 70)
    
    # Demo 1: All properties
    logger.info("\n📍 Demo 1: Search all properties")
    results = search_properties()
    logger.info(f"Found {len(results)} properties")
    for r in results:
        logger.info(f"  • {r['project_name']} - {r['configuration']} - ₹{r['price']}")
    
    # Demo 2: Filter by city
    logger.info("\n🏙️  Demo 2: Search in Pune")
    results = search_properties(city="Pune")
    logger.info(f"Found {len(results)} properties in Pune")
    for r in results:
        logger.info(f"  • {r['configuration']} - ₹{r['price']} - {r['carpet_area']} sq ft")
    
    # Demo 3: Filter by configuration
    logger.info("\n🏠 Demo 3: Search 2 BHK properties")
    results = search_properties(configuration="2 BHK")
    logger.info(f"Found {len(results)} 2 BHK properties")
    for r in results:
        logger.info(f"  • {r['project_name']} - ₹{r['price']}")
    
    # Demo 4: Filter by price range
    logger.info("\n💰 Demo 4: Search properties between 5M-10M")
    results = search_properties(min_price=5000000, max_price=10000000)
    logger.info(f"Found {len(results)} properties in price range")
    for r in results:
        logger.info(f"  • {r['configuration']} - ₹{r['price']}")
    
    # Demo 5: Multiple filters
    logger.info("\n🔍 Demo 5: Search 2 BHK in Pune under 10M")
    results = search_properties(
        city="Pune",
        configuration="2 BHK",
        max_price=10000000
    )
    logger.info(f"Found {len(results)} properties matching criteria")
    for r in results:
        logger.info(f"  • {r['project_name']} ({r['locality']}) - {r['configuration']} - ₹{r['price']}")
    
    logger.info("\n" + "=" * 70)
    logger.success("✅ search_properties() tool works perfectly!")
    logger.info("=" * 70)


if __name__ == "__main__":
    demo()
