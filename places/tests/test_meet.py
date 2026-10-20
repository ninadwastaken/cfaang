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
    # Nothing found, so it widens all the way to the max radius.
    near.assert_called_with(mid[0], mid[1], radius=10000,
                            category='amenity', place_type='cafe',
                            limit=50)
    assert result['midpoint'] == {'lat': mid[0], 'lon': mid[1]}
    assert result['spots'] == []


def test_find_spots_adds_distances_and_sorts():
    near_wsp = fake_place('Near WSP', 40.73, -73.997)
    in_middle = fake_place('Middle', 40.7067, -73.9863)
    with patch('places.query.get_places_near',
               return_value=[near_wsp, in_middle]):
        spots = meet.find_spots(WSP, BARCLAYS, sort='closest')['spots']
    assert [s['name'] for s in spots] == ['Middle', 'Near WSP']
    middle = spots[0]
    assert middle['dist_1'] == round(meet.distance_m(WSP, (40.7067,
                                                           -73.9863)))
    assert middle['lat'] == 40.7067
    assert middle['lon'] == -73.9863


def test_fairness_gap():
    assert meet.fairness_gap({'dist_1': 1200, 'dist_2': 800}) == 400
    assert meet.fairness_gap({'dist_1': 500, 'dist_2': 500}) == 0


def test_find_spots_fair_sort():
    # One spot is right at the midpoint, the other is about 1 km north,
    # closer to person 1. The fair sort should put the even one first.
    even = fake_place('Even', 40.7067, -73.9863)
    lopsided = fake_place('Lopsided', 40.7067 + 0.009, -73.9863)
    with patch('places.query.get_places_near',
               return_value=[lopsided, even] * 3):
        spots = meet.find_spots(WSP, BARCLAYS)['spots']
    assert spots[0]['name'] == 'Even'
    assert spots[0]['gap'] < spots[-1]['gap']


def test_find_spots_fair_sort_prefers_near_over_far_even():
    # Far is about 7.5 km from both people (gap ~1 m). Near is next to
    # the midpoint, about 2.8 km from each (gap ~80 m). Near should win.
    near = fake_place('Near', 40.7071, -73.9864)
    far = fake_place('Far', 40.6862, -74.0648)
    with patch('places.query.get_places_near',
               return_value=[far, near] * 3):
        spots = meet.find_spots(WSP, BARCLAYS)['spots']
    assert spots[0]['name'] == 'Near'
    assert spots[0]['gap'] > spots[-1]['gap']


def test_find_spots_widens_when_few_results():
    one = [fake_place('Only one', 40.7067, -73.9863)]
    with patch('places.query.get_places_near', return_value=one) as near:
        result = meet.find_spots(WSP, BARCLAYS, radius=1000)
    radii = [call.kwargs['radius'] for call in near.call_args_list]
    assert radii == [1000, 2000, 4000, 8000, 10000]
    assert result['radius'] == 10000


def test_find_spots_no_widen_when_enough():
    five = [fake_place(f'Spot {n}', 40.7067, -73.9863) for n in range(5)]
    with patch('places.query.get_places_near', return_value=five) as near:
        result = meet.find_spots(WSP, BARCLAYS, radius=1000)
    assert near.call_count == 1
    assert result['radius'] == 1000


def test_find_spots_bad_sort():
    with pytest.raises(ValueError):
        meet.find_spots(WSP, BARCLAYS, sort='random')
