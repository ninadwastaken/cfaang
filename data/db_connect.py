"""
All interaction with MongoDB should be through this file!
We may be required to use a new database at any point.
"""
import os

import pymongo as pm

LOCAL = "0"
CLOUD = "1"

DEFAULT_DB = 'nyc_map'

client = None

MONGO_ID = '_id'


def connect_db():
    """
    This provides a uniform way to connect to the DB across all uses.
    Returns a mongo client object... maybe we shouldn't?
    Also set global client variable.
    We should probably either return a client OR set a
    client global.
    """
    global client
    if client is None:  # not connected yet!
        print('Setting client because it is None.')
        if os.environ.get('CLOUD_MONGO', LOCAL) == CLOUD:
            password = os.environ.get('MONGO_PASSWD')
            if not password:
                raise ValueError('You must set your password '
                                 + 'to use Mongo in the cloud.')
            print('Connecting to Mongo in the cloud.')
            client = pm.MongoClient(f'mongodb+srv://gcallah:{password}'
                                    + '@koukoumongo1.yud9b.mongodb.net/'
                                    + '?retryWrites=true&w=majority')
        else:
            print("Connecting to Mongo locally.")
            client = pm.MongoClient(
                os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
            )

    return client


def get_db(db=None):
    """Connect as needed and select the configured or explicitly named DB."""
    name = db if db is not None else os.environ.get('MONGO_DB', DEFAULT_DB)
    return connect_db()[name]


def is_db_up():
    """
    Returns True if the DB is up and running.
    """
    try:
        with pm.timeout(5):
            connect_db().admin.command('ping')
        return True
    except pm.errors.PyMongoError:
        return False


def convert_mongo_id(doc: dict):
    if MONGO_ID in doc:
        # Convert mongo ID to a string so it works as JSON
        doc[MONGO_ID] = str(doc[MONGO_ID])


def create(collection, doc, db=None):
    """
    Insert a single doc into collection.
    """
    print(f'{db=}')
    return get_db(db)[collection].insert_one(doc)


def read_one(collection, filt, db=None):
    """
    Find with a filter and return on the first doc found.
    Return None if not found.
    """
    for doc in get_db(db)[collection].find(filt):
        convert_mongo_id(doc)
        return doc


def delete(collection: str, filt: dict, db=None):
    """
    Find with a filter and return on the first doc found.
    """
    print(f'{filt=}')
    del_result = get_db(db)[collection].delete_one(filt)
    return del_result.deleted_count


def update(collection, filters, update_dict, db=None):
    return get_db(db)[collection].update_one(filters, {'$set': update_dict})


def read(collection, db=None, no_id=True) -> list:
    """
    Returns a list from the db.
    """
    ret = []
    for doc in get_db(db)[collection].find():
        if no_id:
            del doc[MONGO_ID]
        else:
            convert_mongo_id(doc)
        ret.append(doc)
    return ret


def read_dict(collection, key, db=None, no_id=True) -> dict:
    recs = read(collection, db=db, no_id=no_id)
    recs_as_dict = {}
    for rec in recs:
        recs_as_dict[rec[key]] = rec
    return recs_as_dict


def fetch_all_as_dict(key, collection, db=None):
    ret = {}
    for doc in get_db(db)[collection].find():
        del doc[MONGO_ID]
        ret[doc[key]] = doc
    return ret
