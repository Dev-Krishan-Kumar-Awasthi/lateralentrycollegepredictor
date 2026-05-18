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
        seen = set()
        deduped = []
        for c in colleges:
            key = (c['college_name'], c['branch'])
            if key not in seen:
                seen.add(key)
                deduped.append(c)
        return deduped

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
        
        # 3. Generate smart recommendations (options they have high/medium probability of getting)
        recommendations = []
        try:
            all_options = get_colleges(cgpa, 'All', category, gender, 'Any', domicile, 'All')
            seen_recommendations = set()
            choice_keys = {(c['college_name'], c['branch']) for c in choices}
            
            for yr in [2025, 2024]:
                if yr in all_options:
                    for item in all_options[yr]['colleges']:
                        col = item['college']
                        prob = item['probability']
                        if prob >= 50 and (col.college_name, col.branch) not in choice_keys:
                            key = (col.college_name, col.branch)
                            if key not in seen_recommendations:
                                seen_recommendations.add(key)
                                recommendations.append({
                                    'college_name': col.college_name,
                                    'branch': col.branch,
                                    'probability': prob,
                                    'college_type': col.college_type
                                })
                                if len(recommendations) >= 5:
                                    break
                if len(recommendations) >= 5:
                    break
        except Exception:
            pass  # Fail-safe: don't crash simulation if recommendations fail
            
        return render_template('simulator.html', result=sim_result, user=user_data, choices=choices, recommendations=recommendations)

    except Exception as e:
        return render_template('simulator.html', error=str(e))


@app.route('/recommendation-list')
def recommendation_list():
    # Pre-defined recommendation list of 37 colleges from 'recommendation choice'
    # mapped exactly to database-compatible names for seamless shortlist and simulator sync!
    best_choices = [
        {"sn": 1, "db_name": "Shri G.S. Institute of Technology & Science, Indore (M.P.) (1952)", "branch": "CSE", "display_name": "SGSITS Indore: CS"},
        {"sn": 2, "db_name": "Shri G.S. Institute of Technology & Science, Indore (M.P.) (1952)", "branch": "IT", "display_name": "SGSITS Indore: IT"},
        {"sn": 3, "db_name": "Institute of Engineering and Technology, DAVV, Indore (1996)", "branch": "CSE", "display_name": "IET DAVV Indore: CS"},
        {"sn": 4, "db_name": "Institute of Engineering and Technology, DAVV, Indore (1996)", "branch": "IT", "display_name": "IET DAVV Indore: IT"},
        {"sn": 5, "db_name": "Shri G.S. Institute of Technology & Science, Indore (M.P.) (1952)", "branch": "ET", "display_name": "SGSITS Indore: ETC"},
        {"sn": 6, "db_name": "Institute of Engineering and Technology, DAVV, Indore (1996)", "branch": "ET", "display_name": "IET DAVV Indore: ETC"},
        {"sn": 7, "db_name": "JABALPUR ENGINEERING COLLEGE, JABALPUR, (JEC) (1947)", "branch": "CSE", "display_name": "JEC Jabalpur: CS"},
        {"sn": 8, "db_name": "JABALPUR ENGINEERING COLLEGE, JABALPUR, (JEC) (1947)", "branch": "IT", "display_name": "JEC Jabalpur: IT"},
        {"sn": 9, "db_name": "Shri G.S. Institute of Technology & Science, Indore (M.P.) (1952)", "branch": "EE", "display_name": "SGSITS Indore: EE"},
        {"sn": 10, "db_name": "Shri G.S. Institute of Technology & Science, Indore (M.P.) (1952)", "branch": "EI", "display_name": "SGSITS Indore: E&I"},
        {"sn": 11, "db_name": "Shri G.S. Institute of Technology & Science, Indore (M.P.) (1952)", "branch": "MECH", "display_name": "SGSITS Indore: Mech."},
        {"sn": 12, "db_name": "Institute of Engineering and Technology, DAVV, Indore (1996)", "branch": "EI", "display_name": "IET DAVV Indore: E&I"},
        {"sn": 13, "db_name": "Madhav Institute of Technology and Science, Gwalior (1957) (Deemed University)", "branch": "CSE", "display_name": "MITS Gwalior: CS"},
        {"sn": 14, "db_name": "Madhav Institute of Technology and Science, Gwalior (1957) (Deemed University)", "branch": "IT", "display_name": "MITS Gwalior: IT"},
        {"sn": 15, "db_name": "University Institute of Technology RGPV, Bhopal (1986)", "branch": "CSE", "display_name": "UIT RGPV Bhopal: CS"},
        {"sn": 16, "db_name": "University Institute of Technology RGPV, Bhopal (1986)", "branch": "IT", "display_name": "UIT RGPV Bhopal: IT"},
        {"sn": 17, "db_name": "Lakshmi Narain College of Technology, Bhopal (1994)", "branch": "CSE", "display_name": "LNCT Bhopal [Main]: CS"},
        {"sn": 18, "db_name": "Acropolis Institute of Technology & Research, Indore (2005)", "branch": "CSE", "display_name": "Acropolis Indore: CS"},
        {"sn": 19, "db_name": "Acropolis Institute of Technology & Research, Indore (2005)", "branch": "IT", "display_name": "Acropolis Indore: IT"},
        {"sn": 20, "db_name": "Oriental Institute of Science & Technology, Bhopal (1995)", "branch": "CSE", "display_name": "Oriental Bhopal: CS/IT"},
        {"sn": 21, "db_name": "JABALPUR ENGINEERING COLLEGE, JABALPUR, (JEC) (1947)", "branch": "ET", "display_name": "JEC Jabalpur: ETC"},
        {"sn": 22, "db_name": "JABALPUR ENGINEERING COLLEGE, JABALPUR, (JEC) (1947)", "branch": "EE", "display_name": "JEC Jabalpur: EE"},
        {"sn": 23, "db_name": "Madhav Institute of Technology and Science, Gwalior (1957) (Deemed University)", "branch": "ET", "display_name": "MITS Gwalior: EC"},
        {"sn": 24, "db_name": "Madhav Institute of Technology and Science, Gwalior (1957) (Deemed University)", "branch": "EE", "display_name": "MITS Gwalior: EE"},
        {"sn": 25, "db_name": "University Institute of Technology RGPV, Bhopal (1986)", "branch": "ET", "display_name": "RGPV Bhopal: EC"},
        {"sn": 26, "db_name": "University Institute of Technology RGPV, Bhopal (1986)", "branch": "EE", "display_name": "RGPV Bhopal: EE"},
        {"sn": 27, "db_name": "Shri G.S. Institute of Technology & Science, Indore (M.P.) (1952)", "branch": "CIVIL", "display_name": "SGSITS Indore: Civil"},
        {"sn": 28, "db_name": "Institute of Engineering and Technology, DAVV, Indore (1996)", "branch": "CIVIL", "display_name": "IET DAVV Indore: Civil"},
        {"sn": 29, "db_name": "Samrat Ashok Technological Institute, Vidisha (1960)", "branch": "CSE", "display_name": "SATI Vidisha: CS"},
        {"sn": 30, "db_name": "Samrat Ashok Technological Institute, Vidisha (1960)", "branch": "IT", "display_name": "SATI Vidisha: IT"},
        {"sn": 31, "db_name": "IPS Academy, Institute of Engineering and Science, Indore (1999)", "branch": "CSE", "display_name": "IPS Indore: CS"},
        {"sn": 32, "db_name": "IPS Academy, Institute of Engineering and Science, Indore (1999)", "branch": "IT", "display_name": "IPS Indore: IT"},
        {"sn": 33, "db_name": "Lakshmi Narain College of Technology & Science, Bhopal (2006)", "branch": "CSE", "display_name": "LNCT Science: CS"},
        {"sn": 34, "db_name": "Lakshmi Narain College of Technology, Bhopal (1994)", "branch": "AIML", "display_name": "LNCT Main: CS SP."},
        {"sn": 35, "db_name": "Acropolis Institute of Technology & Research, Indore (2005)", "branch": "AIML", "display_name": "Acropolis: CS SP."},
        {"sn": 36, "db_name": "Rewa Engineering College, Rewa (REC) (1964)", "branch": "CSE", "display_name": "Rewa Engineering: CS"},
        {"sn": 37, "db_name": "UJJAIN ENGINEERING COLLEGE (FORMERLY GOVT. ENGG. COLLEGE ESTB. IN 1966)", "branch": "CSE", "display_name": "UGC: CS"},
    ]
    return render_template('recommendation_list.html', choices=best_choices)


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/faq')
def faq():
    return render_template('faq.html')


if __name__ == '__main__':
    app.run(debug=False)   # Never run debug=True in production