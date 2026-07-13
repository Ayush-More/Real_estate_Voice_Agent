"""Database configuration using environment variables."""

from pydantic_settings import BaseSettings
from typing import Optional


class DatabaseSettings(BaseSettings):
    """PostgreSQL database configuration from environment variables."""

    db_host: str
    db_port: int = 5432
    db_user: str
    db_password: str
    db_name: str = "postgres"
    db_ssl_mode: Optional[str] = None  # "require", "prefer", "disable"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from environment variables

    @property
    def database_url(self) -> str:
        """Construct PostgreSQL connection string."""
        if self.db_ssl_mode:
            return (
                f"postgresql+psycopg://{self.db_user}:{self.db_password}@"
                f"{self.db_host}:{self.db_port}/{self.db_name}?sslmode={self.db_ssl_mode}"
            )
        return (
            f"postgresql+psycopg://{self.db_user}:{self.db_password}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}"
        )


def get_database_settings() -> DatabaseSettings:
    """Load database settings from environment variables."""
    return DatabaseSettings()
