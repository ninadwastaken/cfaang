from unittest.mock import MagicMock, patch
import pytest
import places.query as qry


def fake_db(docs):
    """
    Build a fake Mongo database whose find().limit() returns docs.
    """
    collection = MagicMock()
    collection.find.return_value.limit.return_value = docs
    database = MagicMock()
    database.__getitem__.return_value = collection
    return database, collection


def test_get_places_filters_by_amenity():
    database, collection = fake_db([{'osm_id': 1}])
    with patch('places.query.get_db', return_value=database):
        result = qry.get_places(category='amenity', place_type='cafe',
                                limit=10)
    assert result == [{'osm_id': 1}]
    collection.find.assert_called_with(
        {'properties.amenity': 'cafe'}, {'_id': 0})
    collection.find.return_value.limit.assert_called_with(10)


def test_get_places_no_filter():
    database, collection = fake_db([])
    with patch('places.query.get_db', return_value=database):
        qry.get_places()
    collection.find.assert_called_with({}, {'_id': 0})


def test_get_places_caps_limit():
    database, collection = fake_db([])
    with patch('places.query.get_db', return_value=database):
        qry.get_places(limit=99999)
    collection.find.return_value.limit.assert_called_with(qry.MAX_LIMIT)


def test_get_places_category_only():
    database, collection = fake_db([])
    with patch('places.query.get_db', return_value=database):
        qry.get_places(category='tourism')
    collection.find.assert_called_with(
        {'properties.tourism': {'$exists': True}}, {'_id': 0})


def test_get_places_leisure_park():
    database, collection = fake_db([])
    with patch('places.query.get_db', return_value=database):
        qry.get_places(category='leisure', place_type='park')
    collection.find.assert_called_with(
        {'properties.leisure': 'park'}, {'_id': 0})


def test_get_places_bad_category():
    with pytest.raises(ValueError):
        qry.get_places(category='password')


def test_get_places_type_without_category():
    with pytest.raises(ValueError):
        qry.get_places(place_type='park')


def test_get_places_uses_configured_database(monkeypatch):
    from data import db_connect as dbc

    monkeypatch.setenv('MONGO_DB', 'test_places')
    database, collection = fake_db([{'osm_id': 1}])
    client = MagicMock()
    client.__getitem__.return_value = database
    monkeypatch.setattr(dbc, 'client', client)

    assert qry.get_places() == [{'osm_id': 1}]
    client.__getitem__.assert_called_once_with('test_places')
    database.__getitem__.assert_called_once_with('places')


def test_get_places_near():
    database, collection = fake_db([{'osm_id': 1}])
    with patch('places.query.get_db', return_value=database):
        result = qry.get_places_near(40.73, -73.99, radius=500)
    assert result == [{'osm_id': 1}]
    filt = collection.find.call_args[0][0]
    center, radians = filt['geometry']['$geoWithin']['$centerSphere']
    assert center == [-73.99, 40.73]
    assert radians == 500 / qry.EARTH_RADIUS_M


def test_get_places_near_with_category():
    database, collection = fake_db([])
    with patch('places.query.get_db', return_value=database):
        qry.get_places_near(40.73, -73.99, category='amenity',
                            place_type='cafe')
    filt = collection.find.call_args[0][0]
    assert filt['properties.amenity'] == 'cafe'
    assert 'geometry' in filt


def test_get_places_near_caps_radius():
    database, collection = fake_db([])
    with patch('places.query.get_db', return_value=database):
        qry.get_places_near(40.73, -73.99, radius=999999)
    filt = collection.find.call_args[0][0]
    radians = filt['geometry']['$geoWithin']['$centerSphere'][1]
    assert radians == qry.MAX_RADIUS_M / qry.EARTH_RADIUS_M


def test_get_places_near_bad_coords():
    with pytest.raises(ValueError):
        qry.get_places_near(200, -73.99)


def test_get_places_near_bad_radius():
    with pytest.raises(ValueError):
        qry.get_places_near(40.73, -73.99, radius=0)


def test_get_places_near_nan_radius():
    with pytest.raises(ValueError):
        qry.get_places_near(40.73, -73.99, radius=float('nan'))
