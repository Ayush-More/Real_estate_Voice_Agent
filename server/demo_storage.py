#!/usr/bin/env python
"""Demo of document storage layer functionality."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from loguru import logger
from storage_layer import get_storage_manager, DocumentType


def demo():
    """Show document storage in action."""

    logger.info("=" * 70)
    logger.info("DOCUMENT STORAGE LAYER DEMO".center(70))
    logger.info("=" * 70)

    manager = get_storage_manager()

    # Demo 1: Storage structure
    logger.info("\n📁 Demo 1: Storage directory structure")
    logger.info(f"Storage location: {manager.get_storage_stats().storage_path}")
    logger.info(f"Supported types: {', '.join(dt.value for dt in DocumentType)}")

    # Demo 2: Current documents
    logger.info("\n📚 Demo 2: Current documents in storage")
    stats = manager.get_storage_stats()
    logger.info(f"Total documents: {stats.total_documents}")
    logger.info(f"Total size: {stats.total_size_mb:.2f} MB")

    for doc_type in DocumentType:
        docs = manager.get_documents_by_type(doc_type)
        logger.info(f"\n{doc_type.value}:")
        if docs:
            for doc in docs:
                logger.info(f"  • {doc.filename} ({doc.file_size} bytes)")
                if doc.description:
                    logger.info(f"    Description: {doc.description}")
                if doc.project_id:
                    logger.info(f"    Project ID: {doc.project_id}")
        else:
            logger.info("  (No documents)")

    # Demo 3: Project organization
    logger.info("\n🏢 Demo 3: Documents by project")
    project_docs = manager.get_documents_by_project(project_id=1)
    if project_docs:
        logger.info("Project 1 documents:")
        for doc_type, docs in project_docs.items():
            logger.info(f"  {doc_type.value}: {len(docs)} document(s)")
    else:
        logger.info("No documents for project 1 yet")

    logger.info("\n" + "=" * 70)
    logger.success("✅ Document storage layer is working!")
    logger.info("=" * 70)


if __name__ == "__main__":
    demo()
