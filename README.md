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

To create the env for a new developer, run `make dev_env`.


# Docker Development

The places importer and database helpers use `nyc_map` by default. Set the
`MONGO_DB` environment variable in the Python process to select another database.
For Docker, add `MONGO_DB` to the API service's environment if you need an override.
Changing this setting selects a database; it does not move existing records.
Helpers connect automatically and still accept an explicit `db=` override.

With Docker running, build and start the API and MongoDB:

```sh
make local_build
```

then to load data into MongoDB run: 

```sh
make local_db
```

View MongoDB Logs: 

```sh
docker compose logs --tail=50 -f mongo
```

Open MongoDB shell for querying:
```sh
docker compose exec mongo mongosh
```
