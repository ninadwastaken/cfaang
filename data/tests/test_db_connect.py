"""Database selection tests; no running MongoDB is needed."""
from unittest.mock import MagicMock

import pytest

from data import db_connect as dbc


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
