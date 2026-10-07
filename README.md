# cfaang

A Flask REST API server.

## Setup

1. Clone the repo and go into it:
   git clone https://github.com/ninadwastaken/cfaang.git
   cd cfaang

2. Create and activate a virtual environment:
   python3 -m venv venv
   source venv/bin/activate

3. Install dependencies:
   make dev_env

4. Set your PYTHONPATH:
   export PYTHONPATH=$(pwd)

## Running the server

./local.sh

Then go to http://127.0.0.1:8000/hello. You should see {"hello": "world"}.
The Swagger docs for all endpoints are at http://127.0.0.1:8000/.

## Tests

make all_tests

Note: the /states test needs MongoDB running locally.

## Production

To build production, type `make prod`.