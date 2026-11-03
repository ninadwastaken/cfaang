# Note, this is mainly for authorization, authentication is still a work in progress!
from sql_db import sql_db
from sql_db.models import *
from sql_db.transactions import get_user_permissions

# Actions
CREATE = 'CREATE'
READ = 'READ'
UPDATE = 'UPDATE'
DELETE = 'DELETE'

# Action masks
ACTION_MASKS = {
    CREATE: 0b1000,
    READ: 0b0100,
    UPDATE: 0b0010,
    DELETE: 0b0001,
}

# Endpoints
PLACES = 'places'
MEET = 'meet'
ENDPOINTS = 'endpoints'

# TODO: add ways to reduce lookups, maybe caching?
def is_permitted(endpoint_name: str, action: str, username: str) -> bool:
    if action not in ACTION_MASKS:
        return False

    user = Users.query.filter_by(username=username).first()
    endpoint = Endpoints.query.filter_by(endpoint_name=endpoint_name).first()

    if not user:
        return False
    elif not endpoint:
        return False

    mask = get_user_permissions(user.uid, endpoint.epid)

    return bool(mask & ACTION_MASKS[action])

    

    
    