"""Database session management."""

from typing import Generator, Optional
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from loguru import logger

from config.database import get_database_settings, DatabaseSettings
from db.models import Base


class DatabaseSession:
    """Manages database connections and sessions."""

    _instance: Optional["DatabaseSession"] = None
    _engine: Optional[Engine] = None
    _session_factory: Optional[sessionmaker] = None

    def __new__(cls) -> "DatabaseSession":
        """Singleton pattern for database session manager."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize database connection (lazy initialization)."""
        if self._initialized:
            return

        self._settings = get_database_settings()
        self._init_engine()
        self._session_factory = sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
            class_=Session,
        )
        self._initialized = True
        logger.info(
            f"Database initialized: {self._settings.db_host}:{self._settings.db_port}/{self._settings.db_name}"
        )

    def _init_engine(self) -> None:
        """Create SQLAlchemy engine with connection pooling."""
        self._engine = create_engine(
            self._settings.database_url,
            echo=False,  # Set to True for SQL debugging
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,  # Verify connections before using
            pool_recycle=3600,  # Recycle connections every hour
        )

        # Log SQL statements (optional, for debugging)
        # @event.listens_for(Engine, "before_cursor_execute")
        # def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        #     logger.debug(f"SQL: {statement}")

    def get_session(self) -> Session:
        """Get a new database session."""
        if self._session_factory is None:
            raise RuntimeError("Database not initialized. Call __init__ first.")
        return self._session_factory()

    def create_all_tables(self) -> None:
        """Create all tables in the database."""
        if self._engine is None:
            raise RuntimeError("Database engine not initialized.")
        Base.metadata.create_all(self._engine)
        logger.info("All database tables created successfully")

    def drop_all_tables(self) -> None:
        """Drop all tables (use with caution)."""
        if self._engine is None:
            raise RuntimeError("Database engine not initialized.")
        Base.metadata.drop_all(self._engine)
        logger.warning("All database tables dropped")

    def close(self) -> None:
        """Close all database connections."""
        if self._engine is not None:
            self._engine.dispose()
            logger.info("Database connections closed")


# Singleton instance
_db_session_manager = DatabaseSession()


def get_db_session() -> Generator[Session, None, None]:
    """Dependency injection for database sessions (FastAPI compatible)."""
    session = _db_session_manager.get_session()
    try:
        yield session
    finally:
        session.close()


def get_db_instance() -> DatabaseSession:
    """Get the database session manager instance."""
    return _db_session_manager
