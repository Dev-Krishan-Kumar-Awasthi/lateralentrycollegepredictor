from flask import Flask, render_template, request, redirect
from urllib.parse import quote as url_quote
from db import db
from predictor import (
    fetch_cgpa_to_rank_map, estimate_rank_range,
    fetch_colleges_from_rank, search_colleges,
    calc_probability, MP_CITIES, get_college_detail,
    BRANCH_NAMES, get_compare_data, run_counselling_simulation
)


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]  = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Jinja2 filter: URL-encode a string (for college name in query param)
app.jinja_env.filters['urlencode_val'] = lambda s: url_quote(str(s), safe='')
# Jinja2 filter: branch code → full name (fallback to original code)
app.jinja_env.filters['branch_name'] = lambda s: BRANCH_NAMES.get(str(s).strip(), s)

db.init_app(app)


# ── In-memory rank-map cache (loaded once at startup) ───────────────────────
RANK_MAPS_CACHE = {}
YEARS = [2025, 2024]

def fetch_rank_maps_cache():
    for year in YEARS:
        RANK_MAPS_CACHE[year] = fetch_cgpa_to_rank_map(year)


# ── Business logic helpers ───────────────────────────────────────────────────

def get_colleges(cgpa, branch, category, gender, college_type, domicile='Y', city='All'):
    result = {}
    for year in YEARS:
        cgpa_to_rank_map = RANK_MAPS_CACHE[year]
        min_rank, max_rank = estimate_rank_range(cgpa_to_rank_map, cgpa)
        raw_colleges = fetch_colleges_from_rank(
            min_rank, max_rank, branch, category, gender, college_type, year, domicile
        )

        # City filter (in-memory: city name appears in college_name)
        if city and city != 'All':
            raw_colleges = [c for c in raw_colleges
                            if city.lower() in c.college_name.lower()]

        # Attach probability to each college and sort by probability desc
        college_data = []
        for c in raw_colleges:
            prob = calc_probability(min_rank, max_rank, c.opening_rank, c.closing_rank)
            college_data.append({'college': c, 'probability': prob})

        college_data.sort(key=lambda x: x['probability'], reverse=True)

        result[year] = {
            'colleges':  college_data,
            'min_rank':  min_rank,
            'max_rank':  max_rank,
        }
    return result


def get_rank(cgpa):
    result = {}
    for year in YEARS:
        cgpa_to_rank_map = RANK_MAPS_CACHE[year]
        min_rank, max_rank = estimate_rank_range(cgpa_to_rank_map, cgpa)
        result[year] = {
            "min_rank": min_rank,
            "max_rank": max_rank,
        }
    return result


# ── Load cache on startup ────────────────────────────────────────────────────
with app.app_context():
    fetch_rank_maps_cache()


# ── Routes ───────────────────────────────────────────────────────────────────

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')


@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')


@app.route('/predictor', methods=['GET', 'POST'])
def predictor():
    if request.method == 'GET':
        # Pre-fill form from shared link query params
        prefill = {
            'cgpa':         request.args.get('cgpa', ''),
            'category':     request.args.get('category', ''),
            'gender':       request.args.get('gender', ''),
            'college_type': request.args.get('college_type', ''),
            'branch':       request.args.getlist('branch') if 'branch' in request.args else '',
            'domicile':     request.args.get('domicile', 'Y'),
            'city':         request.args.get('city', 'All'),
        }
        has_prefill = bool(prefill['cgpa'] and prefill['category'] and prefill['gender'])
        return render_template('predictor.html', data=None, prediction=None,
                               mp_cities=MP_CITIES, prefill=prefill, has_prefill=has_prefill)

    # ── Validate CGPA input ──
    try:
        raw = request.form.get('cgpa', '').strip()
        cgpa = float(raw)
        if not (0.0 <= cgpa <= 10.0):
            raise ValueError("CGPA must be between 0 and 10.")
    except ValueError:
        return render_template(
            'predictor.html',
            data=None,
            prediction=None,
            error="Invalid CGPA. Please enter a number between 0 and 10.",
            mp_cities=MP_CITIES,
            prefill=None,
            has_prefill=False
        )

    category     = request.form.get('category')
    gender       = request.form.get('gender')
    college_type = request.form.get('college_type')
    # Use getlist to handle multiple branch selections
    branch_list  = request.form.getlist('branch')
    domicile     = request.form.get('domicile', 'Y')
    city         = request.form.get('city', 'All')

    form_data = {
        'cgpa':         cgpa,
        'category':     category,
        'gender':       gender,
        'college_type': college_type,
        'branch':       branch_list,
        'domicile':     domicile,
        'city':         city,
    }

    prediction = get_colleges(cgpa, branch_list, category, gender, college_type, domicile, city)

    return render_template('predictor.html', data=form_data, prediction=prediction,
                           mp_cities=MP_CITIES, prefill=None, has_prefill=False)


@app.route('/schedule')
def schedule():
    return redirect('https://dte.mponline.gov.in', code=302)


@app.route('/college')
def college_detail_page():
    name = request.args.get('name', '').strip()
    if not name:
        return redirect('/predictor')
    detail = get_college_detail(name)
    if not detail:
        return render_template('college_detail.html', detail=None, college_name=name)
    return render_template('college_detail.html', detail=detail, college_name=name)


@app.route('/how-it-works')
def how_it_works():
    return render_template('how_it_works.html')


@app.route('/compare')
def compare():
    names = request.args.getlist('colleges')
    names = [n.strip() for n in names if n.strip()][:3]
    if len(names) < 2:
        return redirect('/predictor')
    data = get_compare_data(names)
    return render_template('compare.html', colleges=data,
                           branch_names=BRANCH_NAMES)


@app.route('/search')
def search():
    q            = request.args.get("q",            "").strip()
    category     = request.args.get("category",     "").strip()
    gender       = request.args.get("gender",       "").strip()
    college_type = request.args.get("college_type", "").strip()
    branch       = request.args.get("branch",       "").strip()
    city         = request.args.get("city",         "All").strip()
    year         = request.args.get("year",         "").strip()

    if not q:
        return render_template("search.html", data=None, colleges=None, mp_cities=MP_CITIES)

    data = {
        "q":            q,
        "category":     category,
        "gender":       gender,
        "college_type": college_type,
        "branch":       branch,
        "city":         city,
        "year":         year,
    }

    colleges = search_colleges(
        q=q,
        category=category     or None,
        gender=gender         or None,
        college_type=college_type or None,
        branch=branch         or None,
        year=year             or None,
        city=city             or None
    )

    if request.args.get('json'):
        from models import model_to_dict
        return [model_to_dict(c) for c in colleges]

    return render_template("search.html", data=data, colleges=colleges, mp_cities=MP_CITIES)


@app.route('/rank_predictor', methods=['GET', 'POST'])
def rank():
    if request.method == 'GET':
        return render_template('rank.html', data=None, prediction=None)

    # ── Validate CGPA input ──
    try:
        raw = request.form.get('cgpa', '').strip()
        cgpa = float(raw)
        if not (0.0 <= cgpa <= 10.0):
            raise ValueError("CGPA must be between 0 and 10.")
    except ValueError:
        return render_template(
            'rank.html',
            data=None,
            prediction=None,
            error="Invalid CGPA. Please enter a number between 0 and 10."
        )

    data = {"cgpa": cgpa}
    return render_template('rank.html', data=data, prediction=get_rank(cgpa))


@app.route('/simulator', methods=['GET', 'POST'])
def simulator():
    if request.method == 'GET':
        return render_template('simulator.html', result=None)

    # POST: Process simulation
    try:
        raw_cgpa = request.form.get('cgpa', '').strip()
        cgpa = float(raw_cgpa)
        category = request.form.get('category')
        gender = request.form.get('gender')
        domicile = request.form.get('domicile', 'Y')
        year = int(request.form.get('year', 2025))

        # Get prioritized choice list from hidden input (JSON)
        import json
        raw_choices = request.form.get('choice_list_json', '[]')
        choices = json.loads(raw_choices)
        
        if not choices:
            return render_template('simulator.html', error="Choice list khali hai! Pehle colleges add karein.")

        # 1. Estimate rank (using our existing logic)
        cgpa_to_rank_map = RANK_MAPS_CACHE[year]
        min_rank, max_rank = estimate_rank_range(cgpa_to_rank_map, cgpa)
        
        # Use average rank for a single simulation point
        avg_rank = (min_rank + max_rank) // 2

        # 2. Run simulation
        sim_result = run_counselling_simulation(avg_rank, choices, category, gender, domicile, year)
        
        user_data = {
            'cgpa': cgpa, 'rank': avg_rank, 'category': category, 
            'gender': gender, 'domicile': domicile, 'year': year
        }
        
        return render_template('simulator.html', result=sim_result, user=user_data, choices=choices)

    except Exception as e:
        return render_template('simulator.html', error=str(e))


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/faq')
def faq():
    return render_template('faq.html')


if __name__ == '__main__':
    app.run(debug=False)   # Never run debug=True in production