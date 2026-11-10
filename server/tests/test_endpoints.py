from http.client import (
    BAD_REQUEST,
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


@patch('states.query.is_db_up', return_value=True)
def test_get_states(mock_is_db_up):
    resp = TEST_CLIENT.get(ep.STATES_EP)
    resp_json = resp.get_json()
    assert ep.STATES_RESP in resp_json
    assert isinstance(resp_json[ep.STATES_RESP], dict)


@patch('states.query.is_db_up', return_value=False)
def test_get_states_database_unavailable(mock_is_db_up):
    resp = TEST_CLIENT.get(ep.STATES_EP)
    assert resp.status_code == SERVICE_UNAVAILABLE


def test_health():
    resp = TEST_CLIENT.get(ep.HEALTH_EP)
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert resp_json[ep.HEALTH_RESP] == 'ok'


@patch('data.db_connect.connect_db')
def test_ready_when_mongo_responds(mock_connect):
    mock_connect.return_value.admin.command.return_value = {'ok': 1}
    response = TEST_CLIENT.get('/ready')
    assert response.status_code == OK
    assert response.get_json() == {'status': 'ok'}
    mock_connect.return_value.admin.command.assert_called_once_with('ping')


@pytest.mark.parametrize('error_type', [
    ep.pm.errors.ServerSelectionTimeoutError,
    ep.pm.errors.ConnectionFailure,
    ep.pm.errors.OperationFailure,
])
@patch('data.db_connect.connect_db')
def test_ready_when_mongo_unavailable(mock_connect, error_type):
    mock_connect.return_value.admin.command.side_effect = error_type(
        'private database details')
    response = TEST_CLIENT.get('/ready')
    assert response.status_code == SERVICE_UNAVAILABLE
    assert response.get_json()['message'] == ep.DATABASE_UNAVAILABLE
    assert b'private database details' not in response.data


@patch('data.db_connect.connect_db', side_effect=AssertionError(
    'Liveness must not connect to MongoDB'))
def test_health_does_not_require_mongo(mock_connect):
    response = TEST_CLIENT.get('/health')
    assert response.status_code == OK
    assert response.get_json() == {'status': 'ok'}
    mock_connect.assert_not_called()


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


FAKE_MEET = {'midpoint': {'lat': 40.7, 'lon': -73.98}, 'radius': 1000,
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
                                 place_type='cafe', limit=50,
                                 sort='fair')


def test_meet_missing_person():
    resp = TEST_CLIENT.get(ep.MEET_EP,
                           query_string={'lat1': 40.73, 'lon1': -73.99})
    assert resp.status_code == BAD_REQUEST


def test_meet_bad_number():
    resp = TEST_CLIENT.get(ep.MEET_EP, query_string={
        'lat1': 'abc', 'lon1': -73.99, 'lat2': 40.68, 'lon2': -73.97})
    assert resp.status_code == BAD_REQUEST


def test_meet_bad_sort():
    resp = TEST_CLIENT.get(ep.MEET_EP, query_string={
        'lat1': 40.73, 'lon1': -73.99, 'lat2': 40.68, 'lon2': -73.97,
        'sort': 'random'})
    assert resp.status_code == BAD_REQUEST


@patch('places.query.get_db')
def test_meet_nan_radius(mock_db):
    resp = TEST_CLIENT.get(ep.MEET_EP, query_string={
        'lat1': 40.73, 'lon1': -73.99, 'lat2': 40.68, 'lon2': -73.97,
        'radius': 'nan'})
    assert resp.status_code == BAD_REQUEST
    mock_db.assert_not_called()


def test_meet_person_out_of_range():
    resp = TEST_CLIENT.get(ep.MEET_EP, query_string={
        'lat1': 100, 'lon1': -73.99, 'lat2': -20, 'lon2': -73.97})
    assert resp.status_code == BAD_REQUEST


DATABASE_REQUESTS = [
    ('/places', 'places.query.get_places'),
    ('/meet?lat1=40.73&lon1=-73.99&lat2=40.68&lon2=-73.97',
     'places.meet.find_spots'),
]


@pytest.mark.parametrize('url,target', DATABASE_REQUESTS)
@pytest.mark.parametrize('error_type', [
    ep.pm.errors.ServerSelectionTimeoutError,
    ep.pm.errors.ConnectionFailure,
    ep.pm.errors.NetworkTimeout,
    ep.pm.errors.ExecutionTimeout,
])
def test_database_outage_returns_retryable_response(url, target, error_type):
    with patch(target, side_effect=error_type('private database details')):
        response = TEST_CLIENT.get(url)
    assert response.status_code == SERVICE_UNAVAILABLE
    assert response.get_json()['message'] == ep.DATABASE_UNAVAILABLE
    assert b'private database details' not in response.data


@pytest.mark.parametrize('url,target', DATABASE_REQUESTS)
def test_database_query_errors_are_not_reported_as_outages(url, target):
    error = ep.pm.errors.OperationFailure('Missing geospatial index', code=27)
    with patch(target, side_effect=error):
        response = TEST_CLIENT.get(url)
    assert response.status_code == 500


@pytest.mark.parametrize('url,target', DATABASE_REQUESTS)
def test_database_request_has_one_shared_time_budget(url, target):
    with patch('server.endpoints.pm.timeout') as timeout:
        def check_budget(*args, **kwargs):
            timeout.return_value.__enter__.assert_called_once()
            timeout.return_value.__exit__.assert_not_called()
            return FAKE_MEET if target.endswith('find_spots') else FAKE_PLACES

        with patch(target, side_effect=check_budget):
            response = TEST_CLIENT.get(url)
    assert response.status_code == OK
    timeout.assert_called_once_with(5)
    timeout.return_value.__exit__.assert_called_once()


def test_meet_person_outside_nyc():
    resp = TEST_CLIENT.get(ep.MEET_EP, query_string={
        'lat1': 40.73, 'lon1': -73.99, 'lat2': 41.88, 'lon2': -87.63})
    assert resp.status_code == BAD_REQUEST
    assert 'outside NYC' in resp.get_json()['message']
