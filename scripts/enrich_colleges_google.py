#!/usr/bin/env python3
"""
Batch-enrich all DB colleges using Google Places API.

Usage:
  set GOOGLE_MAPS_API_KEY=your_key
  python scripts/enrich_colleges_google.py
  python scripts/enrich_colleges_google.py --limit 20   # test run
  python scripts/enrich_colleges_google.py --refresh    # re-fetch all

Billing: ~2 API calls per college (Find Place + Details). 261 colleges ≈ 522 calls.
Enable: Places API, Places API (New) optional, Distance Matrix, Geocoding in Google Cloud Console.
"""
import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from main import app  # noqa: E402
from models import SeatInfo  # noqa: E402
from db import db  # noqa: E402
from google_college_service import (  # noqa: E402
    api_key_configured,
    enrich_college,
    load_profiles_cache,
    save_profiles_cache,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()

    if not api_key_configured():
        print("ERROR: Set GOOGLE_MAPS_API_KEY environment variable.")
        print("Get key: https://console.cloud.google.com/google/maps-apis")
        sys.exit(1)

    cache = load_profiles_cache()
    colleges = cache.setdefault("colleges", {})

    with app.app_context():
        names = sorted({r[0] for r in db.session.query(SeatInfo.college_name).distinct().all()})

    if args.limit:
        names = names[: args.limit]

    done, skip, fail = 0, 0, 0
    for i, name in enumerate(names, 1):
        if not args.refresh and name in colleges and colleges[name].get("google_status") == "ok":
            skip += 1
            continue
        print(f"[{i}/{len(names)}] {name[:60]}...")
        try:
            existing = colleges.get(name)
            profile = enrich_college(name, existing)
            colleges[name] = profile
            if profile.get("google_status") == "ok":
                done += 1
            else:
                fail += 1
            if i % 10 == 0:
                save_profiles_cache(cache)
            time.sleep(0.25)
        except Exception as e:
            print(f"  FAIL: {e}")
            fail += 1

    cache["meta"] = {
        "source": "google_maps_platform",
        "enriched_count": sum(1 for v in colleges.values() if v.get("google_status") == "ok"),
        "total": len(colleges),
    }
    save_profiles_cache(cache)
    print(f"\nDone: {done} enriched, {skip} skipped, {fail} failed/not found")
    print(f"Saved: config/college_profiles.json")


if __name__ == "__main__":
    main()
