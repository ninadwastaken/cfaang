"""Database selection and availability tests using a mocked MongoDB client."""
from unittest.mock import MagicMock

import pytest

from data import db_connect as dbc


def test_ensure_connection_initializes_before_call_and_preserves_metadata(mongo):
    @dbc.ensure_connection
    def operation(value, *, suffix):
        """An operation requiring a client."""
        assert dbc.client is not None
        return value + suffix

    assert dbc.client is None
    assert operation('first', suffix=' call') == 'first call'
    assert operation('second', suffix=' call') == 'second call'
    assert operation.__name__ == 'operation'
    assert operation.__doc__ == 'An operation requiring a client.'
    mongo.assert_called_once()


def test_ensure_connection_does_not_run_operation_when_connection_fails(mongo):
    error = dbc.pm.errors.ConnectionFailure('Cannot initialize client')
    mongo.side_effect = error
    called = []

    @dbc.ensure_connection
    def operation():
        called.append(True)

    with pytest.raises(dbc.pm.errors.ConnectionFailure) as caught:
        operation()

    assert caught.value is error
    assert called == []


def test_is_db_up_pings_mongo(mongo):
    mongo.return_value.admin.command.return_value = {'ok': 1}

    assert dbc.is_db_up() is True
    mongo.return_value.admin.command.assert_called_once_with('ping')


@pytest.mark.parametrize('error', [
    dbc.pm.errors.ServerSelectionTimeoutError('MongoDB is unavailable'),
    dbc.pm.errors.ConnectionFailure('Connection lost'),
    dbc.pm.errors.OperationFailure('Ping failed'),
])
def test_is_db_up_returns_false_when_ping_fails(mongo, error):
    mongo.return_value.admin.command.side_effect = error

    assert dbc.is_db_up() is False
    mongo.return_value.admin.command.assert_called_once_with('ping')


@pytest.fixture
def mongo(monkeypatch):
    factory = MagicMock()
    monkeypatch.setattr(dbc.pm, 'MongoClient', factory)
    monkeypatch.setattr(dbc, 'client', None)
    monkeypatch.setenv('CLOUD_MONGO', '0')
    monkeypatch.setenv('MONGO_URI', 'mongodb://test-host:27017/')
    monkeypatch.delenv('MONGO_DB', raising=False)
    return factory


@pytest.mark.parametrize('operation,args', [
    ('create', ('places', {'osm_id': 1})),
    ('read_one', ('places', {'osm_id': 1})),
    ('delete', ('places', {'osm_id': 1})),
    ('update', ('places', {'osm_id': 1}, {'name': 'Cafe'})),
    ('read', ('places',)),
    ('read_dict', ('places', 'osm_id')),
    ('fetch_all_as_dict', ('osm_id', 'places')),
])
@pytest.mark.parametrize('configured_db', [None, 'test_places'])
def test_helpers_connect_and_select_database(
        mongo, monkeypatch, operation, args, configured_db):
    if configured_db is not None:
        monkeypatch.setenv('MONGO_DB', configured_db)
    helper = getattr(dbc, operation)
    helper(*args)
    mongo.return_value.__getitem__.assert_called_with(
        configured_db or 'nyc_map',
    )
    helper(*args, db='explicit_db')
    mongo.return_value.__getitem__.assert_called_with('explicit_db')
    mongo.assert_called_once_with('mongodb://test-host:27017/')


def test_get_db_uses_same_database_as_helpers(mongo, monkeypatch):
    monkeypatch.setenv('MONGO_DB', 'test_places')
    database = dbc.get_db()
    dbc.create('places', {'osm_id': 1})
    database['places'].insert_one.assert_called_once_with({'osm_id': 1})
    mongo.return_value.__getitem__.assert_called_with('test_places')
    mongo.assert_called_once()
