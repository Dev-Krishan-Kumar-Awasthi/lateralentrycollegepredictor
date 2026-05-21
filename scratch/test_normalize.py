import sys
sys.path.append('.')
from main import app
from smart_choices import build_smart_choices
from predictor import fetch_cgpa_to_rank_map

def normalize_name(name):
    if not name:
        return ""
    return " ".join(name.replace(",", " ").split()).lower().strip()

with app.app_context():
    RANK_MAPS_CACHE = {2025: fetch_cgpa_to_rank_map(2025)}
    result = build_smart_choices(
        8.5, ['CSE', 'IT'], 'UR', 'M', 'Any', 'Y', 'All',
        year=2025, rank_maps_cache=RANK_MAPS_CACHE,
        max_per_bucket=9999
    )
    
    best_choices_list = [
        {"sn": 1, "db_name": "Shri G.S. Institute of Technology & Science, Indore (M.P.) (1952)", "branch": "CSE"},
        {"sn": 2, "db_name": "Shri G.S. Institute of Technology & Science, Indore (M.P.) (1952)", "branch": "IT"},
        {"sn": 3, "db_name": "Institute of Engineering and Technology, DAVV, Indore (1996)", "branch": "CSE"},
        {"sn": 4, "db_name": "Institute of Engineering and Technology, DAVV, Indore (1996)", "branch": "IT"},
        {"sn": 5, "db_name": "Shri G.S. Institute of Technology & Science, Indore (M.P.) (1952)", "branch": "ET"},
        {"sn": 6, "db_name": "Institute of Engineering and Technology, DAVV, Indore (1996)", "branch": "ET"},
        {"sn": 7, "db_name": "JABALPUR ENGINEERING COLLEGE, JABALPUR, (JEC) (1947)", "branch": "CSE"},
        {"sn": 8, "db_name": "JABALPUR ENGINEERING COLLEGE, JABALPUR, (JEC) (1947)", "branch": "IT"},
        {"sn": 9, "db_name": "Shri G.S. Institute of Technology & Science, Indore (M.P.) (1952)", "branch": "EE"},
        {"sn": 10, "db_name": "Shri G.S. Institute of Technology & Science, Indore (M.P.) (1952)", "branch": "EI"},
        {"sn": 11, "db_name": "Shri G.S. Institute of Technology & Science, Indore (M.P.) (1952)", "branch": "MECH"},
        {"sn": 12, "db_name": "Institute of Engineering and Technology, DAVV, Indore (1996)", "branch": "EI"},
        {"sn": 13, "db_name": "Madhav Institute of Technology and Science, Gwalior (1957) (Deemed University)", "branch": "CSE"},
        {"sn": 14, "db_name": "Madhav Institute of Technology and Science, Gwalior (1957) (Deemed University)", "branch": "IT"},
        {"sn": 15, "db_name": "University Institute of Technology RGPV, Bhopal (1986)", "branch": "CSE"},
        {"sn": 16, "db_name": "University Institute of Technology RGPV, Bhopal (1986)", "branch": "IT"},
        {"sn": 17, "db_name": "Lakshmi Narain College of Technology, Bhopal (1994)", "branch": "CSE"},
        {"sn": 18, "db_name": "Acropolis Institute of Technology & Research, Indore (2005)", "branch": "CSE"},
        {"sn": 19, "db_name": "Acropolis Institute of Technology & Research, Indore (2005)", "branch": "IT"},
        {"sn": 20, "db_name": "Oriental Institute of Science & Technology, Bhopal (1995)", "branch": "CSE"},
        {"sn": 21, "db_name": "JABALPUR ENGINEERING COLLEGE, JABALPUR, (JEC) (1947)", "branch": "ET"},
        {"sn": 22, "db_name": "JABALPUR ENGINEERING COLLEGE, JABALPUR, (JEC) (1947)", "branch": "EE"},
        {"sn": 23, "db_name": "Madhav Institute of Technology and Science, Gwalior (1957) (Deemed University)", "branch": "ET"},
        {"sn": 24, "db_name": "Madhav Institute of Technology and Science, Gwalior (1957) (Deemed University)", "branch": "EE"},
        {"sn": 25, "db_name": "University Institute of Technology RGPV, Bhopal (1986)", "branch": "ET"},
        {"sn": 26, "db_name": "University Institute of Technology RGPV, Bhopal (1986)", "branch": "EE"},
        {"sn": 27, "db_name": "Shri G.S. Institute of Technology & Science, Indore (M.P.) (1952)", "branch": "CIVIL"},
        {"sn": 28, "db_name": "Institute of Engineering and Technology, DAVV, Indore (1996)", "branch": "CIVIL"},
        {"sn": 29, "db_name": "Samrat Ashok Technological Institute, Vidisha (1960)", "branch": "CSE"},
        {"sn": 30, "db_name": "Samrat Ashok Technological Institute, Vidisha (1960)", "branch": "IT"},
        {"sn": 31, "db_name": "IPS Academy, Institute of Engineering and Science, Indore (1999)", "branch": "CSE"},
        {"sn": 32, "db_name": "IPS Academy, Institute of Engineering and Science, Indore (1999)", "branch": "IT"},
        {"sn": 33, "db_name": "Lakshmi Narain College of Technology & Science, Bhopal (2006)", "branch": "CSE"},
        {"sn": 34, "db_name": "Lakshmi Narain College of Technology, Bhopal (1994)", "branch": "AIML"},
        {"sn": 35, "db_name": "Acropolis Institute of Technology & Research, Indore (2005)", "branch": "AIML"},
        {"sn": 36, "db_name": "Rewa Engineering College, Rewa (REC) (1964)", "branch": "CSE"},
        {"sn": 37, "db_name": "UJJAIN ENGINEERING COLLEGE (FORMERLY GOVT. ENGG. COLLEGE ESTB. IN 1966)", "branch": "CSE"}
    ]
    
    recommendation_map = {
        (normalize_name(item["db_name"]), item["branch"].strip().lower()): item["sn"]
        for item in best_choices_list
    }
    
    matched_count = 0
    for bucket in ('safe', 'target', 'dream'):
        # Annotate
        for item in result[bucket]:
            key = (normalize_name(item['college_name']), item['branch'].strip().lower())
            rec_sn = recommendation_map.get(key)
            item['in_recommendation'] = rec_sn is not None
            item['rec_sn'] = rec_sn if rec_sn is not None else 9999
        
        # Sort
        result[bucket].sort(key=lambda x: (
            0 if x.get('in_recommendation') else 1,
            x.get('rec_sn', 9999),
            -x['probability'],
            x['closing_rank']
        ))
        
        # Slice
        result[bucket] = result[bucket][:15]
        
        # Count and print matches
        for item in result[bucket]:
            if item.get('in_recommendation'):
                matched_count += 1
                print(f"Matched {item['college_name']} - {item['branch']} with rec sn {item['rec_sn']} in bucket {bucket}")
                
    print(f"Total matched after fix: {matched_count}")
