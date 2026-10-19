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

# fixtures

@pytest.fixture
def test_client():
    ep.app.config['TESTING'] = True
    return ep.app.test_client()

@pytest.fixture
def fake_places():
    return [{'osm_id': 1, 'properties': {'amenity': 'cafe'}}]

@pytest.fixture
def admin_headers():
    return {'who': 'admin'}

# testing generic endpoints

def test_hello():
    resp = test_client.get(ep.HELLO_EP)
    resp_json = resp.get_json()
    assert ep.HELLO_RESP in resp_json


def test_get_states():
    resp = test_client.get(ep.STATES_EP)
    resp_json = resp.get_json()
    assert ep.STATES_RESP in resp_json
    assert isinstance(resp_json[ep.STATES_RESP], dict)


def test_health():
    resp = test_client.get(ep.HEALTH_EP)
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert resp_json[ep.HEALTH_RESP] == 'ok'

# testing places endpoint

FAKE_PLACES = [{'osm_id': 1, 'properties': {'amenity': 'cafe'}}]


@patch('server.endpoints.sec.is_permitted', return_value=True)
@patch('server.endpoints.pqry.get_places', return_value=FAKE_PLACES)
def test_get_places_authorized(mock_get_places, mock_is_permitted, test_client, admin_headers, fake_places):
    resp = test_client.get(
        f'{ep.PLACES_EP}?amenity=cafe&limit=5',
        headers={admin_headers}
    )

    assert resp.status_code == OK

    resp_json = resp.get_json()
    assert resp_json[ep.PLACES_RESP] == FAKE_PLACES
    assert resp_json['count'] == 1

    mock_get_places.assert_called_with(
        category='amenity',
        place_type='cafe',
        limit=5
    )

    mock_is_permitted.assert_called_once_with(
        ep.sec.PLACES, ep.sec.READ, 'admin'
    )

@patch('server.endpoints.sec.is_permitted', return_value=False)
@patch('server.endpoints.pqry.get_places', return_value=FAKE_PLACES)
def test_get_places_forbidden(mock_get_places, mock_is_permitted, test_client, admin_headers, fake_places):
    resp = test_client.get(
        f'{ep.PLACES_EP}?amenity=cafe&limit=5',
        headers={'who': 'not_admin'}
    )

    assert resp.status_code == FORBIDDEN

    mock_get_places.assert_not_called()

    mock_is_permitted.assert_called_once_with(
        ep.sec.PLACES, ep.sec.READ, 'guest'
    )


@patch('server.endpoints.sec.is_permitted', return_value=True)
def test_get_places_bad_limit(mock_is_permitted, test_client, admin_headers):
    resp = test_client.get(
        f'{ep.PLACES_EP}?limit=abc',
        headers=admin_headers
    )

    assert resp.status_code == BAD_REQUEST

    mock_is_permitted.assert_called_once_with(
        ep.sec.PLACES, ep.sec.READ, 'admin'
    )


@patch('server.endpoints.sec.is_permitted', return_value=True)
@patch('server.endpoints.pqry.get_places', return_value=FAKE_PLACES)
def test_get_places_by_category(mock_get_places, mock_is_permitted, test_client, admin_headers):
    resp = test_client.get(
        f'{ep.PLACES_EP}?category=leisure&type=park',
        headers=admin_headers
    )

    assert resp.status_code == OK

    mock_get_places.assert_called_with(
        category='leisure',
        place_type='park',
        limit=50
    )

    mock_is_permitted.assert_called_once_with(
        ep.sec.PLACES, ep.sec.READ, 'admin'
    )


@patch('server.endpoints.sec.is_permitted', return_value=True)
@patch('server.endpoints.pqry.get_places', return_value=FAKE_PLACES)
def test_get_places_bad_category(mock_get_places, mock_is_permitted, test_client, admin_headers):
    resp = test_client.get(
        f'{ep.PLACES_EP}?category=password',
        headers=admin_headers
    )

    assert resp.status_code == BAD_REQUEST

    mock_get_places.assert_not_called()

    mock_is_permitted.assert_called_once_with(
        ep.sec.PLACES, ep.sec.READ, 'admin'
    )


@patch('server.endpoints.sec.is_permitted', return_value=False)
@patch('server.endpoints.pqry.get_places', return_value=FAKE_PLACES)
def test_get_places_forbidden(mock_get_places, mock_is_permitted, test_client, admin_headers):
    resp = test_client.get(
        f'{ep.PLACES_EP}?amenity=cafe&limit=5',
        headers=admin_headers
    )

    assert resp.status_code == FORBIDDEN

    mock_get_places.assert_not_called()

    mock_is_permitted.assert_called_once_with(
        ep.sec.PLACES, ep.sec.READ, 'guest'
    )


@patch('server.endpoints.sec.is_permitted', return_value=True)
@patch('server.endpoints.pqry.get_places', return_value=FAKE_PLACES)
def test_get_places_bad_category(mock_get_places, mock_is_permitted, test_client, admin_headers):
    resp = test_client.get(
        f'{ep.PLACES_EP}?category=password',
        headers=admin_headers
    )

    assert resp.status_code == BAD_REQUEST

    mock_get_places.assert_not_called()

    mock_is_permitted.assert_called_once_with(
        ep.sec.PLACES, ep.sec.READ, 'admin'
    )

# raises

@patch('server.endpoints.sec.is_permitted', return_value=True)
@patch('server.endpoints.pqry.get_places', side_effect=ConnectionError('db down'))
def test_get_places_db_error(mock_get_places, mock_is_permitted, test_client):
    with pytest.raises(ConnectionError):
        test_client.get(
            f'{ep.PLACES_EP}?amenity=cafe&limit=5',
            headers={'who': 'admin'}
        )

# skips

@pytest.mark.skip(reason='TODO: endpoint returns 404 when no places match')
def test_get_places_not_found(test_client):
    # not yet implemented, will need to add NOT FOUND status to places endpoints
    pass