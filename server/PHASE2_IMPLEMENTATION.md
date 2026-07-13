"""
# Phase 2: search_properties() Tool

## Overview

Phase 2 implements the `search_properties()` tool — a flexible property search function that queries PostgreSQL using SQLAlchemy repositories (no raw SQL).

The tool is **independently testable** without running bot.py and can search real estate properties using various optional filters.

## Architecture

```
┌──────────────────────────────────┐
│   search_properties() Tool       │
│   (tools/search_properties.py)   │
│  - Flexible filtering            │
│  - No raw SQL                    │
│  - Returns structured JSON       │
└──────────────────────────────────┘
         ↓ Uses
┌──────────────────────────────────┐
│   Repositories (Phase 1)         │
│  - ProjectRepository             │
│  - UnitRepository                │
└──────────────────────────────────┘
         ↓ Queries
┌──────────────────────────────────┐
│   PostgreSQL / Supabase          │
└──────────────────────────────────┘
```

## Implementation

### Supported Filters

All filters are **optional**. Leave them undefined to exclude from search.

| Filter | Type | Description |
|--------|------|-----------|
| `city` | str | Project city (partial match, case-insensitive) |
| `locality` | str | Project locality (partial match, case-insensitive) |
| `configuration` | str | Unit type like "2 BHK" (partial match, case-insensitive) |
| `min_price` | float | Minimum unit price in rupees (inclusive) |
| `max_price` | float | Maximum unit price in rupees (inclusive) |
| `possession_date` | str | Expected possession date (exact match) |
| `availability` | str | Availability status (reserved for future schema updates) |

### Response Format

Returns a list of dictionaries:

```python
[
    {
        "project_name": "Sky Heights Residency",
        "city": "Pune",
        "locality": "Wakad",
        "configuration": "2 BHK",
        "carpet_area": "720",
        "price": "8500000",
        "possession_date": "December 2026",
        "project_id": 1,
        "unit_id": 2,
        "amenities": {
            "features": ["Swimming Pool", "Gym", "Security"],
            "nearbyMetro": True
        },
        "project_status": "Under Construction"
    },
    ...
]
```

## Usage Examples

### Basic Import

```python
from tools import search_properties

# Search all properties (no filters)
results = search_properties()
```

### Single Filter

```python
# All 2 BHK properties
results = search_properties(configuration="2 BHK")

# All properties in Pune
results = search_properties(city="Pune")

# Properties under 10 million rupees
results = search_properties(max_price=10000000)
```

### Multiple Filters (AND logic)

```python
# 2 BHK properties in Pune under 10M
results = search_properties(
    city="Pune",
    configuration="2 BHK",
    max_price=10000000
)
```

### Price Range

```python
# Properties between 5M and 10M
results = search_properties(
    min_price=5000000,
    max_price=10000000
)
```

### Complex Search

```python
# 3 BHK luxury apartments in Wakad locality
results = search_properties(
    locality="Wakad",
    configuration="3 BHK",
    min_price=8000000,
    max_price=15000000
)
```

## Convenience Functions

### search_properties_by_budget()

Search properties within a budget:

```python
from tools.search_properties import search_properties_by_budget

# Find affordable 2 BHK in Pune under 9M
results = search_properties_by_budget(
    max_price=9000000,
    city="Pune",
    configuration="2 BHK"
)
```

### search_properties_by_city()

All properties in a city:

```python
from tools.search_properties import search_properties_by_city

results = search_properties_by_city("Pune")
```

### search_properties_by_configuration()

All properties of a specific type:

```python
from tools.search_properties import search_properties_by_configuration

# All 2 BHK properties in the database
results = search_properties_by_configuration("2 BHK")

# All 2 BHK properties in Bangalore
results = search_properties_by_configuration("2 BHK", city="Bangalore")
```

## Testing (Independent of bot.py)

The tool is fully testable without running the voice pipeline:

```bash
cd server
uv run test_search_properties.py
```

Test coverage includes:
- ✓ Search all properties (no filters)
- ✓ Search by city
- ✓ Search by configuration
- ✓ Search by price range
- ✓ Multiple filters combined
- ✓ Empty result sets
- ✓ Response structure validation

### Example Test Output

```
🧪 TESTING search_properties() TOOL 🧪
This tool is independently testable WITHOUT bot.py

============================================================
Test 1: Search ALL properties (no filters)
============================================================

Found 3 total properties
  • Sky Heights Residency - 3 BHK - ₹12000000 (950 sq ft)
  • Sky Heights Residency - 2 BHK - ₹8500000 (720 sq ft)
  • Sky Heights Residency - 1 BHK - ₹4500000 (550 sq ft)

✓ ALL TESTS PASSED
```

## Implementation Details

### No Raw SQL

All queries use SQLAlchemy repositories with parameterized statements:

```python
# ✓ GOOD - Uses repository methods
projects = project_repo.search_projects(city=city, locality=locality)
units = unit_repo.search_units(project_id=id, configuration=config)

# ✗ AVOID - Raw SQL
session.execute("SELECT * FROM projects WHERE city = ?", (city,))
```

### Dynamic Query Construction

Filters are applied progressively:

1. **Project-level filters**: City, locality
2. **Unit-level filters**: Configuration, price range
3. **Post-processing**: Possession date, availability

```python
# Only applies filters that are provided
projects = project_repo.search_projects(city=city, locality=locality)
# If city=None and locality="Wakad", only locality filter applies
```

### Error Handling

Gracefully handles exceptions:

```python
try:
    results = search_properties(city="Pune")
except Exception as e:
    logger.error(f"Search failed: {e}")
    # Returns empty list, doesn't crash
```

### Logging

Comprehensive logging for debugging:

```
INFO     | Searching properties: city=Pune, config=2 BHK, price_range=[5M, 10M]
DEBUG    | Found 3 projects matching location filters
DEBUG    | Project 1: 2 units match criteria
INFO     | Search completed: returned 2 results
```

## File Structure

```
server/
├── tools/
│   ├── __init__.py                  # Package exports
│   └── search_properties.py          # Main implementation
├── test_search_properties.py         # Comprehensive tests
└── (Phase 1 files unchanged)
```

## Performance Characteristics

### Query Optimization

1. **Project-level filtering first**: Reduces units to scan
2. **Unit-level filtering second**: Narrows down results
3. **No full table scans**: Uses indexed lookups via repositories

### Connection Pooling

Uses Phase 1 connection pooling:
- Session automatically reused
- Connections recycled every 3600 seconds
- Pre-ping verifies connection health

### Result Size

For typical real estate databases:
- 100 projects × 5 units each = 500 total units
- Average query returns 10-50 properties
- Response time: < 1 second for most searches

## Integration with bot.py (Phase 7)

In Phase 7, this tool will be registered with the Groq LLM:

```python
# bot.py (FUTURE - Phase 7)
from tools import search_properties

llm = GroqLLMService(
    api_key=os.environ["GROQ_API_KEY"],
    settings=GroqLLMService.Settings(
        model="llama-3.3-70b-versatile",
        tools=[
            {
                "name": "search_properties",
                "description": "Search real estate properties",
                "function": search_properties,
                "parameters": {
                    "city": {"type": "string", "description": "City name"},
                    "configuration": {"type": "string", "description": "BHK type"},
                    "max_price": {"type": "number", "description": "Max price"},
                    # ... other parameters
                }
            }
        ]
    ),
)
```

Then the LLM will automatically call the tool when users ask:
- *"What 2 BHK properties are available in Pune?"*
- *"Find me properties under 10 million rupees"*
- *"Show me all available units"*

## Testing Checklist

- ✓ Function accepts all optional filters
- ✓ Returns correct structured JSON format
- ✓ Handles no results gracefully
- ✓ Combines filters correctly (AND logic)
- ✓ Uses repositories (no raw SQL)
- ✓ Closes database sessions properly
- ✓ Logs all operations
- ✓ Independently testable (no bot.py required)
- ✓ Type hints for all parameters
- ✓ Comprehensive docstrings

## Next Steps (Phase 3+)

Phase 2 provides:
- ✓ Property search tool
- ✓ Clean integration point for Phase 3

Future phases will add:
- Phase 3: Document storage (PDFs)
- Phase 4: RAG indexing (Qdrant)
- Phase 5: RAG retrieval
- Phase 6: search_documents() tool
- Phase 7: LLM tool registration

The search_properties() tool is **complete and ready** for integration.

## Support

- Run tests: `uv run test_search_properties.py`
- Check logs for debugging information
- All database operations are logged at INFO/DEBUG level
- See `db/README.md` for database layer details

---

**Phase 2 Status**: ✓ COMPLETE

The search_properties() tool is production-ready and fully tested!
"""
