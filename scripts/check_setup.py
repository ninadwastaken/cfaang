"""Read-only checks for a local Meet Me API and imported NYC places."""

import argparse
import json
from urllib.error import URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import urlopen


def fetch_json(url):
    with urlopen(url, timeout=10) as response:
        return json.load(response)


def check_setup(base_url):
    query = urlencode(dict(lat1=40.7359, lon1=-73.9911,
                           lat2=40.7527, lon2=-73.9772,
                           category='amenity', type='cafe', limit=1))
    checks = [
        ('API health', '/health',
         'Start the API with ./local.sh or docker compose up -d --build; '
         'check API_URL and port 8000.'),
        ('MongoDB readiness', '/ready',
         'Run docker compose up -d mongo and check the API MongoDB '
         'connection settings.'),
        ('Sample meeting search', '/meet?' + query,
         'Check API logs and the places import/indexes. For the local '
         'Docker setup, run make local_db, then retry.'),
    ]
    for label, path, guidance in checks:
        try:
            data = fetch_json(base_url.rstrip('/') + path)
            if not isinstance(data, dict):
                raise ValueError('Expected a JSON object')
            if path.startswith('/meet'):
                spots = data.get('Spots')
                if not isinstance(spots, list):
                    raise ValueError('Expected a meeting results list')
                if not spots:
                    raise ValueError('No cafes found for the NYC sample')
            elif data.get('status') != 'ok':
                raise ValueError('Expected status ok')
        except (URLError, OSError, ValueError) as error:
            print(f'FAIL: {label}: {error}')
            print(guidance)
            print('Remaining checks skipped; fix this check and rerun.')
            return 1
        print(f'PASS: {label}')
    print('Local API, database, and sample places search are ready.')
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--api-url', default='http://127.0.0.1:8000')
    args = parser.parse_args()
    url = urlsplit(args.api_url)
    if url.scheme not in ('http', 'https') or not url.netloc:
        parser.error('--api-url must be an HTTP(S) URL')
    return check_setup(args.api_url)


if __name__ == '__main__':
    raise SystemExit(main())
