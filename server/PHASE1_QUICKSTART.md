"""
# Phase 1 — Quick Start Guide

## What Was Implemented

Phase 1 adds a **production-ready PostgreSQL database layer** to your voice agent using SQLAlchemy ORM. The database is **completely isolated** from the voice pipeline and remains **fully testable independently**.

## Files Created

### Core Database Layer
- `db/models.py` — SQLAlchemy models for Projects and Units + Pydantic schemas
- `db/session.py` — Database connection management with connection pooling
- `db/repositories.py` — Repository pattern for database operations
- `db/__init__.py` — Package exports

### Configuration
- `config/database.py` — Database settings from environment variables
- `config/__init__.py` — Updated with database configuration exports

### Utilities
- `db_init.py` — Database initialization and management CLI
- `.env.example` — Template for environment variables
- `db/README.md` — Comprehensive database documentation
- `INTEGRATION_GUIDE.md` — Architecture and future integration guide

### Updated Files
- `pyproject.toml` — Added SQLAlchemy, psycopg, and Pydantic dependencies

## Getting Started

### Step 1: Install Dependencies

```bash
cd server
uv sync
```

This installs all new dependencies including SQLAlchemy and psycopg.

### Step 2: Configure Database

Copy `.env.example` to `.env` and add your Supabase credentials:

```bash
# server/.env

DB_HOST=db.zchsplaygtakpdyyjets.supabase.co
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=zBiS08KjYrmKwS7M    # Your Supabase password
DB_NAME=postgres
DB_SSL_MODE=require
```

### Step 3: Initialize Database

Create the tables in your Supabase PostgreSQL database:

```bash
uv run db_init.py --init
```

**Output:**
```
2024-XX-XX XX:XX:XX.XXX | INFO     | Database initialized: db.zchsplaygtakpdyyjets.supabase.co:5432/postgres
2024-XX-XX XX:XX:XX.XXX | SUCCESS  | ✓ Database tables created successfully
```

### Step 4: Test Connection

Verify the connection works:

```bash
uv run db_init.py --test
```

**Output:**
```
2024-XX-XX XX:XX:XX.XXX | SUCCESS  | ✓ Database connection successful
2024-XX-XX XX:XX:XX.XXX | INFO     | Total projects in database: 0
```

### Step 5: Seed Sample Data (Optional)

Populate with sample real estate data:

```bash
uv run db_init.py --seed
```

**Output:**
```
2024-XX-XX XX:XX:XX.XXX | SUCCESS  | ✓ Created project: Sky Heights Residency (ID: 1)
2024-XX-XX XX:XX:XX.XXX | SUCCESS  | ✓ Created unit: 1 BHK - ₹4500000
2024-XX-XX XX:XX:XX.XXX | SUCCESS  | ✓ Created unit: 2 BHK - ₹8500000
2024-XX-XX XX:XX:XX.XXX | SUCCESS  | ✓ Created unit: 3 BHK - ₹12000000
2024-XX-XX XX:XX:XX.XXX | SUCCESS  | ✓ Sample data seeded successfully
```

## Testing Queries Independently

Create a test script (no bot.py required):

```python
# server/test_query.py

from db import ProjectRepository, UnitRepository, get_db_instance

db = get_db_instance()
session = db.get_session()

try:
    # Query projects
    project_repo = ProjectRepository(session)
    projects = project_repo.get_all_projects()
    
    for project in projects:
        print(f"Project: {project.project_name} in {project.city}")
        
        # Query units for each project
        unit_repo = UnitRepository(session)
        units = unit_repo.get_units_by_project(project.id)
        
        for unit in units:
            print(f"  - {unit.configuration}: ₹{unit.price}")

finally:
    session.close()
```

Run it:

```bash
uv run test_query.py
```

## Key Classes & Methods

### ProjectRepository

```python
from db import ProjectRepository, get_db_instance

db = get_db_instance()
session = db.get_session()
repo = ProjectRepository(session)

# Create
project = repo.create_project(project_name="...", city="...")

# Read
project = repo.get_project_by_id(1)
projects = repo.get_all_projects(skip=0, limit=10)

# Search
results = repo.search_projects(city="Pune", locality="Wakad")

# Update
repo.update_project(1, status="Completed")

# Delete
repo.delete_project(1)
```

### UnitRepository

```python
from db import UnitRepository

repo = UnitRepository(session)

# Create
unit = repo.create_unit(
    project_id=1,
    configuration="2 BHK",
    price="8500000"
)

# Read
unit = repo.get_unit_by_id(1)
units = repo.get_units_by_project(1)

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

## Database Schema

### projects table

| Column | Type | Constraints |
|--------|------|-----------|
| id | bigint | PK, auto-increment |
| project_name | varchar | |
| city | varchar | |
| locality | varchar | |
| status | varchar | |
| rera_number | bigint | |
| description | varchar | |
| brochure_url | varchar | |
| amenities | json | |
| created_at | timestamp | NOT NULL, default now() |
| updated_at | timestamp | default now() |

### units table

| Column | Type | Constraints |
|--------|------|-----------|
| id | bigint | PK, auto-increment |
| project_id | bigint | FK → projects.id |
| configuration | varchar | |
| carpet_area | varchar | |
| price | varchar | |
| possession_date | varchar | |
| created_at | timestamp | NOT NULL, default now() |

## Pydantic Schemas

Use schemas for API responses:

```python
from db import ProjectSchema, UnitSchema, ProjectDetailSchema

# Convert ORM objects to schemas
unit_schema = UnitSchema.model_validate(unit_obj)
project_with_units = ProjectDetailSchema.model_validate(project_obj)

# Access data
print(project_with_units.project_name)
print(project_with_units.units)
```

## Important: bot.py Remains Unchanged

The voice pipeline (`bot.py`) has **NOT been modified**. The database layer is:
- ✓ Completely isolated
- ✓ Independently testable
- ✓ Ready for Phase 2 tool integration

To run the voice agent:

```bash
uv run bot.py
```

Everything works as before.

## What's Next (Future Phases)

- **Phase 2**: Implement `search_properties()` tool using repositories
- **Phase 3**: Document storage for PDFs (local folders)
- **Phase 4**: RAG indexing pipeline with Qdrant
- **Phase 5**: RAG retrieval pipeline
- **Phase 6**: `search_documents()` tool
- **Phase 7**: Register tools with Groq LLM (bot.py modified here)

## Documentation

- `db/README.md` — Complete database layer documentation
- `INTEGRATION_GUIDE.md` — Architecture and future integration plan
- `.env.example` — Environment variables template

## Dependencies Added

```toml
sqlalchemy>=2.0.0,<3
psycopg[binary]>=3.1.0
pydantic>=2.0.0,<3
pydantic-settings>=2.0.0,<3
```

## Troubleshooting

### Connection Failed

Check your `.env` file has the correct Supabase credentials:

```bash
DB_HOST=db.zchsplaygtakpdyyjets.supabase.co
DB_PASSWORD=zBiS08KjYrmKwS7M
DB_SSL_MODE=require
```

Run test to verify:

```bash
uv run db_init.py --test
```

### Tables Already Exist

Tables are only created if they don't exist. To reset (WARNING: deletes data):

```python
from db import get_db_instance

db = get_db_instance()
db.drop_all_tables()
db.create_all_tables()
```

### Missing Dependencies

Ensure you ran `uv sync`:

```bash
uv sync
```

## Support

- See `db/README.md` for detailed documentation
- See `INTEGRATION_GUIDE.md` for architecture and future phases
- Check `.env.example` for configuration reference

---

**Phase 1 Status**: ✓ COMPLETE

Your database layer is production-ready and can be tested independently!

Next: [Phase 2 — search_properties() Tool](INTEGRATION_GUIDE.md#future-integration-phase-2)
"""
