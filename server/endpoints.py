"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""
from http import HTTPStatus

from flask import Flask, request
from flask_restx import Resource, Api  # , fields  # Namespace
from flask_cors import CORS

import werkzeug.exceptions as wz

import states.query as sqry
import places.query as pqry

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
HEALTH_EP = '/health'
HEALTH_RESP = 'status'


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
    Get NYC places, optionally filtered by amenity type.
    """
    @api.doc(params={
        'amenity': 'Amenity type, like cafe, library, or bank',
        'limit': 'Max results to return (default 50, max 500)',
    })
    @api.response(HTTPStatus.OK.value, 'Success')
    @api.response(HTTPStatus.BAD_REQUEST.value, 'Bad limit value')
    def get(self):
        """
        Return NYC places, like /places?amenity=cafe&limit=10.
        """
        amenity = request.args.get('amenity')
        try:
            limit = int(request.args.get('limit', pqry.DEFAULT_LIMIT))
        except ValueError:
            raise wz.BadRequest('limit must be a number.')
        places = pqry.get_places(amenity=amenity, limit=limit)
        return {PLACES_RESP: places, 'count': len(places)}


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
