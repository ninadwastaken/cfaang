from http.client import (
    BAD_REQUEST,
    FORBIDDEN,
    NOT_ACCEPTABLE,
    NOT_FOUND,
    OK,
    SERVICE_UNAVAILABLE,
)

from unittest.mock import patch

import pytest

import server.endpoints as ep

TEST_CLIENT = ep.app.test_client()


def test_hello():
    resp = TEST_CLIENT.get(ep.HELLO_EP)
    resp_json = resp.get_json()
    assert ep.HELLO_RESP in resp_json


def test_get_states():
    resp = TEST_CLIENT.get(ep.STATES_EP)
    resp_json = resp.get_json()
    assert ep.STATES_RESP in resp_json
    assert isinstance(resp_json[ep.STATES_RESP], dict)


def test_health():
    resp = TEST_CLIENT.get(ep.HEALTH_EP)
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert resp_json[ep.HEALTH_RESP] == 'ok'


FAKE_PLACES = [{'osm_id': 1, 'properties': {'amenity': 'cafe'}}]


@patch('places.query.get_places', return_value=FAKE_PLACES)
def test_get_places(mock_get_places):
    resp = TEST_CLIENT.get(f'{ep.PLACES_EP}?amenity=cafe&limit=5')
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert resp_json[ep.PLACES_RESP] == FAKE_PLACES
    assert resp_json['count'] == 1
    mock_get_places.assert_called_with(category='amenity',
                                       place_type='cafe', limit=5)


def test_get_places_bad_limit():
    resp = TEST_CLIENT.get(f'{ep.PLACES_EP}?limit=abc')
    assert resp.status_code == BAD_REQUEST


@patch('places.query.get_places', return_value=FAKE_PLACES)
def test_get_places_by_category(mock_get_places):
    resp = TEST_CLIENT.get(f'{ep.PLACES_EP}?category=leisure&type=park')
    assert resp.status_code == OK
    mock_get_places.assert_called_with(category='leisure',
                                       place_type='park', limit=50)


def test_get_places_bad_category():
    resp = TEST_CLIENT.get(f'{ep.PLACES_EP}?category=password')
    assert resp.status_code == BAD_REQUEST


FAKE_MEET = {'midpoint': {'lat': 40.7, 'lon': -73.98},
             'spots': [{'name': 'Cafe', 'dist_1': 900, 'dist_2': 1100}]}


@patch('places.meet.find_spots', return_value=FAKE_MEET)
def test_meet(mock_find):
    resp = TEST_CLIENT.get(ep.MEET_EP, query_string={
        'lat1': 40.73, 'lon1': -73.99, 'lat2': 40.68, 'lon2': -73.97,
        'type': 'cafe'})
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert resp_json['midpoint'] == FAKE_MEET['midpoint']
    assert resp_json[ep.MEET_RESP] == FAKE_MEET['spots']
    assert resp_json['count'] == 1
    mock_find.assert_called_with((40.73, -73.99), (40.68, -73.97),
                                 radius=1000.0, category='amenity',
                                 place_type='cafe', limit=50)


def test_meet_missing_person():
    resp = TEST_CLIENT.get(ep.MEET_EP,
                           query_string={'lat1': 40.73, 'lon1': -73.99})
    assert resp.status_code == BAD_REQUEST


def test_meet_bad_number():
    resp = TEST_CLIENT.get(ep.MEET_EP, query_string={
        'lat1': 'abc', 'lon1': -73.99, 'lat2': 40.68, 'lon2': -73.97})
    assert resp.status_code == BAD_REQUEST
