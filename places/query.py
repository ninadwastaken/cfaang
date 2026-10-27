"""
Query module for NYC places loaded by data/places/load.py.
"""
from data.db_connect import get_db

PLACES_COLLECT = 'places'
DEFAULT_LIMIT = 50
MAX_LIMIT = 500

# OSM tag keys the loader pulls places from.
CATEGORIES = ('amenity', 'leisure', 'tourism', 'historic', 'natural', 'shop')

DEFAULT_RADIUS_M = 1000
MAX_RADIUS_M = 10000


def build_filter(category=None, place_type=None):
    """
    Build the Mongo filter for a category and optional type.
    """
    if category is not None and category not in CATEGORIES:
        raise ValueError(f'Unknown category: {category}')
    if place_type and not category:
        raise ValueError('type needs a category')
    filt = {}
    if category:
        field = f'properties.{category}'
        filt[field] = place_type if place_type else {'$exists': True}
    return filt


def get_places(category=None, place_type=None, limit=DEFAULT_LIMIT):
    """
    Return a list of places, optionally filtered by category
    (like 'leisure') and type within it (like 'park').
    A category with no type returns everything in that category.
    Limit is capped at MAX_LIMIT.
    """
    filt = build_filter(category, place_type)
    limit = max(1, min(limit, MAX_LIMIT))
    collection = get_db()[PLACES_COLLECT]
    return list(collection.find(filt, {'_id': 0}).limit(limit))


def get_places_near(lat, lon, radius=DEFAULT_RADIUS_M, category=None,
                    place_type=None, limit=DEFAULT_LIMIT):
    """
    Return places within radius meters of (lat, lon).
    Works with the same category and type filters as get_places.
    Radius is capped at MAX_RADIUS_M.
    """
    if not -90 <= lat <= 90 or not -180 <= lon <= 180:
        raise ValueError('lat or lon out of range')
    # Written this way so NaN fails too.
    if not radius > 0:
        raise ValueError('radius must be positive')
    radius = min(radius, MAX_RADIUS_M)
    filt = build_filter(category, place_type)
    # GeoJSON points are stored as [lon, lat].
    # $nearSphere returns closest first, so limit keeps the nearest places.
    filt['geometry'] = {
        '$nearSphere': {
            '$geometry': {'type': 'Point', 'coordinates': [lon, lat]},
            '$maxDistance': radius,
        }
    }
    limit = max(1, min(limit, MAX_LIMIT))
    collection = get_db()[PLACES_COLLECT]
    return list(collection.find(filt, {'_id': 0}).limit(limit))
