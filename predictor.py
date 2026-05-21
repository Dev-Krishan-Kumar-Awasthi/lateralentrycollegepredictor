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
    query = SeatInfo.query.filter(
        SeatInfo.year         == year,
        SeatInfo.closing_rank >= rank_min,
        SeatInfo.category     == category,
        SeatInfo.gender.in_([gender, "OP"])
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
    return (
        CgpaRankRange.query
        .filter(CgpaRankRange.year == year)
        .order_by(CgpaRankRange.cgpa.desc())
        .all()
    )


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
    """Per-branch average closing ranks for 2024 vs 2025 line chart."""
    detail = get_college_detail(college_name)
    if not detail:
        return {"labels": [], "data_2024": [], "data_2025": []}
    labels = detail["branches"]
    data_2024, data_2025 = [], []
    for branch in labels:
        for year, bucket in ((2024, data_2024), (2025, data_2025)):
            rows = detail["by_year"].get(year, [])
            closings = [r.closing_rank for r in rows if r.branch == branch]
            bucket.append(round(sum(closings) / len(closings)) if closings else None)
    return {
        "labels": [BRANCH_NAMES.get(b, b) for b in labels],
        "branch_codes": labels,
        "data_2024": data_2024,
        "data_2025": data_2025,
    }


# ── College Comparison ────────────────────────────────────────────────────────

def get_compare_data(college_names: list) -> list:
    """
    Fetch comparison summary for up to 3 colleges.
    Returns list of dicts with key metrics per college.
    """
    result = []

    for name in college_names[:3]:
        rows_2025 = (db.session.query(SeatInfo)
                     .filter_by(college_name=name, year=2025).all())
        rows_2024 = (db.session.query(SeatInfo)
                     .filter_by(college_name=name, year=2024).all())

        # Use whichever year has data; prefer 2025
        rows_latest = rows_2025 if rows_2025 else rows_2024
        if not rows_latest:
            continue

        branches_2025 = sorted({r.branch for r in rows_2025}) if rows_2025 else []
        branches_2024 = sorted({r.branch for r in rows_2024}) if rows_2024 else []
        all_branches  = sorted({r.branch for r in rows_latest})

        closing_2025 = [r.closing_rank for r in rows_2025] if rows_2025 else []
        closing_2024 = [r.closing_rank for r in rows_2024] if rows_2024 else []

        avg_2025 = round(sum(closing_2025) / len(closing_2025)) if closing_2025 else None
        avg_2024 = round(sum(closing_2024) / len(closing_2024)) if closing_2024 else None

        # Trend: higher closing rank = easier to get in
        if avg_2025 and avg_2024:
            diff = avg_2025 - avg_2024
            if diff < -50:
                trend = 'tighter'    # cutoff got harder
            elif diff > 50:
                trend = 'easier'     # cutoff relaxed
            else:
                trend = 'stable'
        else:
            trend = 'no_data'

        total_seats_2025 = sum(r.total_seats for r in rows_2025) if rows_2025 else 0

        # Best closing rank = highest number = easiest branch to get
        # Worst closing rank = lowest number = hardest branch to get
        easiest_cutoff  = max(closing_2025) if closing_2025 else None
        hardest_cutoff  = min(closing_2025) if closing_2025 else None

        from college_meta import get_fee_info, format_fee_display, infer_city_from_college_name, get_district_for_city, get_placement_info
        fee = get_fee_info(name, rows_latest[0].college_type)
        city = infer_city_from_college_name(name)
        placement = get_placement_info(name, rows_latest[0].college_type)
        result.append({
            'college_name':     name,
            'college_type':     rows_latest[0].college_type,
            'branches':         all_branches,
            'branches_2025':    branches_2025,
            'branches_2024':    branches_2024,
            'branch_count':     len(all_branches),
            'total_seats':      total_seats_2025,
            'domicile_required': any(r.domicile == 'Y' for r in rows_latest),
            'easiest_cutoff':   easiest_cutoff,
            'hardest_cutoff':   hardest_cutoff,
            'avg_cutoff_2025':  avg_2025,
            'avg_cutoff_2024':  avg_2024,
            'trend':            trend,
            'has_2025':         bool(rows_2025),
            'has_2024':         bool(rows_2024),
            'fee_display':      format_fee_display(fee),
            'fee_approximate':  fee.get('is_approximate', True),
            'fee':              fee,
            'city':             city,
            'district':         get_district_for_city(city) if city else None,
            'placement':        placement,
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
