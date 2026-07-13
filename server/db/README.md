"""
# Phase 1: PostgreSQL Database Layer

## Overview

Phase 1 implements a production-ready PostgreSQL database layer for the Real Estate Voice Agent using SQLAlchemy ORM. The database is completely isolated from the voice pipeline and can be used independently.

## Architecture

### Layered Design

```
┌─────────────────────────────────────────┐
│   Voice Pipeline (bot.py - unchanged)   │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│    Tools Layer (Phase 2+)                │
│    - search_properties()                 │
│    - search_documents()                  │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│   Repository/Service Layer (Phase 1)    │
│   - ProjectRepository                   │
│   - UnitRepository                       │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│   SQLAlchemy ORM Layer (Phase 1)         │
│   - Project Model                        │
│   - Unit Model                           │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│   PostgreSQL (Supabase)                  │
└─────────────────────────────────────────┘
```

## File Structure

```
server/
├── config/
│   ├── __init__.py
│   ├── database.py              # Database configuration
│   └── prompts.py               # (existing)
├── db/
│   ├── __init__.py              # Package exports
│   ├── models.py                # SQLAlchemy models + Pydantic schemas
│   ├── session.py               # Database session management
│   └── repositories.py          # Repository pattern implementation
├── db_init.py                   # Database initialization utility
├── .env.example                 # Environment variables template
├── bot.py                       # (existing - UNCHANGED)
└── pyproject.toml               # (updated with new dependencies)
```

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure with your Supabase credentials:

```bash
DB_HOST=db.zchsplaygtakpdyyjets.supabase.co
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=zBiS08KjYrmKwS7M
DB_NAME=postgres
DB_SSL_MODE=require
```

### Database Settings

Configuration is loaded from environment variables via `pydantic-settings`:

```python
from config import get_database_settings

settings = get_database_settings()
print(settings.database_url)  # postgresql+psycopg://...
```

## Database Models

### Project

Represents a real estate project.

**Fields:**
- `id` (BigInt, PK): Auto-incremented identifier
- `project_name` (String): Name of the project
- `city` (String): City where project is located
- `locality` (String): Locality/area within city
- `status` (String): Project status (e.g., "Under Construction", "Completed")
- `rera_number` (BigInt): RERA registration number
- `description` (String): Project description
- `brochure_url` (String): URL to project brochure
- `amenities` (JSON): Array of amenities (e.g., ["Pool", "Gym", "Security"])
- `created_at` (DateTime): Timestamp of creation
- `updated_at` (DateTime): Timestamp of last update

**Relationships:**
- One-to-Many with `Unit` (cascade delete)

### Unit

Represents an individual apartment/unit within a project.

**Fields:**
- `id` (BigInt, PK): Auto-incremented identifier
- `project_id` (BigInt, FK): Reference to Project
- `configuration` (String): Unit type (e.g., "2 BHK", "3 BHK")
- `carpet_area` (String): Carpet area in sq ft
- `price` (String): Price of the unit
- `possession_date` (String): Expected possession date
- `created_at` (DateTime): Timestamp of creation

**Relationships:**
- Many-to-One with `Project`

## Session Management

### Singleton Pattern

Database session is managed as a singleton to ensure a single connection pool:

```python
from db import get_db_instance

db = get_db_instance()
session = db.get_session()
try:
    # Use session
    pass
finally:
    session.close()
```

### Dependency Injection

For FastAPI endpoints:

```python
from db import get_db_session
from fastapi import Depends

@app.get("/projects")
async def get_projects(session: Session = Depends(get_db_session)):
    repo = ProjectRepository(session)
    return repo.get_all_projects()
```

## Repository Pattern

### ProjectRepository

Provides CRUD operations and queries for Projects.

```python
from db import ProjectRepository, get_db_instance

db = get_db_instance()
session = db.get_session()
repo = ProjectRepository(session)

# Create
project = repo.create_project(
    project_name="Sky Heights",
    city="Pune",
    locality="Wakad"
)

# Read
project = repo.get_project_by_id(1)
projects = repo.get_all_projects(skip=0, limit=10)

# Search
results = repo.search_projects(city="Pune", locality="Wakad")

# Update
repo.update_project(1, status="Completed")

# Delete
repo.delete_project(1)

session.close()
```

### UnitRepository

Provides CRUD operations and queries for Units.

```python
from db import UnitRepository

repo = UnitRepository(session)

# Create
unit = repo.create_unit(
    project_id=1,
    configuration="2 BHK",
    carpet_area="720",
    price="8500000"
)

# Read
unit = repo.get_unit_by_id(1)
units = repo.get_units_by_project(project_id=1)

# Search
results = repo.search_units(
    project_id=1,
    configuration="2 BHK",
    min_price=5000000,
    max_price=10000000
)

# Update
repo.update_unit(1, price="9000000")

# Delete
repo.delete_unit(1)
```

## Database Initialization

### Initialize Tables

```bash
cd server
uv sync
uv run db_init.py --init
```

This creates the `projects` and `units` tables in your Supabase database.

### Test Connection

```bash
uv run db_init.py --test
```

Verifies the database connection and shows table statistics.

### Seed Sample Data

```bash
uv run db_init.py --seed
```

Populates the database with sample real estate data (Sky Heights Residency project with multiple units).

## Pydantic Schemas

For API responses and validation:

```python
from db import ProjectSchema, UnitSchema, ProjectDetailSchema

# Single unit
unit_schema = UnitSchema.model_validate(unit_obj)

# Project with units
project_detail = ProjectDetailSchema.model_validate(project_obj)
```

## Connection Pooling

The session manager includes production-ready connection pooling:

- **Pool Size**: 10 connections
- **Max Overflow**: 20 additional connections
- **Pool Pre-ping**: Verifies connections before use
- **Pool Recycle**: Recycles connections every 3600 seconds (1 hour)

## Error Handling

All repository methods include logging:

```python
from loguru import logger

try:
    project = repo.get_project_by_id(999)
    if not project:
        logger.warning(f"Project not found: 999")
except Exception as e:
    logger.error(f"Database error: {e}")
```

## Testing the Database Layer

The database layer is independently testable without Pipecat:

```python
# test_db.py
from db import ProjectRepository, UnitRepository, get_db_instance

db = get_db_instance()
session = db.get_session()

project_repo = ProjectRepository(session)
unit_repo = UnitRepository(session)

# Test operations
project = project_repo.create_project(project_name="Test Project", city="Test City")
unit = unit_repo.create_unit(project_id=project.id, configuration="2 BHK")

results = unit_repo.search_units(project_id=project.id)
assert len(results) == 1

session.close()
```

## Next Steps (Not Implemented in Phase 1)

- Phase 2: Implement `search_properties()` tool using repository
- Phase 3: Document storage for PDFs
- Phase 4: RAG indexing pipeline with Qdrant
- Phase 5: RAG retrieval pipeline
- Phase 6: `search_documents()` tool
- Phase 7: Integrate tools with Groq LLM

## Dependencies Added

```toml
sqlalchemy>=2.0.0,<3
psycopg[binary]>=3.1.0
pydantic>=2.0.0,<3
pydantic-settings>=2.0.0,<3
```

## Key Design Decisions

1. **Isolation**: Database layer is completely separate from voice pipeline
2. **Singleton**: Single connection pool managed globally
3. **Repository Pattern**: Clean separation of data access logic
4. **Pydantic Models**: Type-safe schemas for API responses
5. **Connection Pooling**: Production-ready with retry logic
6. **String Prices**: Prices stored as strings to preserve formatting
7. **JSON Amenities**: Flexible storage for variable amenity lists
8. **Cascade Delete**: Deleting a project removes all related units
9. **Logging**: Comprehensive logging for debugging

## Troubleshooting

### Connection Failed

Check your `.env` file:
```bash
DB_HOST=db.zchsplaygtakpdyyjets.supabase.co
DB_PASSWORD=zBiS08KjYrmKwS7M
DB_SSL_MODE=require
```

### Table Already Exists

Tables are created only if they don't exist. To reset:

```python
from db import get_db_instance
db = get_db_instance()
db.drop_all_tables()  # WARNING: This deletes all data
db.create_all_tables()
```

### Slow Queries

Enable SQL logging by uncommenting in `db/session.py`:

```python
@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    logger.debug(f"SQL: {statement}")
```

---

**Status**: ✓ Phase 1 Complete
**Next**: Phase 2 — search_properties() Tool
"""
