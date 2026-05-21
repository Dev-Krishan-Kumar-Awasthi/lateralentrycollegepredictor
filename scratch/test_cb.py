import sys
sys.path.append('.')
from main import app
from smart_choices import build_smart_choices
from predictor import fetch_cgpa_to_rank_map

with app.app_context():
    RANK_MAPS_CACHE = {2025: fetch_cgpa_to_rank_map(2025)}
    result = build_smart_choices(
        8.5, ['CSE', 'IT'], 'UR', 'M', 'Any', 'Y', 'All',
        year=2025, rank_maps_cache=RANK_MAPS_CACHE
    )
    print("Safe:", len(result['safe']))
    print("Target:", len(result['target']))
    print("Dream:", len(result['dream']))
    for bucket in ('safe', 'target', 'dream'):
        for item in result[bucket]:
            print(f"{bucket}: {item['college_name']} - {item['branch']} (prob: {item['probability']})")
