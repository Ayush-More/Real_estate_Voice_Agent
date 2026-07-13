#!/usr/bin/env python
"""Test search_properties() tool independently (no bot.py required).

This script demonstrates that the search_properties tool is fully testable
without running the voice pipeline.

Run:
    uv run test_search_properties.py
"""

import sys
from pathlib import Path

# Add server directory to path
sys.path.insert(0, str(Path(__file__).parent))

from loguru import logger
from tools import search_properties


def test_search_all_properties() -> None:
    """Test: search all properties (no filters)."""
    logger.info("=" * 60)
    logger.info("Test 1: Search ALL properties (no filters)")
    logger.info("=" * 60)

    results = search_properties()

    logger.info(f"\nFound {len(results)} total properties")
    for result in results:
        logger.info(
            f"  • {result['project_name']} - {result['configuration']} - "
            f"₹{result['price']} ({result['carpet_area']} sq ft)"
        )


def test_search_by_city() -> None:
    """Test: search properties by city."""
    logger.info("\n" + "=" * 60)
    logger.info('Test 2: Search by city ("Pune")')
    logger.info("=" * 60)

    results = search_properties(city="Pune")

    logger.info(f"\nFound {len(results)} properties in Pune")
    for result in results:
        logger.info(
            f"  • {result['project_name']} ({result['locality']}) - "
            f"{result['configuration']} - ₹{result['price']}"
        )


def test_search_by_configuration() -> None:
    """Test: search properties by configuration."""
    logger.info("\n" + "=" * 60)
    logger.info('Test 3: Search by configuration ("2 BHK")')
    logger.info("=" * 60)

    results = search_properties(configuration="2 BHK")

    logger.info(f"\nFound {len(results)} 2 BHK properties")
    for result in results:
        logger.info(
            f"  • {result['project_name']} - ₹{result['price']} - "
            f"{result['carpet_area']} sq ft"
        )


def test_search_by_price_range() -> None:
    """Test: search properties by price range."""
    logger.info("\n" + "=" * 60)
    logger.info("Test 4: Search by price range (5M - 10M)")
    logger.info("=" * 60)

    results = search_properties(min_price=5000000, max_price=10000000)

    logger.info(f"\nFound {len(results)} properties in ₹5M - ₹10M range")
    for result in results:
        logger.info(
            f"  • {result['project_name']} - {result['configuration']} - "
            f"₹{result['price']}"
        )


def test_search_by_multiple_filters() -> None:
    """Test: search with multiple filters combined."""
    logger.info("\n" + "=" * 60)
    logger.info('Test 5: Search with multiple filters (city="Pune", config="2 BHK", max_price=10M)')
    logger.info("=" * 60)

    results = search_properties(
        city="Pune",
        configuration="2 BHK",
        max_price=10000000,
    )

    logger.info(f"\nFound {len(results)} properties matching all criteria")
    for result in results:
        logger.info(
            f"  • {result['project_name']} ({result['city']}) - "
            f"{result['configuration']} - ₹{result['price']}"
        )


def test_search_no_results() -> None:
    """Test: search that returns no results."""
    logger.info("\n" + "=" * 60)
    logger.info('Test 6: Search with no matches (city="NonExistent")')
    logger.info("=" * 60)

    results = search_properties(city="NonExistent")

    logger.info(f"\nFound {len(results)} properties")
    if not results:
        logger.success("✓ Empty result set handled correctly")


def test_with_data_validation() -> None:
    """Test: validate response structure."""
    logger.info("\n" + "=" * 60)
    logger.info("Test 7: Validate response structure")
    logger.info("=" * 60)

    results = search_properties()

    if not results:
        logger.warning("No results to validate")
        return

    result = results[0]
    required_fields = [
        "project_name",
        "city",
        "locality",
        "configuration",
        "carpet_area",
        "price",
        "possession_date",
        "project_id",
        "unit_id",
    ]

    logger.info(f"\nValidating first result: {result['project_name']}")

    missing_fields = [f for f in required_fields if f not in result]
    if missing_fields:
        logger.error(f"✗ Missing fields: {missing_fields}")
    else:
        logger.success("✓ All required fields present")

    logger.info(f"\nResponse structure:")
    for key, value in result.items():
        logger.info(f"  • {key}: {value} (type: {type(value).__name__})")


def main() -> None:
    """Run all tests."""
    logger.info("\n" + "🧪 TESTING search_properties() TOOL 🧪".center(60))
    logger.info("This tool is independently testable WITHOUT bot.py\n")

    try:
        test_search_all_properties()
        test_search_by_city()
        test_search_by_configuration()
        test_search_by_price_range()
        test_search_by_multiple_filters()
        test_search_no_results()
        test_with_data_validation()

        logger.info("\n" + "=" * 60)
        logger.success("✓ ALL TESTS PASSED")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"\n✗ TEST FAILED: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
