"""
Logic for finding a place to meet between two people.
"""
from math import asin, cos, radians, sin, sqrt

import places.query as pqry

EARTH_RADIUS_M = 6371000
SORTS = ('fair', 'closest')
MIN_SPOTS = 5
WIDEN_FACTOR = 2
SAME_PLACE_M = 200


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


def fairness_gap(spot):
    """
    How much farther one person goes than the other, in meters.
    0 means both people travel the same distance.
    """
    return abs(spot['dist_1'] - spot['dist_2'])


def search_widening(mid, radius, category, place_type, limit):
    """
    Search around the midpoint. If fewer than MIN_SPOTS come back,
    double the radius and try again, up to MAX_RADIUS_M.
    Returns the places and the radius that was actually used.
    """
    radius = min(radius, pqry.MAX_RADIUS_M)
    while True:
        places = pqry.get_places_near(mid[0], mid[1], radius=radius,
                                      category=category,
                                      place_type=place_type, limit=limit)
        if len(places) >= MIN_SPOTS or radius >= pqry.MAX_RADIUS_M:
            return places, radius
        radius = min(radius * WIDEN_FACTOR, pqry.MAX_RADIUS_M)


def street_address(spot):
    """
    Return (house number, street) from the OSM tags, or None if
    either is missing.
    """
    props = spot['properties']
    number = props.get('addr:housenumber')
    street = props.get('addr:street')
    if not number or not street:
        return None
    return number.strip().lower(), street.strip().lower()


def same_place(spot_a, spot_b):
    """
    True if two spots look like one place listed twice: the same name,
    within SAME_PLACE_M meters, and one is a point while the other is
    an area. Two points with the same name, like neighboring branches
    of a chain, are separate places. So are spots with different
    street addresses.
    """
    def name(spot):
        return (spot['name'] or '').strip().lower()

    if name(spot_a) != name(spot_b):
        return False
    if spot_a['osm_type'] == spot_b['osm_type']:
        return False
    addr_a, addr_b = street_address(spot_a), street_address(spot_b)
    if addr_a and addr_b and addr_a != addr_b:
        return False
    return distance_m((spot_a['lat'], spot_a['lon']),
                      (spot_b['lat'], spot_b['lon'])) < SAME_PLACE_M


def drop_duplicates(spots):
    """
    OSM can list one place twice, like a park as a point and an area.
    Keep the first spot and drop any later one that same_place says
    is the same.
    """
    kept = []
    for spot in spots:
        if not any(same_place(spot, k) for k in kept):
            kept.append(spot)
    return kept


def find_spots(person_1, person_2, radius=pqry.DEFAULT_RADIUS_M,
               category=None, place_type=None, limit=pqry.DEFAULT_LIMIT,
               sort='fair'):
    """
    Find places near the midpoint of two people.
    Each spot gets dist_1 and dist_2, how far each person is from it
    in meters, plus gap, the difference between the two.
    sort='fair' puts the spots with the shortest longer trip first,
    so nobody gets stuck with a long trip.
    sort='closest' puts the spots closest to the midpoint first.
    If there are only a few spots nearby, the search widens.
    """
    if sort not in SORTS:
        raise ValueError(f'sort must be one of: {", ".join(SORTS)}')
    mid = midpoint(person_1, person_2)
    places, radius_used = search_widening(mid, radius, category,
                                          place_type, limit)
    spots = []
    for place in places:
        point = place_point(place)
        spot = {
            'name': place.get('properties', {}).get('name'),
            'osm_type': place.get('osm_type'),
            'lat': point[0],
            'lon': point[1],
            'dist_1': round(distance_m(person_1, point)),
            'dist_2': round(distance_m(person_2, point)),
            'dist_mid': round(distance_m(mid, point)),
            'properties': place.get('properties', {}),
        }
        spot['gap'] = fairness_gap(spot)
        spots.append(spot)
    if sort == 'fair':
        # Sorting on the gap alone would favor far-off spots that happen
        # to be equally far from both people, so sort on the longer trip
        # and break ties by the gap.
        spots.sort(key=lambda s: (max(s['dist_1'], s['dist_2']), s['gap']))
    else:
        spots.sort(key=lambda s: s['dist_mid'])
    spots = drop_duplicates(spots)
    return {'midpoint': {'lat': mid[0], 'lon': mid[1]},
            'radius': radius_used, 'spots': spots}
