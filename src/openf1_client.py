import hashlib
import json
import time
from pathlib import Path

import requests

BASE_URL = "https://api.openf1.org/v1"
CACHE_DIR = Path(__file__).resolve().parent.parent / "cache" / "openf1"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Free tier allows 30 requests/minute, so wait ~2 seconds between real requests
MIN_SECONDS_BETWEEN_REQUESTS = 2.1
_last_request_time = 0.0


def _cache_path(endpoint, params):
    key = endpoint + "?" + "&".join(f"{k}={params[k]}" for k in sorted(params))
    digest = hashlib.md5(key.encode()).hexdigest()[:12]
    return CACHE_DIR / f"{endpoint}_{digest}.json"


def get(endpoint, **params):
    """Fetch data from OpenF1, using the local cache if we already have it."""
    global _last_request_time
    path = _cache_path(endpoint, params)

    if path.exists():
        return json.loads(path.read_text())

    for _ in range(5):
        wait = MIN_SECONDS_BETWEEN_REQUESTS - (time.time() - _last_request_time)
        if wait > 0:
            time.sleep(wait)

        response = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=60)
        _last_request_time = time.time()

        if response.status_code == 429:
            print("Rate limited, waiting 10 seconds...")
            time.sleep(10)
            continue

        if not response.ok:
            raise RuntimeError(f"OpenF1 error {response.status_code}: {response.text}")

        data = response.json()
        if not isinstance(data, list):
            raise RuntimeError(f"OpenF1 refused the request: {data}")

        path.write_text(json.dumps(data))
        return data

    raise RuntimeError("Too many retries, try again in a minute")