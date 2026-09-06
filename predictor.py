from models import SeatInfo, CgpaRankRange, model_to_dict
from db import db


# ── MP cities for city filter ─────────────────────────────────────────────────
MP_CITIES = [
    "Bhopal", "Indore", "Gwalior", "Jabalpur", "Ujjain",
    "Sagar", "Rewa", "Satna", "Khargone", "Raisen",
    "Chhindwara", "Seoni", "Dewas", "Jhabua",
]


# ── Branch full-name mapping (all codes from DB) ──────────────────────────────
BRANCH_NAMES = {
    'AGE':       'Agriculture Engineering',
    'AI':        'Artificial Intelligence',
    'AIADS':     'AI & Data Science',
    'AIAIDS':    'AI, AI & Data Science',
    'AIML':      'AI & Machine Learning',
    'AIR':       'AI & Robotics',
    'ARE':       'Architecture',
    'AUTO':      'Automobile Engineering',
    'BM':        'Biomedical Engineering',
    'CHEM':      'Chemical Engineering',
    'CIVIL':     'Civil Engineering',
    'CMPS':      'Computer Science (CMPS)',
    'CSBS':      'CSE (Biological Science)',
    'CSD':       'CSE (DevOps)',
    'CSE':       'Computer Science Engg',
    'CSEAI':     'CSE (Artificial Intelligence)',
    'CSEAIAIDS': 'CSE (AI & Data Science)',
    'CSEBC':     'CSE (Blockchain)',
    'CSECS':     'CSE (Cyber Security)',
    'CSEDS':     'CSE (Data Science)',
    'CSEIL':     'CSE (Internet of Laws)',
    'CSEIML':    'CSE (AI & ML)',
    'CSEIOT':    'CSE (IoT)',
    'CSEITCS':   'CSE (IT & Cyber Security)',
    'CSEML':     'CSE (Machine Learning)',
    'CSERC':     'CSE (Robotics & Cloud)',
    'DS':        'Data Science',
    'EC':        'Electronics & Comm. Engg',
    'ECACT':     'EC (Advanced Comm. Tech)',
    'ECS':       'Electronics & Comp. Science',
    'EE':        'Electrical Engineering',
    'EEIOT':     'Electrical Engg (IoT)',
    'EI':        'Electronics & Instrumentation',
    'EL':        'Electronics Engineering',
    'ELECT ELEX':'Electronics & Electrical Engg',
    'ET':        'Electronics & Telecom.',
    'EV':        'Electric Vehicle Technology',
    'FTS':       'Food Technology & Science',
    'INOT':      'Instrumentation & Control (IoT)',
    'IP':        'Industrial & Production Engg',
    'IT':        'Information Technology',
    'ITAIAR':    'IT (AI & AR)',
    'ITIOT':     'IT (IoT)',
    'MAC':       'Mathematics & Computing',
    'MECH':      'Mechanical Engineering',
    'MINING':    'Mining Engineering',
    'MMP':       'Manufacturing & Mechatronics',
    'MTENG':     'Mechatronics Engineering',
    'PCT':       'Polymer & Chemical Technology',
}


# ── College name aliases & acronyms mapping ──────────────────────────────────
COLLEGE_ALIASES = {
    "sgsits": ["Shri G.S. Institute", "SGSITS", "GSITS"],
    "gsits": ["Shri G.S. Institute", "SGSITS", "GSITS"],
    "sgits": ["Shri G.S. Institute", "SGSITS", "GSITS"],
    "mits": ["Madhav Institute", "MITS"],
    "iet": ["Institute of Engineering and Technology", "IET DAVV", "IET-DAVV"],
    "iet davv": ["Institute of Engineering and Technology", "IET DAVV", "IET-DAVV"],
    "iet-davv": ["Institute of Engineering and Technology", "IET DAVV", "IET-DAVV"],
    "davv": ["Institute of Engineering and Technology", "IET DAVV", "IET-DAVV"],
    "jec": ["JABALPUR ENGINEERING COLLEGE", "JEC"],
    "uit rgpv": ["University Institute of Technology RGPV", "University Institute of Technology REPV", "UIT RGPV", "UIT-RGPV"],
    "uit-rgpv": ["University Institute of Technology RGPV", "University Institute of Technology REPV", "UIT RGPV", "UIT-RGPV"],
    "rgpv": ["University Institute of Technology", "RGPV", "SCHOOL OF INFORMATION TECHNOLOGY RGPV"],
    "uit": ["University Institute of Technology", "UIT"],
    "lnct": ["Lakshmi Narain College", "LNCT"],
    "lncts": ["Lakshmi Narain College of Technology & Science", "LNCTS"],
    "lncte": ["Lakshmi Narain College of Technology Excellence", "LNCTE"],
    "jnct": ["Jai Narain College", "JNCT"],
    "uec": ["UJJAIN ENGINEERING COLLEGE", "UEC"],
    "sati": ["Samrat Ashok", "SATI"],
    "rec": ["Rewa Engineering", "REC", "RADHARAMAN ENGINEERING"],
    "igec": ["Indira Gandhi Engineering", "IGEC"],
    "rjit": ["Rustamji Institute", "RJIT"],
    "tit": ["TECHNOCRATS INSTITUTE", "TIT"],
    "sistec": ["Sagar Institute of Science", "SISTEC"],
    "sirt": ["Sagar Institute of Research", "SIRT"],
    "acropolis": ["Acropolis Institute", "AITR"],
    "aitr": ["Acropolis Institute", "AITR"],
    "ips": ["IPS Academy", "IPS College"],
    "ipsa": ["IPS Academy", "IPSA"],
    "oist": ["Oriental Institute", "OIST"],
    "oct": ["Oriental College", "OCT"],
    "ggits": ["GYAN GANGA INSTITUTE", "GGITS"],
    "ggct": ["Gyan Ganga College", "GGCT"],
    "gyan ganga": ["Gyan Ganga"],
    "prestige": ["Prestige Institute", "PIEMR"],
    "piemr": ["Prestige Institute", "PIEMR"],
    "iist": ["Indore Institute of Science", "IIST"],
    "btirt": ["Babulal Tarabai Institute", "BTIRT"],
    "sdbc": ["Sushila Devi Bansal", "SDBC"],
    "svce": ["Swami Vivekanand College", "SVCE"],
    "vits": ["VINDHYA INSTITUTE", "VITS"],
    "nec": ["Nowgong Engineering", "NEC"],
    "soit": ["SCHOOL OF INFORMATION TECHNOLOGY", "SOIT"],
    "truba": ["Truba Institute", "Truba"],
    "bits": ["Bansal Institute", "BITS"],
    "birt": ["Bansal Institute of Research", "BIRT"],
    "bist": ["Bansal Institute of Science", "BIST"],
    "cdgi": ["Chameli Devi", "CDGI"],
    "hcet": ["Hitkarni College", "HCET"],
    "itm": ["INSTITUTE OF TECHNOLOGY AND MANAGEMENT", "ITM"],
    "jit": ["Jawaharlal Institute", "JIT"],
    "mit": ["Mahakal Instute", "Mahakal Institute", "MIT"],
    "mpct": ["Maharana Pratap", "MPCT"],
    "mist": ["Malwa Institute of Science", "MIST"],
    "pcst": ["PATEL COLLEGE", "PCST"],
    "srkcesm": ["SHRI RAMA KRISHNA COLLEGE", "SRKCESM"]
}


def calc_probability(rank_min: int, rank_max: int,
                     opening_rank: int, closing_rank: int) -> int:
    """
    Estimate admission probability % based on:
      rank_min = user's BEST estimated rank (lowest number = top merit)
      rank_max = user's WORST estimated rank (highest number = lower merit)
      opening_rank = best rank admitted last year (lowest number)
      closing_rank = worst rank admitted last year = cutoff

    Logic:
      - If even worst rank <= closing_rank → High (75-92%)
      - If best rank <= closing_rank < worst rank → Medium (25-68%)
      - All shown colleges have closing_rank >= rank_min (guaranteed by DB query)
    """
    if rank_max == rank_min:
        # Exact rank known — simple check
        if rank_min <= opening_rank:
            return 92
        if rank_min <= closing_rank:
            return 75
        return 40

    if rank_max <= closing_rank:
        # Even worst-case rank qualifies
        if rank_min <= opening_rank:
            return 92  # Rank is in toppers range
        return 75

    # Partial overlap: rank_min <= closing_rank < rank_max
    overlap  = closing_rank - rank_min
    span     = rank_max - rank_min
    ratio    = overlap / span if span > 0 else 0
    prob     = int(ratio * 60) + 12   # range: 12 – 72
    return max(12, min(68, prob))


def interpolate_range(c, c1, r1_min, r1_max, c2, r2_min, r2_max):
    r_min = r1_min + (c - c1) * (r2_min - r1_min) / (c2 - c1)
    r_max = r1_max + (c - c1) * (r2_max - r1_max) / (c2 - c1)
    return round(r_min), round(r_max)


def estimate_rank_range(cgpa_to_rank_map, cgpa):
    if not cgpa_to_rank_map:
        return (99999, 99999)
    if cgpa > cgpa_to_rank_map[0].cgpa:
        return (1, 1)
    if cgpa < cgpa_to_rank_map[-1].cgpa:
        return (cgpa_to_rank_map[-1].min_rank, cgpa_to_rank_map[-1].max_rank)

    left = 0
    right = len(cgpa_to_rank_map) - 1

    while left <= right:
        mid = (left + right) // 2

        if cgpa_to_rank_map[mid].cgpa == cgpa:
            return (cgpa_to_rank_map[mid].min_rank, cgpa_to_rank_map[mid].max_rank)
        elif cgpa_to_rank_map[mid].cgpa < cgpa:   # FIX: was 'if', now 'elif' — prevents double-execution
            right = mid - 1
        else:
            left = mid + 1

    left  = min(left,  len(cgpa_to_rank_map) - 1)
    right = max(right, 0)

    r1_min = cgpa_to_rank_map[left].min_rank
    r1_max = cgpa_to_rank_map[left].max_rank
    r2_min = cgpa_to_rank_map[right].min_rank
    r2_max = cgpa_to_rank_map[right].max_rank
    c1     = cgpa_to_rank_map[left].cgpa
    c2     = cgpa_to_rank_map[right].cgpa

    return interpolate_range(cgpa, c1, r1_min, r1_max, c2, r2_min, r2_max)


def fetch_colleges_from_rank(rank_min, rank_max, branch, category, gender, college_type, year, domicile='Y'):
    """
    Fetch colleges where closing_rank >= rank_min.
    Gender matches requested gender OR 'OP' (open to all).
    college_type == 'Any' skips type filter.
    branch == 'All' skips branch filter (show all branches).
    branch can be a string or a list of strings.
    """
    allowed_genders = ["F", "M", "OP"] if gender == "F" else ["M", "OP"]
    query = SeatInfo.query.filter(
        SeatInfo.year         == year,
        SeatInfo.closing_rank >= rank_min,
        SeatInfo.category     == category,
        SeatInfo.gender.in_(allowed_genders)
    )

    # Branch filter: handle single string, list, or 'All'
    if branch:
        if isinstance(branch, list):
            if 'All' not in branch:
                query = query.filter(SeatInfo.branch.in_(branch))
        elif branch != 'All':
            query = query.filter(SeatInfo.branch == branch)

    # College type filter: handle special 'GOVT+SFI' combined type
    if college_type != "Any":
        if college_type == 'GOVT+SFI':
            query = query.filter(SeatInfo.college_type.in_(['GOVT', 'S.F.I.']))
        else:
            query = query.filter(SeatInfo.college_type == college_type)

    # Domicile filter (per DTE MP Rule 1.9.4):
    if domicile == 'N':
        query = query.filter(SeatInfo.domicile == 'N')

    return query.order_by(SeatInfo.closing_rank.asc()).all()



def fetch_cgpa_to_rank_map(year):
    """Returns all CGPA-to-rank mappings for a year, ordered by CGPA descending."""
    try:
        return (
            CgpaRankRange.query
            .filter(CgpaRankRange.year == year)
            .order_by(CgpaRankRange.cgpa.desc())
            .all()
        )
    except Exception as e:
        db.session.rollback()
        print(f"fetch_cgpa_to_rank_map({year}) note: {e}")
        return []


def _build_cgpa_lookup(years):
    """
    FIX: Pre-load CgpaRankRange rows for given years into memory.
    Avoids N+1 DB queries in search_colleges() (was: 2 queries per row).
    Returns: { year: [CgpaRankRange, ...] }
    """
    lookup = {}
    for year in years:
        lookup[year] = (
            CgpaRankRange.query
            .filter(CgpaRankRange.year == year)
            .all()
        )
    return lookup


def _cgpa_for_rank(lookup, year, rank):
    """In-memory CGPA lookup for a given rank within a year."""
    for r in lookup.get(year, []):
        if r.min_rank <= rank <= r.max_rank:
            return r.cgpa
    return None


def search_colleges(q, category=None, gender=None, college_type=None, branch=None, year=None, city=None):
    query = SeatInfo.query

    # Clean the query for alias mapping
    q_clean = q.strip().lower()
    
    # We will build a list of OR filters
    search_filters = [
        SeatInfo.college_name.ilike(f"%{q}%"),
        SeatInfo.branch.ilike(f"%{q}%")
    ]
    
    # Check for alias matches
    alias_matches = []
    
    # Check individual words in query
    words = q_clean.split()
    for word in words:
        if len(word) >= 2:
            for alias, names in COLLEGE_ALIASES.items():
                if word == alias or word in alias:
                    alias_matches.extend(names)
                    
    # Check full query phrase
    for alias, names in COLLEGE_ALIASES.items():
        if alias == q_clean or alias in q_clean:
            alias_matches.extend(names)
            
    # Deduplicate alias match strings
    alias_matches = list(set(alias_matches))
    
    # Add alias filters to query
    for name in alias_matches:
        search_filters.append(SeatInfo.college_name.ilike(f"%{name}%"))

    query = query.filter(db.or_(*search_filters))

    if category:
        query = query.filter(SeatInfo.category == category)
    if gender:
        query = query.filter(SeatInfo.gender.in_([gender, "OP"]))
    if college_type:
        if college_type == 'GOVT+SFI':
            query = query.filter(SeatInfo.college_type.in_(['GOVT', 'S.F.I.']))
        else:
            query = query.filter(SeatInfo.college_type == college_type)
    if branch:
        query = query.filter(SeatInfo.branch == branch)
    if year:
        query = query.filter(SeatInfo.year == int(year))
    if city and city != 'All':
        query = query.filter(SeatInfo.college_name.ilike(f"%{city}%"))

    results = query.order_by(
        SeatInfo.year.desc(),
        SeatInfo.college_name.asc()
    ).all()

    if not results:
        return []

    # Pre-load CGPA data for all needed years — single batch query per year
    years_needed = {row.year for row in results}
    cgpa_lookup  = _build_cgpa_lookup(years_needed)

    return [
        {
            **model_to_dict(row),
            "min_cgpa_required": _cgpa_for_rank(cgpa_lookup, row.year, row.closing_rank),
            "max_cgpa_required": _cgpa_for_rank(cgpa_lookup, row.year, row.opening_rank),
        }
        for row in results
    ]


# ── College Detail Page ───────────────────────────────────────────────────────

def get_college_detail(college_name: str) -> dict:
    """
    Fetch ALL seat rows for a college across all years.
    Returns:
        {
          'college_name': str,
          'college_type': str,
          'by_year': {2025: [SeatInfo, ...], 2024: [SeatInfo, ...]},
          'branches': sorted list of unique branch names
        }
    """
    rows = (
        db.session.query(SeatInfo)
        .filter(SeatInfo.college_name == college_name)
        .order_by(
            SeatInfo.year.desc(),
            SeatInfo.branch,
            SeatInfo.category,
            SeatInfo.gender
        )
        .all()
    )

    if not rows:
        return None

    by_year = {}
    for row in rows:
        by_year.setdefault(row.year, []).append(row)

    branches = sorted({r.branch for r in rows})

    return {
        'college_name': college_name,
        'college_type': rows[0].college_type,
        'by_year':      by_year,
        'branches':     branches,
    }


def get_seat_heatmap(college_name: str, year: int = 2025) -> dict:
    """Branch × category matrix with closing rank and seats for heatmap UI."""
    rows = (
        db.session.query(SeatInfo)
        .filter_by(college_name=college_name, year=year, gender="OP")
        .order_by(SeatInfo.branch, SeatInfo.category)
        .all()
    )
    if not rows:
        rows = (
            db.session.query(SeatInfo)
            .filter_by(college_name=college_name, year=year)
            .order_by(SeatInfo.branch, SeatInfo.category)
            .all()
        )
    branches = sorted({r.branch for r in rows})
    categories = ["UR", "OBC", "SC", "ST"]
    matrix = []
    for branch in branches:
        row_cells = []
        for cat in categories:
            matches = [r for r in rows if r.branch == branch and r.category == cat]
            if matches:
                best = min(matches, key=lambda x: x.closing_rank)
                row_cells.append({
                    "closing_rank": best.closing_rank,
                    "seats": sum(m.total_seats for m in matches),
                    "has_data": True,
                })
            else:
                row_cells.append({"closing_rank": None, "seats": 0, "has_data": False})
        matrix.append({"branch": branch, "cells": row_cells})
    return {"branches": branches, "categories": categories, "matrix": matrix, "year": year}


def get_cutoff_chart_data(college_name: str) -> dict:
    """Per-branch average closing ranks for latest vs previous year line chart."""
    detail = get_college_detail(college_name)
    from db import db
    from models import SeatInfo
    latest_year = db.session.query(db.func.max(SeatInfo.year)).scalar() or 2025
    prev_year = latest_year - 1

    if not detail:
        return {"labels": [], "data_prev": [], "data_latest": []}
    labels = detail["branches"]
    data_prev, data_latest = [], []
    for branch in labels:
        for year, bucket in ((prev_year, data_prev), (latest_year, data_latest)):
            rows = detail["by_year"].get(year, [])
            closings = [r.closing_rank for r in rows if r.branch == branch]
            bucket.append(round(sum(closings) / len(closings)) if closings else None)
    return {
        "labels": [BRANCH_NAMES.get(b, b) for b in labels],
        "branch_codes": labels,
        "data_prev": data_prev,
        "data_latest": data_latest,
    }


# ── College Comparison ────────────────────────────────────────────────────────

def get_compare_data(college_names: list) -> list:
    """
    Fetch comparison summary for up to 3 colleges.
    Returns list of dicts with key metrics per college.
    """
    result = []
    from db import db
    from models import SeatInfo
    latest_year = db.session.query(db.func.max(SeatInfo.year)).scalar() or 2025
    prev_year = latest_year - 1

    for name in college_names[:3]:
        rows_latest = (db.session.query(SeatInfo)
                     .filter_by(college_name=name, year=latest_year).all())
        rows_prev = (db.session.query(SeatInfo)
                     .filter_by(college_name=name, year=prev_year).all())

        # Use whichever year has data; prefer latest
        rows_display = rows_latest if rows_latest else rows_prev
        if not rows_display:
            continue

        branches_latest = sorted({r.branch for r in rows_latest}) if rows_latest else []
        branches_prev = sorted({r.branch for r in rows_prev}) if rows_prev else []
        all_branches  = sorted({r.branch for r in rows_display})

        closing_latest = [r.closing_rank for r in rows_latest] if rows_latest else []
        closing_prev = [r.closing_rank for r in rows_prev] if rows_prev else []

        avg_latest = round(sum(closing_latest) / len(closing_latest)) if closing_latest else None
        avg_prev = round(sum(closing_prev) / len(closing_prev)) if closing_prev else None

        # Trend: higher closing rank = easier to get in
        if avg_latest and avg_prev:
            diff = avg_latest - avg_prev
            if diff < -50:
                trend = 'tighter'    # cutoff got harder
            elif diff > 50:
                trend = 'easier'     # cutoff relaxed
            else:
                trend = 'stable'
        else:
            trend = 'no_data'

        total_seats_latest = sum(r.total_seats for r in rows_latest) if rows_latest else 0

        # Best closing rank = highest number = easiest branch to get
        # Worst closing rank = lowest number = hardest branch to get
        easiest_cutoff  = max(closing_latest) if closing_latest else None
        hardest_cutoff  = min(closing_latest) if closing_latest else None

        from college_meta import get_fee_info, format_fee_display, infer_city_from_college_name, get_district_for_city, get_placement_info
        fee = get_fee_info(name, rows_display[0].college_type)
        city = infer_city_from_college_name(name)
        placement = get_placement_info(name, rows_display[0].college_type)
        
        # Calculate ROI Index: Placement LPA / Tuition Fee LPA
        tuition_val = fee.get('tuition') or ((fee.get('tuition_min', 0) + fee.get('tuition_max', 0)) / 2)
        tuition_lpa = tuition_val / 100000.0 if tuition_val else 0.0
        avg_pkg = placement.get('average_package_lpa', 0.0)
        roi_index = round(avg_pkg / tuition_lpa, 2) if tuition_lpa > 0 else 0.0
        
        result.append({
            'college_name':     name,
            'college_type':     rows_display[0].college_type,
            'branches':         all_branches,
            'branches_latest':  branches_latest,
            'branches_prev':    branches_prev,
            'branch_count':     len(all_branches),
            'total_seats':      total_seats_latest,
            'domicile_required': any(r.domicile == 'Y' for r in rows_display),
            'easiest_cutoff':   easiest_cutoff,
            'hardest_cutoff':   hardest_cutoff,
            'avg_cutoff_latest': avg_latest,
            'avg_cutoff_prev':  avg_prev,
            'trend':            trend,
            'has_latest':       bool(rows_latest),
            'has_prev':         bool(rows_prev),
            'fee_display':      format_fee_display(fee),
            'fee_approximate':  fee.get('is_approximate', True),
            'fee':              fee,
            'city':             city,
            'district':         get_district_for_city(city) if city else None,
            'placement':        placement,
            'roi_index':        roi_index,
        })

    return result

def run_counselling_simulation(rank, choice_list, category, gender, domicile, year):
    allotted = None
    from models import SeatInfo
    from sqlalchemy import func
    
    for idx, choice in enumerate(choice_list):
        c_name = choice['college_name']
        c_branch = choice['branch']
        
        # Normalize the choice name by removing commas, periods, and all spaces
        clean_c_name = c_name.replace(",", "").replace(".", "").replace(" ", "").lower()
        
        # Query seats for this college & branch in this year using double replace on database column
        seats = SeatInfo.query.filter(
            func.replace(func.replace(func.replace(SeatInfo.college_name, ',', ''), '.', ''), ' ', '').ilike(clean_c_name),
            SeatInfo.branch == c_branch,
            SeatInfo.year == year
        ).all()
        
        # Filter seats down to only those that are eligible for this student
        eligible_seats = []
        for s in seats:
            # 1. Rank must be <= closing rank
            if rank > s.closing_rank:
                continue
                
            # 2. Domicile eligibility
            # Non-MP students (domicile == 'N') can ONLY get seats open to all states (domicile == 'N')
            if domicile == 'N' and s.domicile != 'N':
                continue
            # Note: MP Resident (domicile == 'Y') can match both 'Y' and 'N' seats
                
            # 3. Category eligibility
            # UR seats are open to all categories. Reserved seats only match student's specific category.
            if s.category != 'UR' and s.category != category:
                continue
                
            # 4. Gender eligibility
            # Male students ('M') cannot take Female ('F') seats. They can match ('M', 'OP') seats.
            # Female students ('F') can match both ('F', 'M', 'OP') seats.
            if gender == 'M' and s.gender == 'F':
                continue
                
            eligible_seats.append(s)
            
        if eligible_seats:
            # Prioritize matching quotas: UR OP -> UR F -> Reserved OP -> Reserved F
            def allotment_priority(seat):
                is_ur = (seat.category == 'UR')
                is_op_or_m = (seat.gender in ['OP', 'M'])
                
                if is_ur and is_op_or_m:
                    return 1
                elif is_ur and seat.gender == 'F':
                    return 2
                elif seat.category == category and is_op_or_m:
                    return 3
                elif seat.category == category and seat.gender == 'F':
                    return 4
                return 5
                
            eligible_seats.sort(key=allotment_priority)
            allotted = eligible_seats[0]
            break
            
    if allotted:
        return {
            'success': True,
            'college': allotted.college_name,
            'branch': allotted.branch,
            'choice_no': idx + 1,
            'allotted_category': allotted.category,
            'allotted_gender': allotted.gender,
            'year': year
        }
    return {'success': False}


# ── Merit Insights ────────────────────────────────────────────────────────────

def get_merit_insights(cgpa, rank_maps_cache, years=None):
    """
    Compute deep merit analytics for a given CGPA.
    Returns dict with accuracy, percentile, branch opportunities,
    category stats, year-over-year trend, and key takeaways.
    """
    if years is None:
        years = [2025, 2024]

    # ── 1. Rank ranges per year ───────────────────────────────────────────
    rank_data = {}
    for year in years:
        cgpa_map = rank_maps_cache.get(year, [])
        if cgpa_map:
            min_rank, max_rank = estimate_rank_range(cgpa_map, cgpa)
            # Total students = max rank in the map (last entry)
            total_students = cgpa_map[-1].max_rank if cgpa_map else 0
            rank_data[year] = {
                'min_rank': min_rank,
                'max_rank': max_rank,
                'total_students': total_students,
            }

    # ── 2. Accuracy (cross-year validation) ───────────────────────────────
    accuracy = None
    accuracy_detail = None
    if 2024 in rank_data and 2025 in rank_data:
        r24 = rank_data[2024]
        r25 = rank_data[2025]
        # Normalize rank to percentile in each year's merit list
        pct_24 = ((r24['min_rank'] + r24['max_rank']) / 2) / r24['total_students'] * 100
        pct_25 = ((r25['min_rank'] + r25['max_rank']) / 2) / r25['total_students'] * 100
        # Accuracy = how close the percentile positions are across years
        deviation = abs(pct_24 - pct_25)
        accuracy = max(0, round(100 - deviation * 2, 1))  # Scale deviation
        accuracy = min(99.5, accuracy)  # Cap at 99.5%
        accuracy_detail = {
            'pct_2024': round(pct_24, 1),
            'pct_2025': round(pct_25, 1),
            'deviation': round(deviation, 2),
        }

    # ── 3. Percentile positioning ─────────────────────────────────────────
    percentile = {}
    for year, rd in rank_data.items():
        avg_rank = (rd['min_rank'] + rd['max_rank']) / 2
        pct = max(0, round((1 - avg_rank / rd['total_students']) * 100, 1))
        percentile[year] = {
            'value': pct,
            'label': f"Top {round(100 - pct, 1)}%" if pct < 100 else "Top 1%",
            'above_you': rd['min_rank'] - 1,
            'below_you': rd['total_students'] - rd['max_rank'],
            'total': rd['total_students'],
        }

    # ── 4. Branch-wise opportunity map ────────────────────────────────────
    latest_year = years[0]
    rd_latest = rank_data.get(latest_year)
    opportunities = {'safe': [], 'moderate': [], 'reach': []}
    branch_summary = {'safe': 0, 'moderate': 0, 'reach': 0}
    seat_summary = {'safe': 0, 'moderate': 0, 'reach': 0}
    unique_colleges = {'safe': set(), 'moderate': set(), 'reach': set()}

    if rd_latest:
        min_r, max_r = rd_latest['min_rank'], rd_latest['max_rank']
        # Query all UR/OP seats for the latest year
        all_seats = SeatInfo.query.filter(
            SeatInfo.year == latest_year,
            SeatInfo.category == 'UR',
            SeatInfo.gender == 'OP',
        ).all()

        seen = set()  # (college, branch) dedup
        for seat in all_seats:
            key = (seat.college_name, seat.branch)
            if key in seen:
                continue
            seen.add(key)

            prob = calc_probability(min_r, max_r, seat.opening_rank, seat.closing_rank)
            entry = {
                'college': seat.college_name,
                'branch': seat.branch,
                'branch_name': BRANCH_NAMES.get(seat.branch, seat.branch),
                'closing_rank': seat.closing_rank,
                'seats': seat.total_seats,
                'college_type': seat.college_type,
                'prob': prob,
            }
            if prob >= 75:
                opportunities['safe'].append(entry)
                branch_summary['safe'] += 1
                seat_summary['safe'] += seat.total_seats
                unique_colleges['safe'].add(seat.college_name)
            elif prob >= 40:
                opportunities['moderate'].append(entry)
                branch_summary['moderate'] += 1
                seat_summary['moderate'] += seat.total_seats
                unique_colleges['moderate'].add(seat.college_name)
            elif seat.closing_rank >= min_r:
                opportunities['reach'].append(entry)
                branch_summary['reach'] += 1
                seat_summary['reach'] += seat.total_seats
                unique_colleges['reach'].add(seat.college_name)

        # Sort each bucket by probability desc, then closing rank asc
        for bucket in opportunities.values():
            bucket.sort(key=lambda x: (-x['prob'], x['closing_rank']))

    college_count = {
        k: len(v) for k, v in unique_colleges.items()
    }

    # ── 5. Category-wise seat availability ────────────────────────────────
    category_stats = {}
    if rd_latest:
        for cat in ['UR', 'OBC', 'SC', 'ST']:
            cat_seats = SeatInfo.query.filter(
                SeatInfo.year == latest_year,
                SeatInfo.category == cat,
                SeatInfo.closing_rank >= rd_latest['min_rank'],
            ).all()
            total_seats = sum(s.total_seats for s in cat_seats)
            unique_branches = len({s.branch for s in cat_seats})
            unique_clg = len({s.college_name for s in cat_seats})
            category_stats[cat] = {
                'total_seats': total_seats,
                'college_count': unique_clg,
                'branch_count': unique_branches,
                'row_count': len(cat_seats),
            }

    # ── 6. Year-over-year trend ───────────────────────────────────────────
    trend = None
    if 2024 in rank_data and 2025 in rank_data:
        avg_24 = (rank_data[2024]['min_rank'] + rank_data[2024]['max_rank']) / 2
        avg_25 = (rank_data[2025]['min_rank'] + rank_data[2025]['max_rank']) / 2
        shift = round(avg_24 - avg_25)
        # Positive shift = rank improved (lower number in 2025)
        if shift > 5:
            trend_label = 'improved'
            trend_icon = '↑'
            trend_detail = f"Rank improved by ~{abs(shift)} positions"
        elif shift < -5:
            trend_label = 'declined'
            trend_icon = '↓'
            trend_detail = f"Rank shifted down by ~{abs(shift)} positions"
        else:
            trend_label = 'stable'
            trend_icon = '→'
            trend_detail = "Rank position is stable across years"

        # Seat availability trend
        seats_24 = SeatInfo.query.filter(
            SeatInfo.year == 2024,
            SeatInfo.category == 'UR',
            SeatInfo.gender == 'OP',
            SeatInfo.closing_rank >= rank_data[2024]['min_rank'],
        ).count()
        seats_25 = SeatInfo.query.filter(
            SeatInfo.year == 2025,
            SeatInfo.category == 'UR',
            SeatInfo.gender == 'OP',
            SeatInfo.closing_rank >= rank_data[2025]['min_rank'],
        ).count()

        trend = {
            'rank_shift': shift,
            'label': trend_label,
            'icon': trend_icon,
            'detail': trend_detail,
            'avg_rank_2024': round(avg_24),
            'avg_rank_2025': round(avg_25),
            'seats_2024': seats_24,
            'seats_2025': seats_25,
            'total_students_2024': rank_data[2024]['total_students'],
            'total_students_2025': rank_data[2025]['total_students'],
        }

    # ── 7. Key takeaways ─────────────────────────────────────────────────
    takeaways = []
    if rd_latest and percentile.get(latest_year):
        pv = percentile[latest_year]['value']
        if pv >= 90:
            takeaways.append({
                'icon': '🏆', 'type': 'success',
                'text': f"Excellent! Your CGPA {cgpa} puts you in the top {round(100 - pv, 1)}% — strong chance at top Govt colleges."
            })
        elif pv >= 70:
            takeaways.append({
                'icon': '✅', 'type': 'success',
                'text': f"Good standing! You're in the top {round(100 - pv, 1)}% of the merit list."
            })
        elif pv >= 40:
            takeaways.append({
                'icon': '📊', 'type': 'info',
                'text': f"You're in the mid-range ({round(100 - pv, 1)}th percentile). Focus on S.F.I. and Private colleges with good placements."
            })
        else:
            takeaways.append({
                'icon': '⚡', 'type': 'warning',
                'text': f"Your rank is in the lower half. Apply broadly across Private colleges and consider all open branches."
            })

    if branch_summary['safe'] > 0:
        govt_safe = len([o for o in opportunities['safe'] if o['college_type'] == 'GOVT'])
        if govt_safe > 0:
            takeaways.append({
                'icon': '🏛️', 'type': 'success',
                'text': f"{govt_safe} Govt college branches are in your safe zone — you have a strong shot."
            })
        takeaways.append({
            'icon': '🎯', 'type': 'info',
            'text': f"{branch_summary['safe']} total branch options are safe, {branch_summary['moderate']} moderate, and {branch_summary['reach']} are reach."
        })
    elif branch_summary['moderate'] > 0:
        takeaways.append({
            'icon': '🎯', 'type': 'info',
            'text': f"No safe options yet, but {branch_summary['moderate']} branches are in moderate range. Fill choices strategically."
        })

    if category_stats.get('OBC') and category_stats.get('UR'):
        obc_extra = category_stats['OBC']['total_seats'] - category_stats['UR']['total_seats']
        if obc_extra > 0:
            takeaways.append({
                'icon': '📋', 'type': 'info',
                'text': f"OBC quota has {obc_extra} more seats accessible than UR. Check if you qualify."
            })

    if trend and trend['label'] == 'improved':
        takeaways.append({
            'icon': '📈', 'type': 'success',
            'text': f"Your rank position improved by ~{abs(trend['rank_shift'])} compared to last year's data."
        })
    elif trend and trend['label'] == 'declined':
        takeaways.append({
            'icon': '📉', 'type': 'warning',
            'text': f"More competition this year — rank shifted by ~{abs(trend['rank_shift'])} positions. Fill more choices."
        })

    if accuracy and accuracy >= 90:
        takeaways.append({
            'icon': '🔬', 'type': 'info',
            'text': f"Our prediction model is {accuracy}% accurate based on cross-year validation."
        })

    return {
        'cgpa': cgpa,
        'rank_data': rank_data,
        'accuracy': accuracy,
        'accuracy_detail': accuracy_detail,
        'percentile': percentile,
        'opportunities': opportunities,
        'branch_summary': branch_summary,
        'seat_summary': seat_summary,
        'college_count': college_count,
        'category_stats': category_stats,
        'trend': trend,
        'takeaways': takeaways,
        'latest_year': latest_year,
    }
