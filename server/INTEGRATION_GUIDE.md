"""
# Integration Guide — Phase 1

## Overview

Phase 1 implements a standalone database layer that is **completely independent** from the voice pipeline. This guide explains how the layers are organized and how they will integrate in future phases.

## Current Architecture (Phase 1)

```
┌──────────────────────────────────┐
│   Voice Pipeline (bot.py)         │
│  - Deepgram STT                   │
│  - Groq LLM                        │
│  - Sarvam TTS                      │
│  - Pipecat Framework               │
│  - WebRTC Transport                │
│                                   │
│  [UNCHANGED - No modifications]    │
└──────────────────────────────────┘
         ↓ (will integrate in Phase 2)
┌──────────────────────────────────┐
│   Tools Layer (Phase 2+)          │
│  [NOT YET IMPLEMENTED]            │
└──────────────────────────────────┘
         ↓
┌──────────────────────────────────┐
│   Isolated Database Layer (Phase 1)│
│  - ProjectRepository              │
│  - UnitRepository                 │
│  - SQLAlchemy Models              │
│  - Connection Management          │
│                                   │
│  [CAN BE TESTED INDEPENDENTLY]    │
└──────────────────────────────────┘
         ↓
┌──────────────────────────────────┐
│   PostgreSQL / Supabase           │
└──────────────────────────────────┘
```

## Why Isolated?

1. **Testability**: Test database queries without running voice pipeline
2. **Reusability**: Repository layer can be used by any service
3. **Separation of Concerns**: Business logic stays out of bot.py
4. **Scalability**: Easy to add more services (API endpoints, cron jobs, etc.)
5. **Maintainability**: Changes to database don't affect voice pipeline

## Testing the Database Layer

The database layer works independently:

```bash
cd server

# 1. Create tables
uv run db_init.py --init

# 2. Verify connection
uv run db_init.py --test

# 3. Seed sample data
uv run db_init.py --seed
```

You can test all database operations **without running bot.py**.

## Example: Query Projects Independently

Create a test script `server/test_db.py`:

```python
#!/usr/bin/env python
"""Standalone database test (no bot.py required)."""

from db import ProjectRepository, UnitRepository, get_db_instance

def main():
    # Get database instance
    db = get_db_instance()
    session = db.get_session()

    try:
        # Initialize repositories
        project_repo = ProjectRepository(session)
        unit_repo = UnitRepository(session)

        # Query all projects
        projects = project_repo.get_all_projects()
        print(f"Total projects: {len(projects)}")

        # Search projects
        pune_projects = project_repo.search_projects(city="Pune")
        for project in pune_projects:
            print(f"- {project.project_name} in {project.city}")

        # Query units for each project
        for project in projects:
            units = unit_repo.get_units_by_project(project.id)
            print(f"  Units: {len(units)}")

    finally:
        session.close()

if __name__ == "__main__":
    main()
```

Run it:

```bash
uv run test_db.py
```

## Future Integration: Phase 2

In Phase 2, we'll create a `search_properties()` tool that uses the repository layer:

```python
# tools/search_properties.py (WILL BE CREATED IN PHASE 2)

from db import ProjectRepository, UnitRepository, get_db_instance

def search_properties(
    city: str = None,
    configuration: str = None,
    max_price: float = None,
    **filters
) -> list[dict]:
    """Tool for searching properties (Phase 2)."""
    
    db = get_db_instance()
    session = db.get_session()
    
    try:
        project_repo = ProjectRepository(session)
        unit_repo = UnitRepository(session)
        
        # Find projects matching city filter
        projects = project_repo.search_projects(city=city)
        
        # Find units with matching criteria
        results = []
        for project in projects:
            units = unit_repo.search_units(
                project_id=project.id,
                configuration=configuration,
                max_price=max_price
            )
            
            for unit in units:
                results.append({
                    "project_name": project.project_name,
                    "configuration": unit.configuration,
                    "price": unit.price,
                    "carpet_area": unit.carpet_area
                })
        
        return results
    
    finally:
        session.close()
```

Then in Phase 7, we'll register this tool with the LLM:

```python
# bot.py (MODIFICATION IN PHASE 7)

from tools.search_properties import search_properties

llm = GroqLLMService(
    api_key=os.environ["GROQ_API_KEY"],
    settings=GroqLLMService.Settings(
        model="llama-3.3-70b-versatile",
        system_instruction=REAL_ESTATE_SYSTEM_PROMPT,
        tools=[
            {
                "name": "search_properties",
                "description": "Search real estate properties",
                "function": search_properties
            }
        ]
    ),
)
```

## How Phases Build On Each Other

```
Phase 1 (Current)
├─ SQLAlchemy Models ✓
├─ Repository Pattern ✓
├─ Database Session ✓
└─ Connection Pooling ✓
   ↓
Phase 2
├─ search_properties() tool
├─ Uses ProjectRepository
├─ Uses UnitRepository
└─ No bot.py changes
   ↓
Phase 3
├─ Document Storage
├─ Local folder structure
└─ No database changes
   ↓
Phase 4
├─ RAG Indexing Pipeline
├─ Uses Document Storage
├─ Writes to Qdrant
└─ No bot.py changes
   ↓
Phase 5
├─ RAG Retrieval Pipeline
├─ Queries Qdrant
└─ No bot.py changes
   ↓
Phase 6
├─ search_documents() tool
├─ Uses Qdrant Retrieval
└─ No database changes
   ↓
Phase 7
├─ Tool Integration
├─ Register search_properties() with LLM ← bot.py modified here
├─ Register search_documents() with LLM
└─ LLM automatically decides which tool to use
```

## Development Workflow

### For Phase 1 (Now)

1. ✓ Database schema is defined
2. ✓ Models are created
3. ✓ Repository layer is ready
4. ✓ Connection pooling is configured
5. ✓ Can be tested independently

**What you can do now:**
- Run `db_init.py --init` to create tables
- Run `db_init.py --seed` to add sample data
- Query the database using repositories
- Test queries without voice pipeline

### For Phase 2 (Next)

1. Create `tools/search_properties.py`
2. Implement property search using repositories
3. Test tool independently
4. Verify queries and results

### For Phase 7 (Final Integration)

1. Register tools with Groq LLM
2. Modify bot.py to include tools
3. Test end-to-end with voice pipeline
4. LLM will automatically call tools when needed

## Dependency Injection Pattern

Throughout the codebase, we use dependency injection:

```python
# Current (Phase 1)
from db import get_db_instance

db = get_db_instance()
session = db.get_session()
repo = ProjectRepository(session)

# Future (Phase 2+)
def search_properties(filters: dict, session: Session = None):
    if session is None:
        db = get_db_instance()
        session = db.get_session()
        should_close = True
    else:
        should_close = False
    
    try:
        repo = ProjectRepository(session)
        return repo.search_projects(**filters)
    finally:
        if should_close:
            session.close()
```

This allows:
- Testing with mock sessions
- Integration with FastAPI dependencies
- Reusing sessions across multiple operations
- Proper resource cleanup

## FAQs

### Q: Can I run the database layer without bot.py?
**A**: Yes! The database is completely independent. Use `db_init.py` for testing.

### Q: Will bot.py be modified in Phase 1?
**A**: No. Phase 1 only adds database layer. bot.py remains unchanged.

### Q: When does bot.py get modified?
**A**: Phase 7, when tools are registered with the LLM.

### Q: Can I query the database while bot.py is running?
**A**: Yes! The connection pool supports concurrent access.

### Q: How do I add more database tables?
**A**: Create new models in `db/models.py`, then create repositories in `db/repositories.py`.

### Q: Can I use this with other frameworks?
**A**: Yes! The repository layer is framework-agnostic and can be integrated with FastAPI, Flask, Django, etc.

## Best Practices

1. **Always close sessions**: Use try/finally or context managers
2. **Use repositories**: Don't query directly in bot.py or tools
3. **Validate input**: Repositories validate allowed fields
4. **Log operations**: All CRUD operations are logged
5. **Handle exceptions**: Repository methods are defensive
6. **Type hints**: All functions have type annotations
7. **Pydantic schemas**: Use schemas for API responses

## Performance Considerations

1. **Connection Pooling**: 10 default connections, scales to 30
2. **Connection Reuse**: Connections recycled every hour
3. **Query Optimization**: Use specific queries, not select all
4. **Indexing**: Consider adding indexes on frequently queried fields:
   - projects.city
   - projects.locality
   - units.project_id
   - units.configuration

## Security Considerations

1. **Credentials**: Never hardcode passwords, use .env
2. **SQL Injection**: All queries use parameterized statements
3. **SSL**: Enabled by default with DB_SSL_MODE=require
4. **Connection Pool**: Uses pre-ping to detect stale connections
5. **Error Logging**: Sensitive data is not logged

---

**Current Status**: ✓ Phase 1 Complete — Database layer ready for testing
**Next Phase**: Phase 2 — search_properties() Tool Implementation
"""
