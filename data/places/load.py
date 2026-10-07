import requests
from data.db_connect import connect_db
import os 

LOCAL = "0"
CLOUD = "1"

if os.environ.get('CLOUD_MONGO', LOCAL) == LOCAL:
    #Create Overpass query to find amenities (restaurants, cafes, etc.) in NYC
    overpass_url = "https://overpass-api.de/api/interpreter"
    overpass_query = """
    [out:json][timeout:90];
    node["amenity"](40.4774,-74.2589,40.9176,-73.7004);
    out body;
    """

    print("Fetching data from OpenStreetMap Overpass API...")
    try:
        response = requests.post(
            overpass_url,
            data={'data': overpass_query},
            headers={
                "User-Agent": "cfaang-local-dev/1.0",
                "Accept": "application/json",
            },
            timeout=120,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        detail = ""
        if exc.response is not None:
            detail = f"\nServer response: {exc.response.text[:1000]}"
        raise SystemExit(f"Overpass request failed: {exc}{detail}") from None
    data = response.json()

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
