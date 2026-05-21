"""Smart choice-list builder: Safe / Target / Dream buckets."""
from predictor import (
    fetch_cgpa_to_rank_map, estimate_rank_range,
    fetch_colleges_from_rank, calc_probability, BRANCH_NAMES,
)


def build_smart_choices(cgpa: float, branch, category: str, gender: str,
                        college_type: str, domicile: str = "Y",
                        city: str = "All", year: int = 2025,
                        rank_maps_cache: dict | None = None,
                        max_per_bucket: int = 15) -> dict:
    """
    Returns ordered choice list in three buckets plus merged list.
    """
    if rank_maps_cache is None:
        rank_maps_cache = {year: fetch_cgpa_to_rank_map(year)}

    branches = branch if isinstance(branch, list) else ([branch] if branch and branch != "All" else ["All"])

    cgpa_map = rank_maps_cache.get(year) or fetch_cgpa_to_rank_map(year)
    min_rank, max_rank = estimate_rank_range(cgpa_map, cgpa)

    seen = set()
    safe, target, dream = [], [], []

    for br in branches:
        raw = fetch_colleges_from_rank(
            min_rank, max_rank, br, category, gender, college_type, year, domicile
        )
        if city and city != "All":
            raw = [c for c in raw if city.lower() in c.college_name.lower()]

        for col in raw:
            key = (col.college_name, col.branch)
            if key in seen:
                continue
            seen.add(key)

            prob = calc_probability(min_rank, max_rank, col.opening_rank, col.closing_rank)
            item = {
                "college_name": col.college_name,
                "branch": col.branch,
                "branch_name": BRANCH_NAMES.get(col.branch, col.branch),
                "probability": prob,
                "college_type": col.college_type,
                "closing_rank": col.closing_rank,
                "opening_rank": col.opening_rank,
            }
            if prob >= 80:
                safe.append(item)
            elif prob >= 50:
                target.append(item)
            elif prob >= 25:
                dream.append(item)

    safe.sort(key=lambda x: (-x["probability"], x["closing_rank"]))
    target.sort(key=lambda x: (-x["probability"], x["closing_rank"]))
    dream.sort(key=lambda x: (-x["probability"], x["closing_rank"]))

    safe = safe[:max_per_bucket]
    target = target[:max_per_bucket]
    dream = dream[:max_per_bucket]

    # Merged order: dream → target → safe (standard counselling fill strategy)
    merged = []
    for label, bucket in (("dream", dream), ("target", target), ("safe", safe)):
        for item in bucket:
            merged.append({**item, "bucket": label})

    return {
        "min_rank": min_rank,
        "max_rank": max_rank,
        "year": year,
        "safe": safe,
        "target": target,
        "dream": dream,
        "merged": merged,
        "total": len(merged),
    }
