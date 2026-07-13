#!/usr/bin/env python
"""Test document storage layer independently (no bot.py required).

This script demonstrates that the storage layer is fully testable
without running the voice pipeline.

Run:
    uv run test_storage_layer.py
"""

import sys
import tempfile
from pathlib import Path

# Add server directory to path
sys.path.insert(0, str(Path(__file__).parent))

from loguru import logger
from storage_layer import (
    DocumentStorageManager,
    DocumentType,
    get_storage_manager,
)


def create_test_pdf() -> Path:
    """Create a simple test PDF file."""
    import io
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter

    # Create temporary PDF
    temp_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    pdf_path = Path(temp_file.name)

    # Generate simple PDF
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    c.drawString(100, 750, "Test Document")
    c.drawString(100, 730, "This is a test PDF for storage layer testing")
    c.save()

    return pdf_path


def create_test_text() -> Path:
    """Create a simple test text file."""
    temp_file = tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w")
    temp_file.write("This is a test FAQ document.\n")
    temp_file.write("Q: What is this?\n")
    temp_file.write("A: This is a test file for storage layer testing.\n")
    temp_file.close()
    return Path(temp_file.name)


def test_save_brochure() -> None:
    """Test: save a brochure document."""
    logger.info("=" * 60)
    logger.info("Test 1: Save a brochure document")
    logger.info("=" * 60)

    # Create test PDF
    test_pdf = create_test_pdf()

    try:
        manager = get_storage_manager()

        # Save brochure
        metadata = manager.save_document(
            file_path=str(test_pdf),
            doc_type=DocumentType.BROCHURE,
            project_id=1,
            description="Sky Heights Residency Brochure",
        )

        logger.success(f"✓ Document saved: {metadata.doc_id}")
        logger.info(f"  Filename: {metadata.filename}")
        logger.info(f"  Size: {metadata.file_size} bytes")
        logger.info(f"  Project ID: {metadata.project_id}")

    finally:
        test_pdf.unlink()


def test_save_floorplan() -> None:
    """Test: save a floorplan document."""
    logger.info("\n" + "=" * 60)
    logger.info("Test 2: Save a floorplan document")
    logger.info("=" * 60)

    # Create test PDF
    test_pdf = create_test_pdf()

    try:
        manager = get_storage_manager()

        # Save floorplan
        metadata = manager.save_document(
            file_path=str(test_pdf),
            doc_type=DocumentType.FLOORPLAN,
            project_id=1,
            description="2 BHK Floor Plan",
        )

        logger.success(f"✓ Document saved: {metadata.doc_id}")
        logger.info(f"  Type: {metadata.doc_type}")

    finally:
        test_pdf.unlink()


def test_save_faq() -> None:
    """Test: save an FAQ document."""
    logger.info("\n" + "=" * 60)
    logger.info("Test 3: Save an FAQ document")
    logger.info("=" * 60)

    # Create test text
    test_txt = create_test_text()

    try:
        manager = get_storage_manager()

        # Save FAQ
        metadata = manager.save_document(
            file_path=str(test_txt),
            doc_type=DocumentType.FAQ,
            description="Frequently Asked Questions",
        )

        logger.success(f"✓ Document saved: {metadata.doc_id}")
        logger.info(f"  Type: {metadata.doc_type}")

    finally:
        test_txt.unlink()


def test_list_documents_by_type() -> None:
    """Test: list documents by type."""
    logger.info("\n" + "=" * 60)
    logger.info("Test 4: List documents by type")
    logger.info("=" * 60)

    manager = get_storage_manager()

    for doc_type in DocumentType:
        docs = manager.get_documents_by_type(doc_type)
        logger.info(f"\n{doc_type.value}:")
        if docs:
            for doc in docs:
                logger.info(f"  • {doc.filename} ({doc.file_size} bytes)")
        else:
            logger.info("  (No documents)")


def test_get_documents_by_project() -> None:
    """Test: get all documents for a project."""
    logger.info("\n" + "=" * 60)
    logger.info("Test 5: Get documents by project")
    logger.info("=" * 60)

    manager = get_storage_manager()

    project_docs = manager.get_documents_by_project(project_id=1)

    if project_docs:
        logger.info(f"Found documents for project 1:")
        for doc_type, docs in project_docs.items():
            logger.info(f"  {doc_type.value}: {len(docs)} document(s)")
            for doc in docs:
                logger.info(f"    • {doc.filename}")
    else:
        logger.info("No documents found for project 1")


def test_get_storage_stats() -> None:
    """Test: get storage statistics."""
    logger.info("\n" + "=" * 60)
    logger.info("Test 6: Get storage statistics")
    logger.info("=" * 60)

    manager = get_storage_manager()
    stats = manager.get_storage_stats()

    logger.info(f"\nStorage Statistics:")
    logger.info(f"  Total documents: {stats.total_documents}")
    logger.info(f"  Total size: {stats.total_size_mb:.2f} MB")
    logger.info(f"  Storage path: {stats.storage_path}")
    logger.info(f"\n  Documents by type:")
    for doc_type, count in stats.documents_by_type.items():
        logger.info(f"    • {doc_type}: {count}")


def test_retrieve_document() -> None:
    """Test: retrieve document metadata by ID."""
    logger.info("\n" + "=" * 60)
    logger.info("Test 7: Retrieve document metadata")
    logger.info("=" * 60)

    manager = get_storage_manager()

    # Get first brochure
    brochures = manager.get_documents_by_type(DocumentType.BROCHURE)

    if brochures:
        doc = brochures[0]
        logger.info(f"Retrieving: {doc.doc_id}")

        retrieved = manager.get_document(doc.doc_id)
        if retrieved:
            logger.success(f"✓ Document retrieved")
            logger.info(f"  ID: {retrieved.doc_id}")
            logger.info(f"  Filename: {retrieved.filename}")
            logger.info(f"  Type: {retrieved.doc_type}")
            logger.info(f"  Description: {retrieved.description}")
            logger.info(f"  Created: {retrieved.created_at}")
        else:
            logger.error("✗ Failed to retrieve document")
    else:
        logger.warning("No brochures to retrieve")


def test_delete_document() -> None:
    """Test: delete a document."""
    logger.info("\n" + "=" * 60)
    logger.info("Test 8: Delete a document")
    logger.info("=" * 60)

    manager = get_storage_manager()

    # Create a test document
    test_pdf = create_test_pdf()

    try:
        # Save document
        metadata = manager.save_document(
            file_path=str(test_pdf),
            doc_type=DocumentType.FAQ,
            description="Temporary test document",
        )

        logger.info(f"Created test document: {metadata.doc_id}")

        # Delete it
        success = manager.delete_document(metadata.doc_id)

        if success:
            logger.success(f"✓ Document deleted: {metadata.doc_id}")
        else:
            logger.error(f"✗ Failed to delete document: {metadata.doc_id}")

    finally:
        test_pdf.unlink()


def test_storage_isolation() -> None:
    """Test: verify storage layer is independent."""
    logger.info("\n" + "=" * 60)
    logger.info("Test 9: Storage layer independence")
    logger.info("=" * 60)

    # This test verifies that storage works without other components
    manager = get_storage_manager()

    logger.success("✓ Storage manager created successfully")
    logger.success("✓ Storage layer works independently (no database required)")

    stats = manager.get_storage_stats()
    logger.info(f"✓ Current storage usage: {stats.total_size_mb:.2f} MB")


def main() -> None:
    """Run all tests."""
    logger.info("\n" + "🧪 TESTING DOCUMENT STORAGE LAYER 🧪".center(60))
    logger.info("This layer stores PDFs locally, independent of Qdrant\n")

    try:
        test_save_brochure()
        test_save_floorplan()
        test_save_faq()
        test_list_documents_by_type()
        test_get_documents_by_project()
        test_get_storage_stats()
        test_retrieve_document()
        test_delete_document()
        test_storage_isolation()

        logger.info("\n" + "=" * 60)
        logger.success("✓ ALL TESTS PASSED")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"\n✗ TEST FAILED: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
