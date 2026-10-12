"""
Query module for NYC places loaded by data/places/load.py.
"""
from data.db_connect import connect_db

PLACES_DB = 'nyc_map'
PLACES_COLLECT = 'places'
DEFAULT_LIMIT = 50
MAX_LIMIT = 500


def get_places(amenity=None, limit=DEFAULT_LIMIT):
    """
    Return a list of places, optionally filtered by amenity type
    (like 'cafe' or 'library'). Limit is capped at MAX_LIMIT.
    """
    filt = {}
    if amenity:
        filt['properties.amenity'] = amenity
    limit = max(1, min(limit, MAX_LIMIT))
    collection = connect_db()[PLACES_DB][PLACES_COLLECT]
    return list(collection.find(filt, {'_id': 0}).limit(limit))
