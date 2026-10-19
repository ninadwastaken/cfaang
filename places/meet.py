"""
Logic for finding a place to meet between two people.
"""
from math import asin, cos, radians, sin, sqrt

import places.query as pqry

EARTH_RADIUS_M = 6371000


def distance_m(point_a, point_b):
    """
    Straight-line (haversine) distance in meters between two
    (lat, lon) points.
    """
    lat1, lon1 = map(radians, point_a)
    lat2, lon2 = map(radians, point_b)
    a = (sin((lat2 - lat1) / 2) ** 2
         + cos(lat1) * cos(lat2) * sin((lon2 - lon1) / 2) ** 2)
    return 2 * EARTH_RADIUS_M * asin(sqrt(a))


def midpoint(point_a, point_b):
    """
    Return the (lat, lon) halfway between two points.
    A plain average is close enough at NYC distances.
    """
    return ((point_a[0] + point_b[0]) / 2, (point_a[1] + point_b[1]) / 2)


def place_point(place):
    """
    GeoJSON stores [lon, lat], so flip it to (lat, lon).
    """
    lon, lat = place['geometry']['coordinates']
    return lat, lon


def find_spots(person_1, person_2, radius=pqry.DEFAULT_RADIUS_M,
               category=None, place_type=None, limit=pqry.DEFAULT_LIMIT):
    """
    Find places near the midpoint of two people.
    Each spot gets dist_1 and dist_2, how far each person is from it
    in meters. Spots come back closest to the midpoint first.
    """
    mid = midpoint(person_1, person_2)
    places = pqry.get_places_near(mid[0], mid[1], radius=radius,
                                  category=category,
                                  place_type=place_type, limit=limit)
    spots = []
    for place in places:
        point = place_point(place)
        spot = {
            'name': place.get('properties', {}).get('name'),
            'lat': point[0],
            'lon': point[1],
            'dist_1': round(distance_m(person_1, point)),
            'dist_2': round(distance_m(person_2, point)),
            'dist_mid': round(distance_m(mid, point)),
            'properties': place.get('properties', {}),
        }
        spots.append(spot)
    spots.sort(key=lambda s: s['dist_mid'])
    return {'midpoint': {'lat': mid[0], 'lon': mid[1]}, 'spots': spots}
