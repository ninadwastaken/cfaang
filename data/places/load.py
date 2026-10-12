import requests
from data.db_connect import connect_db
import os 
import time

LOCAL = "0"
CLOUD = "1"


def fetch_places(url, query):
    """Retry temporary Overpass failures before allowing a database reload."""
    for attempt in range(3):
        try:
            response = requests.post(
                url,
                data={'data': query},
                headers={
                    "User-Agent": "cfaang-local-dev/1.0",
                    "Accept": "application/json",
                },
                timeout=120,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            status = exc.response.status_code if exc.response is not None else None
            retryable = isinstance(exc, (requests.Timeout, requests.ConnectionError)) or status in (429, 502, 503, 504)
            if retryable and attempt < 2:
                delay = 10 * (attempt + 1)
                print(f"Overpass temporarily unavailable ({status or type(exc).__name__}). "
                      f"Retrying in {delay}s ({attempt + 2}/3)...", flush=True)
                time.sleep(delay)
                continue
            raise SystemExit(f"Overpass request failed after {attempt + 1} attempt(s): {exc}. "
                             "Existing database records were not changed.") from None

        try:
            data = response.json()
        except ValueError:
            raise SystemExit("Overpass returned invalid JSON; database records were not changed.") from None
        # Overpass can return HTTP 200 with an error and incomplete results.
        if data.get('remark'):
            raise SystemExit(f"Overpass returned incomplete results: {data['remark']}. "
                             "Database records were not changed.")
        if not isinstance(data.get('elements'), list):
            raise SystemExit("Overpass response is missing elements; database records were not changed.")
        return data


if os.environ.get('CLOUD_MONGO', LOCAL) == LOCAL:
    #Create Overpass query to find amenities (restaurants, cafes, etc.) in NYC
    overpass_url = os.environ.get('OVERPASS_URL', "https://overpass-api.de/api/interpreter")
    overpass_query = """
    [out:json][timeout:90];
    node["amenity"](40.4774,-74.2589,40.9176,-73.7004);
    out body;
    """

    print("Fetching data from OpenStreetMap Overpass API...")
    data = fetch_places(overpass_url, overpass_query)

    elements = data.get("elements", [])
    print(f"Found {len(elements)} elements. Formatting for GeoJSON...")

    #Format the raw OSM data into GeoJSON format
    documents = []
    for item in elements:
        geojson_doc = {
            "osm_id": item.get("id"),
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [item.get("lon"), item.get("lat")]
            },
            "properties": item.get("tags", {})
        }
        documents.append(geojson_doc)

    #Ingest into your local MongoDB
    if documents:
        client = connect_db()
        db = client["nyc_map"]
        collection = db["places"]
        collection.delete_many({}) # Optional: Clear collection before reload
        result = collection.insert_many(documents)
        print(f"Successfully imported {len(result.inserted_ids)} NYC places into local MongoDB!")
    else:
        print("No records found to import.")
