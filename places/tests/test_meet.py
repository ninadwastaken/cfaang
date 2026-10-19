from unittest.mock import patch

import pytest

import places.meet as meet

WSP = (40.7308, -73.9973)       # Washington Square Park
BARCLAYS = (40.6826, -73.9754)  # Barclays Center


def fake_place(name, lat, lon):
    return {'geometry': {'type': 'Point', 'coordinates': [lon, lat]},
            'properties': {'name': name}}


def test_distance_same_point():
    assert meet.distance_m(WSP, WSP) == 0


def test_distance_wsp_to_barclays():
    # About 5.6 km as the crow flies.
    assert meet.distance_m(WSP, BARCLAYS) == pytest.approx(5600, rel=0.05)


def test_midpoint():
    assert meet.midpoint((40, -74), (42, -72)) == (41, -73)


def test_find_spots_searches_midpoint():
    with patch('places.query.get_places_near', return_value=[]) as near:
        result = meet.find_spots(WSP, BARCLAYS, category='amenity',
                                 place_type='cafe')
    mid = meet.midpoint(WSP, BARCLAYS)
    near.assert_called_with(mid[0], mid[1], radius=1000,
                            category='amenity', place_type='cafe',
                            limit=50)
    assert result['midpoint'] == {'lat': mid[0], 'lon': mid[1]}
    assert result['spots'] == []


def test_find_spots_adds_distances_and_sorts():
    near_wsp = fake_place('Near WSP', 40.73, -73.997)
    in_middle = fake_place('Middle', 40.7067, -73.9863)
    with patch('places.query.get_places_near',
               return_value=[near_wsp, in_middle]):
        spots = meet.find_spots(WSP, BARCLAYS)['spots']
    assert [s['name'] for s in spots] == ['Middle', 'Near WSP']
    middle = spots[0]
    assert middle['dist_1'] == round(meet.distance_m(WSP, (40.7067,
                                                           -73.9863)))
    assert middle['lat'] == 40.7067
    assert middle['lon'] == -73.9863
