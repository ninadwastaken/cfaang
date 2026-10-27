# Note, this is mainly for authorization, authentication is still a work in progress!

import os
from functools import wraps

# set to 0 to enforce authorization, 1 to bypass authorization
# ALWAYS SET TO 0 IN PRODUCTION!
AUTH_BYPASS = os.getenv("AUTH_BYPASS") == "1"

# import data.db_connect as dbc

"""
Our record format to meet our requirements (see security.md) will be:

{
    feature_name1: {
        create: {
            user_list: [],
            checks: {
                login: True,
                ip_address: False,
                dual_factor: False,
                # etc.
            },
        },
        read: {
            user_list: [],
            checks: {
                login: True,
                ip_address: False,
                dual_factor: False,
                # etc.
            },
        },
        update: {
            user_list: [],
            checks: {
                login: True,
                ip_address: False,
                dual_factor: False,
                # etc.
            },
        },
        delete: {
            user_list: [],
            checks: {
                login: True,
                ip_address: False,
                dual_factor: False,
                # etc.
            },
        },
    },
    feature_name2: # etc.
}
"""

# COLLECT_NAME = 'security'
CREATE = 'create'
READ = 'read'
UPDATE = 'update'
DELETE = 'delete'
USER_LIST = 'user_list'
CHECKS = 'checks'
LOGIN = 'login'

# Features:
PLACES = 'places'
MEET = 'meet'
ENDPOINTS = 'endpoints'

security_recs = None
# These will come from the DB soon:
temp_recs = {
    PLACES: {
        READ: {
            USER_LIST: ['admin'],
            CHECKS: {
                LOGIN: True,
            },
        },
    },
    MEET: {
        READ: {
            USER_LIST: ['admin'],
            CHECKS: {
                LOGIN: True,
            },
        },
    },
    ENDPOINTS: {
        READ: {
            USER_LIST: ['admin'],
            CHECKS: {
                LOGIN: True,
            },
        },
    },
}


def read() -> dict:
    global security_recs
    # dbc.read()
    security_recs = temp_recs
    return security_recs


def needs_recs(fn):
    """
    Should be used to decorate any function that directly accesses sec recs.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        global security_recs
        if not security_recs:
            security_recs = read()
        return fn(*args, **kwargs)
    return wrapper


@needs_recs
def read_feature(feature_name: str) -> dict:
    if feature_name in security_recs:
        return security_recs[feature_name]
    else:
        return None


@needs_recs
def is_permitted(feature_name: str, action: str, user: str, **kwargs) -> bool:
    if AUTH_BYPASS:
        return True

    rules = read_feature(feature_name)

    if not rules:
        return False

    user_exists = user in rules.get(action, {}).get(USER_LIST, [])

    return user_exists