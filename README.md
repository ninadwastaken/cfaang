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

## Mobile app connection

The app checks Flask's `/health` endpoint on launch and offers a retry if the
connection fails. This checks API availability; it does not check MongoDB.

1. Run `./local.sh` with your Python environment activated.
2. Set `EXPO_PUBLIC_API_URL` in `mobile/.env.local` (see `mobile/.env.example`).
   Use `http://127.0.0.1:8000` for the iOS simulator or a browser on your computer,
   or `http://10.0.2.2:8000` for the Android emulator.
3. For a physical phone, use your computer's LAN IP, such as
   `http://192.168.1.20:8000`, and run `FLASK_RUN_HOST=0.0.0.0 ./local.sh` on a
   trusted local network. Connect the phone and computer to the same network.
4. Run `cd mobile` and `npm start`. Reload the app after changing the API URL.

The Docker setup publishes the API on loopback only; use `local.sh` as above
for physical-phone development. Use an HTTPS API URL for deployed builds.

### Mobile meeting preview

The mobile app has a two-location form and category-filtered sample results.
Locations are labels only: geocoding and `/meet` integration are pending.
All places and distances in the preview are fictional fixtures in
`mobile/src/data/demo.ts`. The preview works even when Flask is offline;
the home screen reports the API connection separately.

Navigation uses Expo Router, with screens in `mobile/src/app/`. After installing
dependencies or switching from the original home screen, restart Metro with
`cd mobile && npm start -- --clear`.

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
