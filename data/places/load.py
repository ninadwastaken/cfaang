import requests
from data.db_connect import connect_db
import os 
import time
from uuid import uuid4

from pymongo.errors import PyMongoError

LOCAL = "0"
CLOUD = "1"
DEFAULT_OVERPASS_URL = "https://overpass-api.de/api/interpreter"


def fetch_places(url, query, fallback_urls=()):
    """Retry temporary Overpass failures before allowing a database reload."""
    endpoints = list(dict.fromkeys((url, *fallback_urls)))
    for attempt in range(3):
        endpoint = endpoints[min(attempt, len(endpoints) - 1)]
        try:
            response = requests.post(
                endpoint,
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
                next_endpoint = endpoints[min(attempt + 1, len(endpoints) - 1)]
                print(f"Overpass temporarily unavailable at {endpoint} "
                      f"({status or type(exc).__name__}). "
                      f"Retrying at {next_endpoint} in {delay}s ({attempt + 2}/3)...", flush=True)
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


PLACE_CATEGORIES = {
    "amenity": "restaurant|cafe|bar|pub|food_court|ice_cream|cinema|theatre|arts_centre|community_centre|library",
    "leisure": "park|garden|playground|nature_reserve|sports_centre|fitness_centre|swimming_pool|bowling_alley|miniature_golf|escape_game|amusement_arcade",
    "tourism": "museum|gallery|attraction|viewpoint|zoo|aquarium|theme_park|artwork|picnic_site",
    "historic": "monument|memorial|castle|ruins|fort|archaeological_site",
    "natural": "beach|peak|wood",
    "shop": "books|mall|department_store|music|games|hobby|antiques|art",
}


def fetch_all_places(url, fallback_urls=()):
    """Fetch categories sequentially; return only after every request succeeds."""
    elements = {}
    for number, (category, values) in enumerate(PLACE_CATEGORIES.items(), start=1):
        print(f"Fetching {category} ({number}/{len(PLACE_CATEGORIES)})...", flush=True)
        query = f'''
        [out:json][timeout:90];
        area["wikidata"="Q60"]->.nyc;
        nwr["{category}"~"^({values})$"](area.nyc);
        out center;
        '''
        try:
            data = fetch_places(url, query, fallback_urls)
        except SystemExit as exc:
            raise SystemExit(f"Category {category} failed: {exc}") from None
        for item in data['elements']:
            # A place may match multiple categories; OSM IDs are unique per type.
            elements[(item['type'], item['id'])] = item
        print(f"Fetched {len(data['elements'])} {category} elements.", flush=True)
    return list(elements.values())


def replace_places(db, documents):
    """Stage a complete import before replacing places; last successful rename wins."""
    if not documents:
        return None

    staging_name = f"places_import_{uuid4().hex}"
    staging = db[staging_name]
    try:
        for name, index in db['places'].index_information().items():
            if name == '_id_':
                continue
            options = {key: value for key, value in index.items()
                       if key not in ('key', 'v', 'ns')}
            staging.create_index(index['key'], name=name, **options)
        result = staging.insert_many(documents)
        staging.rename('places', dropTarget=True)
        return result
    finally:
        # Use the original name: after a successful rename, it no longer exists.
        try:
            db.drop_collection(staging_name)
        except PyMongoError as exc:
            print(f"Could not clean up temporary collection {staging_name}: {exc}")


if __name__ == '__main__' and os.environ.get('CLOUD_MONGO', LOCAL) == LOCAL:
    # Find places to eat, hang out, explore, and do activities within NYC.
    overpass_url = DEFAULT_OVERPASS_URL
    print("Fetching data from OpenStreetMap Overpass API...")
    elements = fetch_all_places(overpass_url)

    print(f"Found {len(elements)} elements. Formatting for GeoJSON...")

    #Format the raw OSM data into GeoJSON format
    documents = []
    for item in elements:
        # Ways and relations use a bounding-box center for their map marker.
        location = item if item["type"] == "node" else item.get("center", {})
        lon = location.get("lon")
        lat = location.get("lat")
        if lon is None or lat is None:
            continue

        geojson_doc = {
            "osm_id": item["id"],
            "osm_type": item["type"],
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat]
            },
            "properties": item.get("tags", {})
        }
        documents.append(geojson_doc)

    #Ingest into your local MongoDB
    if documents:
        client = connect_db()
        db = client["nyc_map"]
        result = replace_places(db, documents)
        print(f"Successfully imported {len(result.inserted_ids)} NYC places into local MongoDB!")
    else:
        print("No records found to import.")
