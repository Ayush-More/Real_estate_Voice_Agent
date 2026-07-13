"""Search properties tool for Real Estate Voice Agent.

This tool provides flexible property search across projects and units
without hardcoding SQL. It uses SQLAlchemy repositories for all queries.

The function is independently testable without Pipecat.
"""

from typing import List, Dict, Any, Optional
from loguru import logger

from db import ProjectRepository, UnitRepository, get_db_instance


def search_properties(
    city: Optional[str] = None,
    locality: Optional[str] = None,
    configuration: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    possession_date: Optional[str] = None,
    availability: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Search real estate properties with flexible filters.

    All filters are optional. Queries are constructed dynamically using SQLAlchemy
    without raw SQL strings. Results include project details and unit specifications.

    Args:
        city: Filter by project city (e.g., "Pune", "Bangalore"). Case-insensitive partial match.
        locality: Filter by project locality (e.g., "Wakad", "Whitefield"). Case-insensitive partial match.
        configuration: Filter by unit configuration (e.g., "2 BHK", "3 BHK"). Case-insensitive partial match.
        min_price: Minimum price in rupees (inclusive).
        max_price: Maximum price in rupees (inclusive).
        possession_date: Filter by possession date (exact match, e.g., "December 2026").
        availability: Filter by availability status (not yet implemented in schema).

    Returns:
        List of property dictionaries with structure:
        [
            {
                "project_name": str,
                "city": str,
                "locality": str,
                "configuration": str,
                "carpet_area": str,
                "price": str,
                "possession_date": str,
                "project_id": int,
                "unit_id": int,
                "amenities": dict or None,
                "project_status": str or None,
            },
            ...
        ]

    Raises:
        Exception: If database connection fails or query execution fails.

    Example:
        >>> results = search_properties(city="Pune", configuration="2 BHK", max_price=10000000)
        >>> for result in results:
        ...     print(f"{result['project_name']} - {result['configuration']} - ₹{result['price']}")
    """

    db = get_db_instance()
    session = db.get_session()

    try:
        logger.info(
            f"Searching properties: city={city}, locality={locality}, "
            f"config={configuration}, price_range=[{min_price}, {max_price}]"
        )

        # Initialize repositories
        project_repo = ProjectRepository(session)
        unit_repo = UnitRepository(session)

        # Search projects with city and locality filters
        projects = project_repo.search_projects(city=city, locality=locality)

        logger.debug(f"Found {len(projects)} projects matching location filters")

        results: List[Dict[str, Any]] = []

        # For each project, search units with configuration and price filters
        for project in projects:
            try:
                units = unit_repo.search_units(
                    project_id=project.id,
                    configuration=configuration,
                    min_price=min_price,
                    max_price=max_price,
                )

                logger.debug(
                    f"Project {project.id} ({project.project_name}): {len(units)} units match criteria"
                )

                # Filter units by possession_date if provided
                for unit in units:
                    # Apply possession_date filter
                    if possession_date and unit.possession_date != possession_date:
                        continue

                    # Apply availability filter (reserved for future use)
                    if availability:
                        # availability field not yet in schema
                        pass

                    # Build result object with all relevant fields
                    result = {
                        "project_name": project.project_name,
                        "city": project.city,
                        "locality": project.locality,
                        "configuration": unit.configuration,
                        "carpet_area": unit.carpet_area,
                        "price": unit.price,
                        "possession_date": unit.possession_date,
                        "project_id": project.id,
                        "unit_id": unit.id,
                        "amenities": project.amenities,
                        "project_status": project.status,
                    }

                    results.append(result)

            except Exception as e:
                logger.error(f"Error processing project {project.id}: {e}")
                continue

        logger.info(f"Search completed: returned {len(results)} results")
        return results

    except Exception as e:
        logger.error(f"Property search failed: {e}", exc_info=True)
        raise

    finally:
        session.close()


# ============= Helper Functions =============


def search_properties_by_budget(
    max_price: float,
    city: Optional[str] = None,
    configuration: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Convenience function: search properties within a budget.

    Args:
        max_price: Maximum budget in rupees.
        city: Optional city filter.
        configuration: Optional configuration filter.

    Returns:
        List of affordable properties.

    Example:
        >>> results = search_properties_by_budget(max_price=8500000, city="Pune")
    """
    return search_properties(
        city=city,
        configuration=configuration,
        max_price=max_price,
    )


def search_properties_by_city(city: str) -> List[Dict[str, Any]]:
    """Convenience function: search all properties in a city.

    Args:
        city: City name.

    Returns:
        List of properties in the city.

    Example:
        >>> results = search_properties_by_city("Pune")
    """
    return search_properties(city=city)


def search_properties_by_configuration(
    configuration: str, city: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Convenience function: search properties by configuration type.

    Args:
        configuration: Unit configuration (e.g., "2 BHK").
        city: Optional city filter.

    Returns:
        List of properties matching configuration.

    Example:
        >>> results = search_properties_by_configuration("2 BHK", city="Pune")
    """
    return search_properties(city=city, configuration=configuration)
