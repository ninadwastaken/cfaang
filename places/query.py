"""
Query module for NYC places loaded by data/places/load.py.
"""
from data.db_connect import connect_db

PLACES_DB = 'nyc_map'
PLACES_COLLECT = 'places'
DEFAULT_LIMIT = 50
MAX_LIMIT = 500

# OSM tag keys the loader pulls places from.
CATEGORIES = ('amenity', 'leisure', 'tourism', 'historic', 'natural', 'shop')


def get_places(category=None, place_type=None, limit=DEFAULT_LIMIT):
    """
    Return a list of places, optionally filtered by category
    (like 'leisure') and type within it (like 'park').
    A category with no type returns everything in that category.
    Limit is capped at MAX_LIMIT.
    """
    if category is not None and category not in CATEGORIES:
        raise ValueError(f'Unknown category: {category}')
    if place_type and not category:
        raise ValueError('type needs a category')
    filt = {}
    if category:
        field = f'properties.{category}'
        filt[field] = place_type if place_type else {'$exists': True}
    limit = max(1, min(limit, MAX_LIMIT))
    collection = connect_db()[PLACES_DB][PLACES_COLLECT]
    return list(collection.find(filt, {'_id': 0}).limit(limit))
