"""SQLAlchemy models for Real Estate database."""

from datetime import datetime
from typing import Optional, List
import json

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    String,
    Integer,
    JSON,
    func,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped
from pydantic import BaseModel, Field

Base = declarative_base()


class Project(Base):
    """Real estate project model."""

    __tablename__ = "projects"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(
        DateTime(timezone=False), nullable=True, default=func.now(), onupdate=func.now()
    )
    project_name = Column(String, nullable=True)
    city = Column(String, nullable=True)
    locality = Column(String, nullable=True)
    status = Column(String, nullable=True)
    rera_number = Column(BigInteger, nullable=True)
    description = Column(String, nullable=True)
    brochure_url = Column(String, nullable=True)
    amenities = Column(JSON, nullable=True)

    # Relationship
    units: Mapped[List["Unit"]] = relationship(
        "Unit", back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name={self.project_name}, city={self.city})>"


class Unit(Base):
    """Real estate unit model."""

    __tablename__ = "units"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    project_id = Column(BigInteger, ForeignKey("projects.id"), nullable=True)
    configuration = Column(String, nullable=True)
    carpet_area = Column(String, nullable=True)
    price = Column(String, nullable=True)
    possession_date = Column(String, nullable=True)

    # Relationship
    project: Mapped["Project"] = relationship("Project", back_populates="units")

    def __repr__(self) -> str:
        return f"<Unit(id={self.id}, project_id={self.project_id}, config={self.configuration})>"


# ============= Pydantic Schemas =============
# Used for API responses and validation


class UnitSchema(BaseModel):
    """Pydantic schema for Unit."""

    id: int
    project_id: Optional[int] = None
    configuration: Optional[str] = None
    carpet_area: Optional[str] = None
    price: Optional[str] = None
    possession_date: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectSchema(BaseModel):
    """Pydantic schema for Project."""

    id: int
    project_name: Optional[str] = None
    city: Optional[str] = None
    locality: Optional[str] = None
    status: Optional[str] = None
    rera_number: Optional[int] = None
    description: Optional[str] = None
    brochure_url: Optional[str] = None
    amenities: Optional[dict] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProjectDetailSchema(ProjectSchema):
    """Pydantic schema for Project with units."""

    units: List[UnitSchema] = Field(default_factory=list)

    class Config:
        from_attributes = True
