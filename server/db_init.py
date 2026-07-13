"""Database initialization and testing utility.

Usage:
    uv run db_init.py --init        # Create all tables
    uv run db_init.py --test        # Test database connection
    uv run db_init.py --seed        # Seed with sample data
"""

import os
import sys
from pathlib import Path

# Add server directory to path
sys.path.insert(0, str(Path(__file__).parent))

from loguru import logger
from db.session import get_db_instance
from db.repositories import ProjectRepository, UnitRepository
import argparse


def init_database() -> None:
    """Create all database tables."""
    logger.info("Initializing database schema...")
    try:
        db = get_db_instance()
        db.create_all_tables()
        logger.success("✓ Database tables created successfully")
    except Exception as e:
        logger.error(f"✗ Failed to initialize database: {e}")
        sys.exit(1)


def test_connection() -> None:
    """Test database connectivity."""
    logger.info("Testing database connection...")
    try:
        db = get_db_instance()
        session = db.get_session()

        # Simple query to test connection
        from db.models import Project

        result = session.query(Project).first()
        session.close()

        logger.success("✓ Database connection successful")
        logger.info(f"  Total projects in database: {session.query(Project).count()}")
    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")
        sys.exit(1)


def seed_sample_data() -> None:
    """Seed database with sample real estate data."""
    logger.info("Seeding sample data...")

    try:
        db = get_db_instance()
        session = db.get_session()

        project_repo = ProjectRepository(session)
        unit_repo = UnitRepository(session)

        # Check if data already exists
        from db.models import Project

        if session.query(Project).count() > 0:
            logger.warning("Sample data already exists, skipping seed")
            session.close()
            return

        # Sample project
        project = project_repo.create_project(
            project_name="Sky Heights Residency",
            city="Pune",
            locality="Wakad",
            status="Under Construction",
            rera_number=123456789,
            description="Luxury residential apartments with modern amenities",
            brochure_url="https://example.com/brochure.pdf",
            amenities={
                "features": [
                    "Swimming Pool",
                    "Clubhouse",
                    "Gym",
                    "24/7 Security",
                    "Parking",
                ],
                "nearbyMetro": True,
            },
        )
        logger.success(f"✓ Created project: {project.project_name} (ID: {project.id})")

        # Sample units
        configs = ["1 BHK", "2 BHK", "3 BHK"]
        prices = ["4500000", "8500000", "12000000"]
        carpet_areas = ["550", "720", "950"]

        for config, price, area in zip(configs, prices, carpet_areas):
            unit = unit_repo.create_unit(
                project_id=project.id,
                configuration=config,
                carpet_area=area,
                price=price,
                possession_date="December 2026",
            )
            logger.success(f"  ✓ Created unit: {config} - ₹{price}")

        session.close()
        logger.success("✓ Sample data seeded successfully")

    except Exception as e:
        logger.error(f"✗ Failed to seed data: {e}")
        sys.exit(1)


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Database initialization and management utility"
    )
    parser.add_argument(
        "--init", action="store_true", help="Create all database tables"
    )
    parser.add_argument(
        "--test", action="store_true", help="Test database connection"
    )
    parser.add_argument(
        "--seed", action="store_true", help="Seed with sample data"
    )

    args = parser.parse_args()

    if not any([args.init, args.test, args.seed]):
        parser.print_help()
        sys.exit(0)

    if args.init:
        init_database()

    if args.test:
        test_connection()

    if args.seed:
        seed_sample_data()


if __name__ == "__main__":
    main()
