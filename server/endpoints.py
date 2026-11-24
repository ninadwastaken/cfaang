"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""
# import os # used to get environment variables
import hashlib
import secrets

from datetime import datetime, timezone, timedelta

from argon2.exceptions import VerificationError
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from contextlib import contextmanager
from http import HTTPStatus

from flask import Flask, request
from flask_restx import Resource, Api, fields  # Namespace
from flask_cors import CORS
import pymongo as pm

from sql_db import init_db, sql_db, ph
from sql_db.models import Users, ApiTokens
from sql_db.transactions import create_new_user

import werkzeug.exceptions as wz

import states.query as sqry
import places.query as pqry
import security.security as sec
import places.meet as meet
import data.db_connect as dbc

app = Flask(__name__)

# rate limiting settings
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],
    storage_uri="memory://",
    headers_enabled=True
)

limiter.init_app(app)

init_db(app)
CORS(app)
api = Api(app)

ENDPOINT_EP = '/endpoints'
ENDPOINT_RESP = 'Available endpoints'
HELLO_EP = '/hello'
HELLO_RESP = 'hello'
STATES_EP = '/states'
STATES_RESP = 'States:'
MESSAGE = 'Message'
PLACES_EP = '/places'
PLACES_RESP = 'Places'
MEET_EP = '/meet'
MEET_RESP = 'Spots'
HEALTH_EP = '/health'
HEALTH_RESP = 'status'
REGISTER_EP = '/register'
TOKEN_EP = '/auth/token'
READY_EP = '/ready'
DATABASE_TIMEOUT_SECONDS = 5
DATABASE_UNAVAILABLE = 'Database is temporarily unavailable. Please try again.'

USERNAME_PASSWORD_MODEL = api.model('UserRegistration', {
    'username': fields.String(
        required=True,
        min_length=3,
        max_length=64
    ),
    'password': fields.String(
        required=True,
        min_length=12,
        max_length=128
    )
})

@contextmanager
def database_request():
    """Share one database time budget across all queries in a request."""
    try:
        with pm.timeout(DATABASE_TIMEOUT_SECONDS):
            yield
    except pm.errors.PyMongoError as err:
        if not (isinstance(err, pm.errors.ConnectionFailure) or err.timeout):
            raise
        app.logger.exception('Database request unavailable')
        raise wz.ServiceUnavailable(DATABASE_UNAVAILABLE) from None

# already have a health endpoint, this is redundant - Will
# @api.route(HELLO_EP)
# class HelloWorld(Resource):
#     """
#     The purpose of the HelloWorld class is to have a simple test to see if the
#     app is working at all.
#     """
#     def get(self):
#         """
#         A trivial endpoint to see if the server is running.
#         """
#         return {HELLO_RESP: 'world'}


@api.route(ENDPOINT_EP)
class Endpoints(Resource):
    """
    This class will serve as live, fetchable documentation of what endpoints
    are available in the system.
    """
    def get(self):
        """
        The `get()` method will return a sorted list of available endpoints.
        """

        if not sec.is_permitted(sec.ENDPOINTS, sec.READ, request.headers.get('Authorization', '')):
            raise wz.Forbidden('Not authorized')
        
        endpoints = sorted(rule.rule for rule in api.app.url_map.iter_rules())
        return {"Available endpoints": endpoints}


# This looks like it's unused - Will
# @api.route(STATES_EP)
# class States(Resource):
#     """
#     The get method will return a list of all states in the database.
#     """
#     @api.response(HTTPStatus.OK.value, 'Success')
#     @api.response(HTTPStatus.SERVICE_UNAVAILABLE.value, 'Service Unavailable')
#     def get(self):
#         """
#         The get method will return a list of all states in the database.
#         """
        
#         states = sqry.get_states()
#         if states is None:
#             raise wz.ServiceUnavailable('Database may be down.')
#         return {STATES_RESP: states}


@api.route(PLACES_EP)
class Places(Resource):
    """
    Get NYC places, optionally filtered by category and type.
    """
    @api.doc(params={
        'category': 'One of: amenity, leisure, tourism, historic, '
                    'natural, shop',
        'type': 'Type within the category, like park or museum',
        'amenity': 'Shortcut for category=amenity&type=<value>',
        'limit': 'Max results to return (default 50, max 500)',
    })
    @api.response(HTTPStatus.OK.value, 'Success')
    @api.response(HTTPStatus.BAD_REQUEST.value, 'Bad query parameters')
    @api.response(HTTPStatus.SERVICE_UNAVAILABLE.value, 'Database unavailable')
    @limiter.limit("30 per minute")
    def get(self):
        """
        Return NYC places, like /places?category=leisure&type=park.
        """

        # check if user is authorized to read places
        if not sec.is_permitted(sec.PLACES, sec.READ, request.headers.get('Authorization', '')):
            raise wz.Forbidden('Not authorized')

        category = request.args.get('category')
        place_type = request.args.get('type')
        amenity = request.args.get('amenity')
        if amenity:
            category, place_type = 'amenity', amenity
        try:
            limit = int(request.args.get('limit', pqry.DEFAULT_LIMIT))
        except ValueError:
            raise wz.BadRequest('limit must be a number.')
        try:
            with database_request():
                places = pqry.get_places(category=category,
                                         place_type=place_type, limit=limit)
        except ValueError as err:
            raise wz.BadRequest(str(err))
        return {PLACES_RESP: places, 'count': len(places)}


@api.route(MEET_EP)
class Meet(Resource):
    """
    Find places to meet between two people.
    """
    @api.doc(params={
        'lat1': 'Latitude of person 1 (required)',
        'lon1': 'Longitude of person 1 (required)',
        'lat2': 'Latitude of person 2 (required)',
        'lon2': 'Longitude of person 2 (required)',
        'radius': 'Search radius around the midpoint in meters '
                  '(default 1000, max 10000)',
        'category': 'One of: amenity, leisure, tourism, historic, '
                    'natural, shop',
        'type': 'Type within the category, like cafe or park',
        'limit': 'Max results to return (default 50, max 500)',
        'sort': 'fair (shortest longer trip first, default) or closest '
                '(closest to the midpoint first)',
        'max_walk': 'Skip spots where either person walks more than this '
                    'many minutes (optional)',
    })
    @api.response(HTTPStatus.OK.value, 'Success')
    @api.response(HTTPStatus.BAD_REQUEST.value, 'Bad query parameters')
    @api.response(HTTPStatus.SERVICE_UNAVAILABLE.value, 'Database unavailable')
    @limiter.limit("30 per minute")
    def get(self):
        """
        Return spots near the midpoint of two people, like
        /meet?lat1=40.73&lon1=-73.99&lat2=40.68&lon2=-73.97&type=cafe.
        """
        # check if user is authorized to read meet
        if not sec.is_permitted(sec.MEET, sec.READ, request.headers.get('Authorization', '')):
            raise wz.Forbidden('Not authorized')

        try:
            lat1 = float(request.args['lat1'])
            lon1 = float(request.args['lon1'])
            lat2 = float(request.args['lat2'])
            lon2 = float(request.args['lon2'])
            radius = float(request.args.get('radius',
                                            pqry.DEFAULT_RADIUS_M))
            limit = int(request.args.get('limit', pqry.DEFAULT_LIMIT))
            max_walk = request.args.get('max_walk')
            if max_walk is not None:
                max_walk = float(max_walk)
        except KeyError:
            raise wz.BadRequest('lat1, lon1, lat2, and lon2 are required.')
        except ValueError:
            raise wz.BadRequest('Coordinates, radius, limit, and max_walk '
                                'must be numbers.')
        category = request.args.get('category')
        place_type = request.args.get('type')
        if place_type and not category:
            category = 'amenity'
        try:
            with database_request():
                result = meet.find_spots(
                    (lat1, lon1), (lat2, lon2), radius=radius,
                    category=category, place_type=place_type, limit=limit,
                    sort=request.args.get('sort', 'fair'),
                    max_walk=max_walk)
        except ValueError as err:
            raise wz.BadRequest(str(err))
        return {'midpoint': result['midpoint'],
                'radius': result['radius'],
                MEET_RESP: result['spots'],
                'count': len(result['spots'])}


@api.route(HEALTH_EP)
class Health(Resource):
    """
    A simple health check to confirm the server is up.
    """
    def get(self):
        """
        Returns ok if the server is running.
        """
        return {HEALTH_RESP: 'ok'}

# user management endpoints
@api.route(REGISTER_EP)
class Register(Resource):
    '''
    Register (create) new users.
    '''
    @api.expect(USERNAME_PASSWORD_MODEL, validate=True)
    @api.response(HTTPStatus.CREATED.value, 'User created')
    @api.response(HTTPStatus.BAD_REQUEST.value, 'Invalid request')
    @api.response(HTTPStatus.CONFLICT.value, 'Username already exists')
    @limiter.limit("3 per hour")
    def post(self):
        data = request.get_json()

        username = data['username']
        password = data['password']

        if Users.query.filter_by(username=username).first():
            raise wz.Conflict('Username already exists.')

        password_hash = ph.hash(password)

        create_new_user(username, password_hash)

        return {
            'message': 'User created successfully.'
        }, HTTPStatus.CREATED

# authentication endpoints
@api.route(TOKEN_EP)
class Token(Resource):
    """
    Authenticate users and manage API tokens.
    """
    @api.response(HTTPStatus.CREATED.value, 'Token created')
    @api.response(HTTPStatus.UNAUTHORIZED.value, 'Invalid credentials')
    @api.response(HTTPStatus.BAD_REQUEST.value, 'Invalid request')
    @limiter.limit("5 per minute; 20 per hour")
    def post(self):
        # authenticate a user and create an api token
        data = request.get_json()

        username = data['username']
        password = data['password']

        if not username or not password:
            raise wz.BadRequest('Username and password required.')

        user = Users.query.filter_by(username=username).first()
        
        if not user:
            raise wz.Unauthorized('Invalid credentials.')

        try:
            ph.verify(user.password, password)
        except VerificationError:
            raise wz.Unauthorized('Invalid credentials.')

        # auth good, make token
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        expires = now + timedelta(days=7)

        # save to db
        api_token = ApiTokens(uid=user.uuid, token_hash=token_hash, created_at=now, expires_at=expires)

        sql_db.session.add(api_token)
        sql_db.session.commit()

        # return vals
        return {
            'access_token': token,
            'token_type': 'Bearer',
            'expires_at': expires.isoformat() + 'Z'
        }, HTTPStatus.CREATED

    # helper function to get api token
    # used for checking (GET) and revoking (DELETE) tokens
    def get_api_token():
        auth = request.headers.get('Authorization', '')

        if not auth.startswith('Bearer '):
            raise wz.Unauthorized('Bearer token required.')

        token = auth.removeprefix('Bearer ').strip()

        if not token:
            raise wz.Unauthorized('Invalid token.')

        token_hash = hashlib.sha256(token.encode()).hexdigest()
        api_token = ApiTokens.query.filter_by(token_hash=token_hash).first()

        if not api_token:
            raise wz.Unauthorized('Invalid token.')

        return api_token

    @api.response(HTTPStatus.OK.value, 'Token status')
    @api.response(HTTPStatus.UNAUTHORIZED.value, 'Invalid token')
    @limiter.limit("30 per minute")
    def get(self):
        api_token = self.get_api_token()

        now = datetime.now(timezone.utc)

        if api_token.revoked_at:
            status = 'revoked'
        elif api_token.expires_at.replace(tzinfo=timezone.utc) <= now:
            status = 'expired'
        else:
            status = 'active'

        return {
            'status': status,
            'created_at': api_token.created_at.isoformat(),
            'expires_at': api_token.expires_at.isoformat(),
            'revoked_at': api_token.revoked_at.isoformat() if api_token.revoked_at else None
        }, HTTPStatus.OK

    @api.response(HTTPStatus.OK.value, 'Token status')
    @api.response(HTTPStatus.UNAUTHORIZED.value, 'Invalid token')
    @limiter.limit("5 per minute; 20 per hour")
    def delete(self):
        api_token = self.get_api_token()

        if api_token.revoked_at:
            return {'message': 'Token already revoked.'}, HTTPStatus.OK

        now = datetime.now(timezone.utc)
        api_token.revoked_at = now

        sql_db.session.commit()

        return {
            'message': 'Token revoked successfully.',
            'revoked_at': now.isoformat()
        }, HTTPStatus.OK

@api.route(READY_EP)
class Ready(Resource):
    """Check MongoDB connectivity independently of Flask liveness."""

    @api.response(HTTPStatus.OK.value, 'MongoDB reachable')
    @api.response(HTTPStatus.SERVICE_UNAVAILABLE.value, 'Database unavailable')
    def get(self):
        """Ping MongoDB with a five-second database time budget."""
        if not dbc.is_db_up():
            raise wz.ServiceUnavailable(DATABASE_UNAVAILABLE)
        return {HEALTH_RESP: 'ok'}
