# Note, this is mainly for authorization, authentication is still a work in progress!
from sql_db import sql_db
from sql_db.models import *
from sql_db.transactions import get_user_permissions

import hashlib
from datetime import datetime, timezone

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
def is_permitted(endpoint_name: str, action: str, auth_header: str) -> bool:
    if action not in ACTION_MASKS:
        return False

    # first check if authenticated (i.e. has a valid api token)
    input_token = auth_header.removeprefix('Bearer ')

    input_token_hash = hashlib.sha256(input_token.encode()).hexdigest()

    api_token = ApiTokens.query.filter_by(token_hash=input_token_hash).first()

    if not api_token: # no matching token found
        return False

    if api_token.revoked_at is not None: # found token is revoked
        return False

    if api_token.expires_at <= datetime.now(timezone.utc): # found token is expired
        return False

    # second check if authorized (i.e. api token's associated user has sufficient permissions to do the action on the endpoint)
    endpoint = Endpoints.query.filter_by(endpoint_name=endpoint_name).first()

    if not endpoint:
        return False

    mask = get_user_permissions(api_token.uid, endpoint.epid)

    return bool(mask & ACTION_MASKS[action])
