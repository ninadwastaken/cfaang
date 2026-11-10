"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""
from contextlib import contextmanager
from http import HTTPStatus

from flask import Flask, request
from flask_restx import Resource, Api  # , fields  # Namespace
from flask_cors import CORS
import pymongo as pm

import werkzeug.exceptions as wz

import states.query as sqry
import places.query as pqry
import places.meet as meet
import data.db_connect as dbc

app = Flask(__name__)
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
READY_EP = '/ready'
DATABASE_TIMEOUT_SECONDS = 5
DATABASE_UNAVAILABLE = 'Database is temporarily unavailable. Please try again.'


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


@api.route(HELLO_EP)
class HelloWorld(Resource):
    """
    The purpose of the HelloWorld class is to have a simple test to see if the
    app is working at all.
    """
    def get(self):
        """
        A trivial endpoint to see if the server is running.
        """
        return {HELLO_RESP: 'world'}


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
        endpoints = sorted(rule.rule for rule in api.app.url_map.iter_rules())
        return {"Available endpoints": endpoints}


@api.route(STATES_EP)
class States(Resource):
    """
    The get method will return a list of all states in the database.
    """
    @api.response(HTTPStatus.OK.value, 'Success')
    @api.response(HTTPStatus.SERVICE_UNAVAILABLE.value, 'Service Unavailable')
    def get(self):
        """
        The get method will return a list of all states in the database.
        """
        states = sqry.get_states()
        if states is None:
            raise wz.ServiceUnavailable('Database may be down.')
        return {STATES_RESP: states}


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
    def get(self):
        """
        Return NYC places, like /places?category=leisure&type=park.
        """
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
    })
    @api.response(HTTPStatus.OK.value, 'Success')
    @api.response(HTTPStatus.BAD_REQUEST.value, 'Bad query parameters')
    @api.response(HTTPStatus.SERVICE_UNAVAILABLE.value, 'Database unavailable')
    def get(self):
        """
        Return spots near the midpoint of two people, like
        /meet?lat1=40.73&lon1=-73.99&lat2=40.68&lon2=-73.97&type=cafe.
        """
        try:
            lat1 = float(request.args['lat1'])
            lon1 = float(request.args['lon1'])
            lat2 = float(request.args['lat2'])
            lon2 = float(request.args['lon2'])
            radius = float(request.args.get('radius',
                                            pqry.DEFAULT_RADIUS_M))
            limit = int(request.args.get('limit', pqry.DEFAULT_LIMIT))
        except KeyError:
            raise wz.BadRequest('lat1, lon1, lat2, and lon2 are required.')
        except ValueError:
            raise wz.BadRequest('Coordinates, radius, and limit must be '
                                'numbers.')
        category = request.args.get('category')
        place_type = request.args.get('type')
        if place_type and not category:
            category = 'amenity'
        try:
            with database_request():
                result = meet.find_spots(
                    (lat1, lon1), (lat2, lon2), radius=radius,
                    category=category, place_type=place_type, limit=limit,
                    sort=request.args.get('sort', 'fair'))
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
