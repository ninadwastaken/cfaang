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
    mock_get_places.assert_called_with(amenity='cafe', limit=5)


def test_get_places_bad_limit():
    resp = TEST_CLIENT.get(f'{ep.PLACES_EP}?limit=abc')
    assert resp.status_code == BAD_REQUEST
