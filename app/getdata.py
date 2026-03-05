import csv
import json
import os
import requests

API_KEY = "live_7NVXrCqqp8cEJjyyAcaL5hblJ9MMUXCnbIWOgLfOYR8FrjPPHU0Iyp57bWheLzst"
GET_ALL_BREEDS = "https://api.thedogapi.com/v1/breeds"
QUERY_BREEDS = "https://api.thedogapi.com/v1/breeds/search"
GET_BREED_DETAILS = "https://api.thedogapi.com/v1/breeds/{breed_id}"

# Data folder relative to project root (parent of app/)
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
BREEDS_CSV = "breeds.csv"
BREEDS_JSON = "breeds.json"


def _flatten_breed(breed: dict) -> dict:
    """Flatten breed for CSV: weight/height as imperial_*, metric_*; image.url as image_url; no reference_image_id."""
    row = {}
    for key, value in breed.items():
        if key == "reference_image_id":
            continue
        if key == "weight" and isinstance(value, dict):
            row["imperial_weight"] = value.get("imperial", "")
            row["metric_weight"] = value.get("metric", "")
        elif key == "height" and isinstance(value, dict):
            row["imperial_height"] = value.get("imperial", "")
            row["metric_height"] = value.get("metric", "")
        elif key == "image" and isinstance(value, dict):
            row["image_url"] = value.get("url", "")
        elif isinstance(value, dict):
            for subkey, subvalue in value.items():
                row[f"{key}_{subkey}"] = subvalue
        else:
            row[key] = value
    return row


def fetch_breeds(api_key: str | None = None) -> list[dict]:
    """Fetch all breeds from The Dog API. Pass api_key or set DOG_API_KEY env var."""
    key = api_key
    if not key:
        raise ValueError("Provide api_key or set DOG_API_KEY environment variable")
    resp = requests.get(
        GET_ALL_BREEDS,
        headers={"x-api-key": key},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def save_breeds_to_csv(
    filepath: str | None = None,
    api_key: str | None = None,
) -> str:
    """Fetch breeds via fetch_breeds(), map to CSV, and save to the data folder. Returns path to saved file."""
    breeds = fetch_breeds(api_key)
    if not breeds:
        raise ValueError("No breeds returned from API")
    flat = [_flatten_breed(b) for b in breeds]
    all_keys = sorted({k for row in flat for k in row.keys()})
    path = filepath or os.path.join(DATA_DIR, BREEDS_CSV)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=all_keys, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(flat)
    return path


def save_breeds_to_json(
    filepath: str | None = None,
    api_key: str | None = None,
) -> str:
    """Fetch breeds via fetch_breeds() and save raw JSON to the data folder. Returns path to saved file."""
    breeds = fetch_breeds(api_key)
    if not breeds:
        raise ValueError("No breeds returned from API")
    path = filepath or os.path.join(DATA_DIR, BREEDS_JSON)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(breeds, f, indent=2, ensure_ascii=False)
    return path


def search_breeds(query: str, breed_groups: str, api_key: str | None = None) -> list[dict]:
    """Search breeds by name."""
    key = api_key
    if not key:
        raise ValueError("Provide api_key or set DOG_API_KEY environment variable")
    if not query or not query.strip():
        return []
    resp = requests.get(
        QUERY_BREEDS,
        params={"q": query.strip(), "breed_groups": breed_groups},
        headers={"x-api-key": key},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()

def get_breed_details(breed_id: str, api_key: str | None = None) -> dict:
    """Get breed details by ID."""
    key = api_key
    if not key:
        raise ValueError("Provide api_key or set DOG_API_KEY environment variable")
    resp = requests.get(
        GET_BREED_DETAILS.format(breed_id=breed_id),
        headers={"x-api-key": key},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()

if __name__ == "__main__":
    saved_csv = save_breeds_to_csv(api_key=API_KEY)
    saved_json = save_breeds_to_json(api_key=API_KEY)
    print(f"Saved breeds CSV to {saved_csv}")
    print(f"Saved breeds JSON to {saved_json}")
