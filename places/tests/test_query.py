from unittest.mock import MagicMock, patch
import pytest
import places.query as qry


def fake_db(docs):
    """
    Build a fake Mongo client whose find().limit() returns docs.
    """
    collection = MagicMock()
    collection.find.return_value.limit.return_value = docs
    client = MagicMock()
    client.__getitem__.return_value.__getitem__.return_value = collection
    return client, collection


def test_get_places_filters_by_amenity():
    client, collection = fake_db([{'osm_id': 1}])
    with patch('places.query.connect_db', return_value=client):
        result = qry.get_places(category='amenity', place_type='cafe',
                                limit=10)
    assert result == [{'osm_id': 1}]
    collection.find.assert_called_with(
        {'properties.amenity': 'cafe'}, {'_id': 0})
    collection.find.return_value.limit.assert_called_with(10)


def test_get_places_no_filter():
    client, collection = fake_db([])
    with patch('places.query.connect_db', return_value=client):
        qry.get_places()
    collection.find.assert_called_with({}, {'_id': 0})


def test_get_places_caps_limit():
    client, collection = fake_db([])
    with patch('places.query.connect_db', return_value=client):
        qry.get_places(limit=99999)
    collection.find.return_value.limit.assert_called_with(qry.MAX_LIMIT)


def test_get_places_category_only():
    client, collection = fake_db([])
    with patch('places.query.connect_db', return_value=client):
        qry.get_places(category='tourism')
    collection.find.assert_called_with(
        {'properties.tourism': {'$exists': True}}, {'_id': 0})


def test_get_places_leisure_park():
    client, collection = fake_db([])
    with patch('places.query.connect_db', return_value=client):
        qry.get_places(category='leisure', place_type='park')
    collection.find.assert_called_with(
        {'properties.leisure': 'park'}, {'_id': 0})


def test_get_places_bad_category():
    with pytest.raises(ValueError):
        qry.get_places(category='password')


def test_get_places_type_without_category():
    with pytest.raises(ValueError):
        qry.get_places(place_type='park')
