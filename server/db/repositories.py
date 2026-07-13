"""Repository layer for database operations."""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, select
from loguru import logger

from db.models import Project, Unit, ProjectSchema, UnitSchema


class ProjectRepository:
    """Repository for Project model operations."""

    def __init__(self, session: Session) -> None:
        """Initialize with database session."""
        self.session = session

    def create_project(
        self,
        project_name: str,
        city: str,
        locality: Optional[str] = None,
        status: Optional[str] = None,
        rera_number: Optional[int] = None,
        description: Optional[str] = None,
        brochure_url: Optional[str] = None,
        amenities: Optional[Dict[str, Any]] = None,
    ) -> Project:
        """Create a new project."""
        project = Project(
            project_name=project_name,
            city=city,
            locality=locality,
            status=status,
            rera_number=rera_number,
            description=description,
            brochure_url=brochure_url,
            amenities=amenities,
        )
        self.session.add(project)
        self.session.commit()
        self.session.refresh(project)
        logger.info(f"Project created: {project.id} - {project_name}")
        return project

    def get_project_by_id(self, project_id: int) -> Optional[Project]:
        """Retrieve a project by ID."""
        return self.session.query(Project).filter(Project.id == project_id).first()

    def get_all_projects(self, skip: int = 0, limit: int = 100) -> List[Project]:
        """Retrieve all projects with pagination."""
        return (
            self.session.query(Project)
            .order_by(Project.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search_projects(
        self,
        city: Optional[str] = None,
        locality: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Project]:
        """Search projects by filters."""
        query = self.session.query(Project)

        filters = []
        if city:
            filters.append(Project.city.ilike(f"%{city}%"))
        if locality:
            filters.append(Project.locality.ilike(f"%{locality}%"))
        if status:
            filters.append(Project.status.ilike(f"%{status}%"))

        if filters:
            query = query.filter(and_(*filters))

        return query.order_by(Project.created_at.desc()).all()

    def update_project(
        self, project_id: int, **kwargs: Any
    ) -> Optional[Project]:
        """Update a project by ID."""
        project = self.get_project_by_id(project_id)
        if not project:
            logger.warning(f"Project not found: {project_id}")
            return None

        # Only update allowed fields
        allowed_fields = {
            "project_name",
            "city",
            "locality",
            "status",
            "rera_number",
            "description",
            "brochure_url",
            "amenities",
        }

        for key, value in kwargs.items():
            if key in allowed_fields:
                setattr(project, key, value)

        self.session.commit()
        self.session.refresh(project)
        logger.info(f"Project updated: {project_id}")
        return project

    def delete_project(self, project_id: int) -> bool:
        """Delete a project by ID (cascades to units)."""
        project = self.get_project_by_id(project_id)
        if not project:
            logger.warning(f"Project not found: {project_id}")
            return False

        self.session.delete(project)
        self.session.commit()
        logger.info(f"Project deleted: {project_id}")
        return True


class UnitRepository:
    """Repository for Unit model operations."""

    def __init__(self, session: Session) -> None:
        """Initialize with database session."""
        self.session = session

    def create_unit(
        self,
        project_id: int,
        configuration: Optional[str] = None,
        carpet_area: Optional[str] = None,
        price: Optional[str] = None,
        possession_date: Optional[str] = None,
    ) -> Unit:
        """Create a new unit."""
        unit = Unit(
            project_id=project_id,
            configuration=configuration,
            carpet_area=carpet_area,
            price=price,
            possession_date=possession_date,
        )
        self.session.add(unit)
        self.session.commit()
        self.session.refresh(unit)
        logger.info(f"Unit created: {unit.id} in project {project_id}")
        return unit

    def get_unit_by_id(self, unit_id: int) -> Optional[Unit]:
        """Retrieve a unit by ID."""
        return self.session.query(Unit).filter(Unit.id == unit_id).first()

    def get_units_by_project(self, project_id: int) -> List[Unit]:
        """Retrieve all units for a project."""
        return (
            self.session.query(Unit)
            .filter(Unit.project_id == project_id)
            .order_by(Unit.created_at.desc())
            .all()
        )

    def search_units(
        self,
        project_id: Optional[int] = None,
        configuration: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
    ) -> List[Unit]:
        """Search units by filters."""
        query = self.session.query(Unit)

        filters = []
        if project_id is not None:
            filters.append(Unit.project_id == project_id)
        if configuration:
            filters.append(Unit.configuration.ilike(f"%{configuration}%"))

        if filters:
            query = query.filter(and_(*filters))

        # Note: price is stored as string, so numeric filtering requires conversion
        # This is handled at the service layer for cleaner code
        results = query.order_by(Unit.created_at.desc()).all()

        # Post-process price filtering
        if min_price is not None or max_price is not None:
            results = [u for u in results if self._matches_price_range(u, min_price, max_price)]

        return results

    @staticmethod
    def _matches_price_range(
        unit: Unit, min_price: Optional[float], max_price: Optional[float]
    ) -> bool:
        """Check if unit price falls within range."""
        if not unit.price:
            return False

        try:
            # Remove common currency symbols and parse
            price_str = unit.price.replace(",", "").split()[0]
            price = float(price_str)

            if min_price is not None and price < min_price:
                return False
            if max_price is not None and price > max_price:
                return False
            return True
        except (ValueError, IndexError):
            return False

    def update_unit(self, unit_id: int, **kwargs: Any) -> Optional[Unit]:
        """Update a unit by ID."""
        unit = self.get_unit_by_id(unit_id)
        if not unit:
            logger.warning(f"Unit not found: {unit_id}")
            return None

        allowed_fields = {
            "configuration",
            "carpet_area",
            "price",
            "possession_date",
        }

        for key, value in kwargs.items():
            if key in allowed_fields:
                setattr(unit, key, value)

        self.session.commit()
        self.session.refresh(unit)
        logger.info(f"Unit updated: {unit_id}")
        return unit

    def delete_unit(self, unit_id: int) -> bool:
        """Delete a unit by ID."""
        unit = self.get_unit_by_id(unit_id)
        if not unit:
            logger.warning(f"Unit not found: {unit_id}")
            return False

        self.session.delete(unit)
        self.session.commit()
        logger.info(f"Unit deleted: {unit_id}")
        return True
