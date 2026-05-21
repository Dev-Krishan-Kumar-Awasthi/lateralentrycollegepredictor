"""
Google Maps Platform integration for college profiles and driving distance.

Requires env: GOOGLE_MAPS_API_KEY (Places + Distance Matrix + Geocoding enabled)

Google Places does NOT publish B.Tech tuition — fees come from:
  - college_profiles.json cache (enriched from official sites / verified listings)
  - website URL returned by Google Place Details
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

_PROFILES_PATH = Path(__file__).parent / "config" / "college_profiles.json"
_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "").strip()


def _http_get(url: str, params: dict) -> dict:
    qs = urllib.parse.urlencode(params)
    full = f"{url}?{qs}"
    req = urllib.request.Request(full, headers={"User-Agent": "MP-DTE-Predictor/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Google Maps API error fetching {url}: {e}")
        return {}



def api_key_configured() -> bool:
    return bool(_API_KEY)


def find_place(query: str) -> dict | None:
    """Text search → basic place info + place_id."""
    if not _API_KEY:
        return None
    data = _http_get(
        "https://maps.googleapis.com/maps/api/place/findplacefromtext/json",
        {
            "input": f"{query} engineering college Madhya Pradesh India",
            "inputtype": "textquery",
            "fields": "place_id,name,formatted_address,geometry,rating,user_ratings_total,business_status",
            "key": _API_KEY,
        },
    )
    if data.get("status") != "OK" or not data.get("candidates"):
        return None
    c = data["candidates"][0]
    loc = c.get("geometry", {}).get("location", {})
    return {
        "place_id": c.get("place_id"),
        "google_name": c.get("name"),
        "address": c.get("formatted_address"),
        "lat": loc.get("lat"),
        "lng": loc.get("lng"),
        "rating": c.get("rating"),
        "user_ratings_total": c.get("user_ratings_total"),
        "business_status": c.get("business_status"),
    }


def place_details(place_id: str) -> dict:
    if not _API_KEY or not place_id:
        return {}
    data = _http_get(
        "https://maps.googleapis.com/maps/api/place/details/json",
        {
            "place_id": place_id,
            "fields": "name,formatted_address,geometry,formatted_phone_number,website,url,rating,user_ratings_total,opening_hours",
            "key": _API_KEY,
        },
    )
    if data.get("status") != "OK":
        return {}
    r = data.get("result", {})
    loc = r.get("geometry", {}).get("location", {})
    return {
        "google_name": r.get("name"),
        "address": r.get("formatted_address"),
        "lat": loc.get("lat"),
        "lng": loc.get("lng"),
        "phone": r.get("formatted_phone_number"),
        "website": r.get("website"),
        "maps_url": r.get("url"),
        "rating": r.get("rating"),
        "user_ratings_total": r.get("user_ratings_total"),
        "opening_hours": (r.get("opening_hours") or {}).get("weekday_text"),
    }


def driving_distance_km(origin_lat: float, origin_lng: float,
                        dest_lat: float, dest_lng: float) -> dict | None:
    """Google Distance Matrix — driving distance & duration."""
    if not _API_KEY:
        return None
    data = _http_get(
        "https://maps.googleapis.com/maps/api/distancematrix/json",
        {
            "origins": f"{origin_lat},{origin_lng}",
            "destinations": f"{dest_lat},{dest_lng}",
            "mode": "driving",
            "region": "in",
            "key": _API_KEY,
        },
    )
    if data.get("status") != "OK":
        return None
    rows = data.get("rows", [])
    if not rows or not rows[0].get("elements"):
        return None
    el = rows[0]["elements"][0]
    if el.get("status") != "OK":
        return None
    dist_m = el["distance"]["value"]
    dur_s = el["duration"]["value"]
    return {
        "distance_km": round(dist_m / 1000),
        "distance_text": el["distance"]["text"],
        "duration_text": el["duration"]["text"],
        "source": "google_distance_matrix",
    }


def geocode_city(city: str) -> dict | None:
    if not _API_KEY:
        return None
    data = _http_get(
        "https://maps.googleapis.com/maps/api/geocode/json",
        {
            "address": f"{city}, Madhya Pradesh, India",
            "key": _API_KEY,
        },
    )
    if data.get("status") != "OK" or not data.get("results"):
        return None
    loc = data["results"][0]["geometry"]["location"]
    return {"lat": loc["lat"], "lng": loc["lng"]}


def enrich_college(college_name: str, existing: dict | None = None) -> dict:
    """Fetch Google data and merge into profile dict."""
    profile = dict(existing or {})
    profile["college_name"] = college_name
    profile.setdefault("sources", [])

    found = find_place(college_name)
    if not found:
        profile["google_status"] = "not_found"
        return profile

    profile.update(found)
    if found.get("place_id"):
        time.sleep(0.15)
        profile.update(place_details(found["place_id"]))

    profile["google_status"] = "ok"
    if "google_places" not in profile["sources"]:
        profile["sources"].append("google_places")
    profile["fetched_at"] = time.strftime("%Y-%m-%d")
    return profile


def load_profiles_cache() -> dict:
    if not _PROFILES_PATH.exists():
        return {"colleges": {}, "meta": {"source": "google_maps_platform"}}
    with open(_PROFILES_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_profiles_cache(data: dict) -> None:
    _PROFILES_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(_PROFILES_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_cached_profile(college_name: str) -> dict | None:
    cache = load_profiles_cache()
    return cache.get("colleges", {}).get(college_name)
