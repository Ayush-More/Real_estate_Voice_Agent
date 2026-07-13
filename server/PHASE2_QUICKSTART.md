"""
# Phase 2: Quick Start Guide

## What Was Implemented

Phase 2 adds the **search_properties() tool** — a flexible property search function that queries your PostgreSQL database using SQLAlchemy repositories.

The tool is **independently testable** without running bot.py and provides an easy-to-use interface for searching real estate properties.

## Files Created

### Core Implementation
- `tools/__init__.py` — Package exports
- `tools/search_properties.py` — Main search_properties() function + convenience functions

### Testing & Documentation
- `test_search_properties.py` — Comprehensive independent tests
- `PHASE2_IMPLEMENTATION.md` — Detailed technical documentation

## Getting Started

### Quick Test

Verify the tool works:

```bash
cd server
uv run test_search_properties.py
```

Expected output:
```
🧪 TESTING search_properties() TOOL 🧪
This tool is independently testable WITHOUT bot.py

✓ ALL TESTS PASSED
```

### Basic Usage

```python
from tools import search_properties

# Search all properties
results = search_properties()

# Search by city
results = search_properties(city="Pune")

# Search by configuration
results = search_properties(configuration="2 BHK")

# Search by price range
results = search_properties(min_price=5000000, max_price=10000000)

# Multiple filters combined
results = search_properties(
    city="Pune",
    configuration="2 BHK",
    max_price=10000000
)

# Process results
for property in results:
    print(f"{property['project_name']} - {property['configuration']} - ₹{property['price']}")
```

## Supported Filters

All filters are **optional**. Combine any filters to narrow your search.

| Filter | Example | Description |
|--------|---------|-----------|
| `city` | `"Pune"` | Project city (partial, case-insensitive) |
| `locality` | `"Wakad"` | Project locality (partial, case-insensitive) |
| `configuration` | `"2 BHK"` | Unit type (partial, case-insensitive) |
| `min_price` | `5000000` | Minimum price in rupees |
| `max_price` | `10000000` | Maximum price in rupees |
| `possession_date` | `"December 2026"` | Expected possession (exact match) |
| `availability` | Reserved for future use |

## Response Format

Each result is a dictionary with:

```python
{
    "project_name": str,        # Project name
    "city": str,                # City
    "locality": str,            # Locality/area
    "configuration": str,       # Unit type (e.g., "2 BHK")
    "carpet_area": str,         # Carpet area in sq ft
    "price": str,               # Price in rupees
    "possession_date": str,     # Expected possession date
    "project_id": int,          # Database project ID
    "unit_id": int,             # Database unit ID
    "amenities": dict,          # JSON amenities
    "project_status": str,      # Project status
}
```

## Convenience Functions

For common search patterns:

```python
from tools.search_properties import search_properties_by_budget

# Budget search
results = search_properties_by_budget(max_price=10000000, city="Pune")

# Search by city
from tools.search_properties import search_properties_by_city
results = search_properties_by_city("Pune")

# Search by configuration
from tools.search_properties import search_properties_by_configuration
results = search_properties_by_configuration("2 BHK", city="Pune")
```

## Test Coverage

The tool includes 7 comprehensive tests:

1. ✓ Search all properties (no filters)
2. ✓ Search by city
3. ✓ Search by configuration
4. ✓ Search by price range
5. ✓ Multiple filters combined
6. ✓ No results handling
7. ✓ Response structure validation

Run tests:

```bash
uv run test_search_properties.py
```

## Key Features

- ✓ **No Raw SQL** — Uses SQLAlchemy repositories exclusively
- ✓ **Flexible Filtering** — All filters optional, combine any way
- ✓ **Type Safe** — Full type hints throughout
- ✓ **Logged** — All operations logged for debugging
- ✓ **Error Handling** — Graceful exception handling
- ✓ **Independent** — Works without bot.py
- ✓ **Production Ready** — Thoroughly tested
- ✓ **Extensible** — Easy to add new filters

## Integration with Voice Agent (Phase 7)

In Phase 7, this tool will be integrated with the Groq LLM so the voice agent can automatically call it when users ask property-related questions:

*"What 2 BHK properties are available in Pune?"*
→ Calls `search_properties(city="Pune", configuration="2 BHK")`
→ Returns matching properties
→ Agent speaks the results

For now, the tool is complete and ready for Phase 3.

## Project Structure

```
server/
├── tools/
│   ├── __init__.py              ✓ NEW
│   └── search_properties.py      ✓ NEW
├── test_search_properties.py     ✓ NEW
├── PHASE2_IMPLEMENTATION.md      ✓ NEW (detailed docs)
├── db/                           (unchanged from Phase 1)
├── config/                       (unchanged from Phase 1)
├── bot.py                        (unchanged)
└── (other files)
```

## No Breaking Changes

- ✓ Phase 1 database layer unchanged
- ✓ All Phase 1 tests still pass
- ✓ bot.py not modified
- ✓ No dependency updates required
- ✓ Backward compatible

## Next Steps

Phase 2 is **COMPLETE**. The next phase (Phase 3) will add:

- Document storage for PDFs (local folders)
- Preparation for RAG pipeline

The search_properties() tool is ready and can be used independently anytime.

## Debugging

If you encounter issues:

1. **Check database connection:**
   ```bash
   uv run db_init.py --test
   ```

2. **Run tests:**
   ```bash
   uv run test_search_properties.py
   ```

3. **Check logs:** All operations are logged with timestamps and details

4. **Database data:** Verify sample data exists:
   ```bash
   uv run db_init.py --init  # Create tables if needed
   uv run db_init.py --seed  # Seed sample data
   ```

## Example Usage Script

Create a file `demo_search.py`:

```python
from tools import search_properties
from tools.search_properties import search_properties_by_budget

# Example 1: All properties
print("All properties in database:")
results = search_properties()
print(f"  Found {len(results)} total")

# Example 2: By city
print("\nProperties in Pune:")
results = search_properties(city="Pune")
for prop in results:
    print(f"  • {prop['project_name']} - {prop['configuration']}")

# Example 3: Budget search
print("\nAffordable 2 BHK under 9M:")
results = search_properties_by_budget(
    max_price=9000000,
    configuration="2 BHK"
)
for prop in results:
    print(f"  • {prop['project_name']} - ₹{prop['price']}")

# Example 4: Complex search
print("\nLuxury units in Wakad, 3M-12M:")
results = search_properties(
    locality="Wakad",
    min_price=3000000,
    max_price=12000000
)
for prop in results:
    print(f"  • {prop['configuration']} - ₹{prop['price']}")
```

Run it:

```bash
uv run demo_search.py
```

---

**Phase 2 Status**: ✓ COMPLETE

The search_properties() tool is production-ready, thoroughly tested, and ready for Phase 3!

**To verify everything works**: `uv run test_search_properties.py`
"""
