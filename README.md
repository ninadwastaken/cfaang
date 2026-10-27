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

### Live meeting recommendations

The mobile app lets two people choose NYC landmarks and a category (cafés,
parks, or museums). It calls `/meet` with landmark coordinates and shows real
places from MongoDB. Landmark coordinates are approximate; address search and
live device location are not implemented. Distances are straight-line meters
converted to kilometers, not walking or transit times. Results follow the
backend's current midpoint ordering; transit fairness is not calculated.

For a complete local setup:

```sh
# Stop any separately running ./local.sh server first (both use port 8000).
docker compose up -d --build
# Import NYC places if the database is empty. Requires Overpass internet access.
make local_db
cd mobile
npm ci
npm start -- --clear
```

Set `mobile/.env.local` as described above. The Docker API is accessible from
the iOS simulator at `http://127.0.0.1:8000`, or from the Android emulator at
`http://10.0.2.2:8000`. For a physical phone, Docker's MongoDB port is internal:
add a local Compose override publishing MongoDB to loopback before running
Flask on the host, or explicitly publish the Docker API to your trusted LAN.
Running `local.sh` alone does not start MongoDB.

Choose two landmarks, select a category, and tap **Find meeting spots**.
If no places match within 1 km of the midpoint, expand the radius or change
category. Retry is available for network and server errors. Each result has a
Google Maps directions link starting at your selected landmark. Maps opens
externally; the app does not compute those routes. API health indicates Flask
availability only and does not confirm MongoDB or the import is ready.

Screens live in `mobile/src/app/`; API contracts and category mappings are in
`mobile/api.ts`, and landmark presets are in `mobile/src/data/landmarks.ts`.
There is no sample-data fallback. A local API smoke check:

```sh
curl 'http://127.0.0.1:8000/meet?lat1=40.7359&lon1=-73.9911&lat2=40.7527&lon2=-73.9772&category=amenity&type=cafe'
```

Mobile checks: `npm run lint`, `npm run typecheck`, and
`node --test tests/api.test.cjs` from `mobile/`.

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
