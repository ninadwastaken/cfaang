"""Places import index tests; no running MongoDB is needed."""
from unittest.mock import MagicMock, call

import pytest
from pymongo.errors import OperationFailure

from data.places.load import replace_places


@pytest.fixture
def collections():
    db = MagicMock()
    live = MagicMock()
    staging = MagicMock()
    live.index_information.return_value = {
        '_id_': {'key': [('_id', 1)]},
    }
    db.__getitem__.side_effect = (
        lambda name: live if name == 'places' else staging
    )
    return db, live, staging


@pytest.fixture
def documents():
    return [{
        'osm_id': 1,
        'type': 'Feature',
        'geometry': {
            'type': 'Point',
            'coordinates': [-73.9857, 40.7484],
        },
        'properties': {'amenity': 'cafe'},
    }]


def test_geospatial_index_created_before_replacing_places(
        collections, documents):
    db, live, staging = collections

    result = replace_places(db, documents)

    staging.assert_has_calls([
        call.insert_many(documents),
        call.create_index([('geometry', '2dsphere')]),
        call.rename('places', dropTarget=True),
    ])
    assert result is staging.insert_many.return_value
    live.create_index.assert_not_called()


def test_index_failure_does_not_replace_live_places(collections, documents):
    db, live, staging = collections
    staging.create_index.side_effect = OperationFailure('Index build failed')

    with pytest.raises(OperationFailure, match='Index build failed'):
        replace_places(db, documents)

    staging.rename.assert_not_called()
    live.drop.assert_not_called()
    staging_name = db.__getitem__.call_args_list[0].args[0]
    assert staging_name.startswith('places_import_')
    db.drop_collection.assert_called_once_with(staging_name)
