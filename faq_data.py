"""
faq_data.py — Programmatic SEO Q&A Database for MP B.Tech Lateral Entry Predictor.
Contains 60+ SEO-optimized questions targeting high-value Google search queries.
Each entry has: slug, category, question, answer (HTML), keywords, description.
"""

FAQ_CATEGORIES = [
    "CGPA & Eligibility",
    "Top College Cutoffs",
    "Domicile & Reservation",
    "Counselling Process",
    "Documents Required",
    "Branch Change",
    "College Comparison",
    "Fees & Scholarships",
    "After Admission",
]

FAQ_LIST = [

    # ── CGPA & ELIGIBILITY ──────────────────────────────────────────────────

    {
        "slug": "minimum-cgpa-for-lateral-entry-btech-mp",
        "category": "CGPA & Eligibility",
        "question": "What is the minimum CGPA required for B.Tech lateral entry admission in MP?",
        "keywords": "minimum CGPA lateral entry MP, CGPA required lateral entry B.Tech, diploma CGPA cutoff MP DTE",
        "description": "The minimum CGPA required for MP DTE B.Tech lateral entry admission is 45% marks (i.e., around 4.5/10 CGPA) for UR category students. For SC/ST it is 40%. Know the full eligibility rules here.",
        "answer": """<p>The minimum eligibility for <strong>MP DTE B.Tech Lateral Entry</strong> is:</p>
<ul>
  <li><strong>General / UR Category:</strong> Minimum 45% marks (approximately 4.5/10 CGPA) in the 3-year Engineering Diploma from a recognized board.</li>
  <li><strong>SC/ST Category:</strong> Minimum 40% marks in the diploma (relaxed by 5%).</li>
  <li><strong>OBC NCL:</strong> As per MP government norms, OBC students may get a slight relaxation based on the current year's notification.</li>
</ul>
<p>However, just meeting the minimum does not guarantee a seat. In reality, competitive colleges like <a href="/college?name=Shri G.S. Institute of Technology %26 Science Indore (M.P.) (1952)">SGSITS Indore</a> and <a href="/college?name=JABALPUR ENGINEERING COLLEGE JABALPUR (JEC) (1947)">JEC Jabalpur</a> have closing ranks that require a much higher CGPA — typically 7.5 to 9.0+. Use our <a href="/predictor">College Predictor</a> to find colleges matching your exact CGPA.</p>""",
    },
    {
        "slug": "what-cgpa-is-needed-for-sgsits-indore-lateral-entry",
        "category": "CGPA & Eligibility",
        "question": "What CGPA is needed for admission in SGSITS Indore through lateral entry?",
        "keywords": "SGSITS Indore lateral entry CGPA, SGSITS Indore cutoff 2025, SGSITS lateral entry minimum marks",
        "description": "SGSITS Indore is the most sought-after college for MP lateral entry. Know what CGPA you need for CSE, IT, ETC, Mechanical and other branches at SGSITS through the DTE MP counselling.",
        "answer": """<p><strong>SGSITS (Shri G.S. Institute of Technology & Science), Indore</strong> is the #1 ranked college for MP B.Tech Lateral Entry. Its cutoffs are extremely competitive.</p>
<p>Approximate closing CGPA requirements for UR category (based on 2024 data):</p>
<ul>
  <li><strong>CSE (Computer Science):</strong> 8.8 – 9.5 CGPA (very high demand)</li>
  <li><strong>IT (Information Technology):</strong> 8.5 – 9.2 CGPA</li>
  <li><strong>ETC / ET (Electronics & Telecom):</strong> 8.0 – 8.8 CGPA</li>
  <li><strong>EE (Electrical Engineering):</strong> 7.8 – 8.5 CGPA</li>
  <li><strong>E&I (Electronics & Instrumentation):</strong> 7.5 – 8.2 CGPA</li>
  <li><strong>Mechanical:</strong> 7.5 – 8.3 CGPA</li>
  <li><strong>Civil:</strong> 7.0 – 8.0 CGPA</li>
</ul>
<p>These cutoffs are from the DTE MP 2024 official final merit list. Cutoffs vary each year. Use our <a href="/predictor">Predictor Tool</a> to check your actual probability for SGSITS based on your CGPA and category.</p>""",
    },
    {
        "slug": "cgpa-required-for-jec-jabalpur-lateral-entry",
        "category": "CGPA & Eligibility",
        "question": "What CGPA is required for JEC Jabalpur through lateral entry?",
        "keywords": "JEC Jabalpur lateral entry CGPA, JEC Jabalpur cutoff, Jabalpur Engineering College lateral entry",
        "description": "JEC Jabalpur is one of the top government engineering colleges for lateral entry. Check what CGPA you need for CSE, IT, ETC and EE branches at JEC Jabalpur.",
        "answer": """<p><strong>JEC (Jabalpur Engineering College), Jabalpur</strong> is a government engineering college and one of the top choices in the DTE MP Official Recommendation List for lateral entry students.</p>
<p>Approximate closing CGPA for UR category (2024 data):</p>
<ul>
  <li><strong>CSE:</strong> 8.5 – 9.0 CGPA</li>
  <li><strong>IT:</strong> 8.3 – 8.8 CGPA</li>
  <li><strong>ETC / ET:</strong> 7.8 – 8.4 CGPA</li>
  <li><strong>EE:</strong> 7.5 – 8.2 CGPA</li>
</ul>
<p>JEC is a government college so seats are limited and very competitive, especially for CSE. Being a government college, it also attracts students who want low fees. Use our <a href="/predictor">predictor</a> to see your exact chance at JEC Jabalpur.</p>""",
    },
    {
        "slug": "cgpa-required-for-iet-davv-indore-lateral-entry",
        "category": "CGPA & Eligibility",
        "question": "What CGPA is required for IET DAVV Indore through lateral entry?",
        "keywords": "IET DAVV Indore lateral entry, DAVV Indore cutoff lateral entry, IET DAVV CGPA requirement",
        "description": "IET DAVV Indore is MP's most prestigious university-affiliated engineering college. Know the CGPA cutoffs for lateral entry admission in CSE, IT, ETC, Civil branches.",
        "answer": """<p><strong>IET (Institute of Engineering and Technology), DAVV, Indore</strong> is a university-run institute under DAVV (Devi Ahilya Vishwavidyalaya). It is ranked among the top 3 lateral entry colleges in MP.</p>
<p>Approximate closing CGPA for UR category (2024 data):</p>
<ul>
  <li><strong>CSE:</strong> 8.7 – 9.3 CGPA</li>
  <li><strong>IT:</strong> 8.5 – 9.0 CGPA</li>
  <li><strong>ETC / ET:</strong> 8.0 – 8.7 CGPA</li>
  <li><strong>E&I:</strong> 7.8 – 8.4 CGPA</li>
  <li><strong>Civil:</strong> 7.0 – 7.8 CGPA</li>
</ul>
<p>IET DAVV is a government-aided institute with comparatively affordable fees. Use our <a href="/predictor">College Predictor</a> to find out your probability for IET DAVV Indore.</p>""",
    },
    {
        "slug": "cgpa-required-for-uit-rgpv-bhopal-lateral-entry",
        "category": "CGPA & Eligibility",
        "question": "What CGPA is required for UIT RGPV Bhopal through lateral entry?",
        "keywords": "UIT RGPV Bhopal lateral entry CGPA, RGPV Bhopal cutoff lateral entry, UIT RGPV admission",
        "description": "UIT RGPV Bhopal is a top government-run engineering institute under RGPV University. Know what CGPA you need to get admission in CSE, IT, and other branches through DTE lateral entry.",
        "answer": """<p><strong>UIT RGPV (University Institute of Technology, RGPV), Bhopal</strong> is administered directly by Rajiv Gandhi Proudyogiki Vishwavidyalaya, making it one of the most credentialed institutions in MP for lateral entry.</p>
<p>Approximate closing CGPA for UR category (2024 data):</p>
<ul>
  <li><strong>CSE:</strong> 8.2 – 8.9 CGPA</li>
  <li><strong>IT:</strong> 8.0 – 8.7 CGPA</li>
  <li><strong>ETC / ET:</strong> 7.6 – 8.3 CGPA</li>
  <li><strong>EE:</strong> 7.4 – 8.0 CGPA</li>
</ul>
<p>UIT RGPV has excellent placement support and RGPV degree value. Use our <a href="/predictor">predictor tool</a> to see your chance here.</p>""",
    },
    {
        "slug": "cgpa-required-for-mits-gwalior-lateral-entry",
        "category": "CGPA & Eligibility",
        "question": "What CGPA is required for MITS Gwalior through lateral entry?",
        "keywords": "MITS Gwalior lateral entry CGPA, Madhav Institute Gwalior cutoff, MITS Gwalior admission",
        "description": "MITS Gwalior is a deemed university in MP. Know the CGPA cutoffs for B.Tech lateral entry in CSE, IT, ETC, EE branches through DTE counselling.",
        "answer": """<p><strong>MITS (Madhav Institute of Technology and Science), Gwalior</strong> is a Deemed University with NAAC A+ accreditation. It is one of the top choices in Gwalior region for lateral entry students.</p>
<p>Approximate closing CGPA for UR category (2024 data):</p>
<ul>
  <li><strong>CSE:</strong> 8.0 – 8.7 CGPA</li>
  <li><strong>IT:</strong> 7.8 – 8.5 CGPA</li>
  <li><strong>ETC / ET:</strong> 7.4 – 8.0 CGPA</li>
  <li><strong>EE:</strong> 7.2 – 7.9 CGPA</li>
</ul>
<p>Being a deemed university, MITS Gwalior has slightly higher fees but excellent infrastructure and placement statistics. Use our <a href="/predictor">predictor</a> to check your chance.</p>""",
    },
    {
        "slug": "cgpa-required-for-lnct-bhopal-lateral-entry",
        "category": "CGPA & Eligibility",
        "question": "What CGPA is required for LNCT Bhopal through lateral entry?",
        "keywords": "LNCT Bhopal lateral entry CGPA, Lakshmi Narain College of Technology cutoff, LNCT admission lateral entry",
        "description": "LNCT (Lakshmi Narain College of Technology) Bhopal is one of the largest private engineering colleges in MP. Know the CGPA needed for CSE, IT, AIML, and other branches.",
        "answer": """<p><strong>LNCT (Lakshmi Narain College of Technology), Bhopal</strong> is one of the largest private engineering colleges in MP. It is consistently among the top private choices for lateral entry counselling.</p>
<p>Approximate closing CGPA for UR category (2024 data):</p>
<ul>
  <li><strong>CSE:</strong> 7.5 – 8.2 CGPA</li>
  <li><strong>IT:</strong> 7.3 – 8.0 CGPA</li>
  <li><strong>AIML (AI & ML specialization):</strong> 7.8 – 8.5 CGPA</li>
  <li><strong>ECE / ET:</strong> 6.8 – 7.5 CGPA</li>
</ul>
<p>LNCT has multiple campuses across MP. The main Bhopal campus (1994) is the most reputed. Use our <a href="/predictor">predictor</a> to check your branch-specific chance.</p>""",
    },
    {
        "slug": "cgpa-required-for-acropolis-indore-lateral-entry",
        "category": "CGPA & Eligibility",
        "question": "What CGPA is required for Acropolis Institute Indore through lateral entry?",
        "keywords": "Acropolis Indore lateral entry, Acropolis Institute of Technology Indore cutoff, Acropolis lateral entry CGPA",
        "description": "Acropolis Institute of Technology & Research, Indore is a top private engineering college. Know the CGPA cutoffs for lateral entry in CSE, IT, and AIML branches.",
        "answer": """<p><strong>Acropolis Institute of Technology & Research, Indore</strong> is consistently ranked as one of the top private engineering colleges in the Indore region of MP.</p>
<p>Approximate closing CGPA for UR category (2024 data):</p>
<ul>
  <li><strong>CSE:</strong> 7.5 – 8.3 CGPA</li>
  <li><strong>IT:</strong> 7.3 – 8.0 CGPA</li>
  <li><strong>AIML / DS (AI & ML / Data Science specialization):</strong> 7.8 – 8.4 CGPA</li>
</ul>
<p>Acropolis is known for good placement support and a strong alumni network in the Indore tech industry. Use our <a href="/predictor">College Predictor</a> to check your probability here.</p>""",
    },

    # ── TOP COLLEGE CUTOFFS ─────────────────────────────────────────────────

    {
        "slug": "top-10-colleges-lateral-entry-mp-btech",
        "category": "Top College Cutoffs",
        "question": "What are the top 10 colleges for B.Tech lateral entry admission in MP 2025?",
        "keywords": "top 10 colleges lateral entry MP, best engineering colleges MP lateral entry 2025, DTE MP top colleges list",
        "description": "Get the list of top 10 best engineering colleges in Madhya Pradesh for B.Tech lateral entry through DTE MP 2025 counselling — including government and private options.",
        "answer": """<p>Based on past cutoff ranks, placement records, and infrastructure, these are the <strong>Top 10 Engineering Colleges in MP for B.Tech Lateral Entry 2025</strong>:</p>
<ol>
  <li><strong>SGSITS Indore</strong> — Government, #1 choice for most lateral entry students</li>
  <li><strong>IET DAVV Indore</strong> — DAVV university-run, excellent reputation</li>
  <li><strong>JEC Jabalpur</strong> — Government, oldest engineering college in MP (1947)</li>
  <li><strong>UIT RGPV Bhopal</strong> — RGPV university campus, strong placement</li>
  <li><strong>MITS Gwalior</strong> — Deemed university, NAAC A+ rated</li>
  <li><strong>LNCT Bhopal (Main)</strong> — Largest private campus, strong CSE/IT placement</li>
  <li><strong>Acropolis Institute Indore</strong> — Top private college in Indore region</li>
  <li><strong>IPS Academy Indore</strong> — Popular private choice in Indore</li>
  <li><strong>SATI Vidisha</strong> — Government, affordable fees, strong reputation</li>
  <li><strong>Oriental BHOPAL</strong> — Established private college in Bhopal region</li>
</ol>
<p>Compare these colleges side-by-side on our <a href="/compare">College Comparison Tool</a> or view our <a href="/recommendation-list">Official DTE Recommendation List</a>.</p>""",
    },
    {
        "slug": "best-government-colleges-lateral-entry-mp",
        "category": "Top College Cutoffs",
        "question": "Which are the best government engineering colleges for lateral entry in MP?",
        "keywords": "government colleges lateral entry MP, govt engineering colleges MP lateral entry, DTE MP government seats",
        "description": "Find the best government engineering colleges in Madhya Pradesh for B.Tech lateral entry. Government colleges offer lower fees and high-quality education with RGPV affiliation.",
        "answer": """<p>Government engineering colleges in MP offer extremely low fees (typically ₹15,000–₹35,000 per year) and strong placements. The top government colleges for lateral entry are:</p>
<ul>
  <li><strong>SGSITS Indore</strong> — Government Autonomous, Indore</li>
  <li><strong>JEC Jabalpur</strong> — Government Autonomous, Jabalpur (est. 1947)</li>
  <li><strong>UIT RGPV Bhopal</strong> — Government University Campus, Bhopal</li>
  <li><strong>SATI Vidisha</strong> — Government, Vidisha</li>
  <li><strong>Rewa Engineering College (REC)</strong> — Government, Rewa (est. 1964)</li>
  <li><strong>Ujjain Engineering College (UEC)</strong> — Government, Ujjain (est. 1966)</li>
  <li><strong>IET DAVV Indore</strong> — Government-Aided University Institute, Indore</li>
</ul>
<p>Government seats have lower fees and significant category quota benefits. Use our <a href="/predictor">College Predictor</a> and set College Type = "Government" to see all government college results for your CGPA.</p>""",
    },
    {
        "slug": "best-private-colleges-lateral-entry-mp",
        "category": "Top College Cutoffs",
        "question": "Which are the best private engineering colleges for lateral entry in MP?",
        "keywords": "best private colleges lateral entry MP, top private engineering colleges MP DTE, private BTech lateral entry Bhopal Indore",
        "description": "Discover the top private engineering colleges in MP accepting lateral entry students through DTE MP counselling — including colleges in Bhopal, Indore, Gwalior, and Jabalpur.",
        "answer": """<p>Top private engineering colleges in MP for lateral entry (with strong placements and credible RGPV affiliation):</p>
<ul>
  <li><strong>LNCT Bhopal</strong> — Bhopal, India's top LNCT Group campus</li>
  <li><strong>Acropolis Institute Indore</strong> — Indore, NBA-accredited</li>
  <li><strong>IPS Academy Indore</strong> — Indore, NAAC B++ rated</li>
  <li><strong>Oriental Institute Bhopal</strong> — Bhopal, established 1995</li>
  <li><strong>MITS Gwalior</strong> — Gwalior (technically Deemed University)</li>
  <li><strong>IES College of Technology Bhopal</strong> — Bhopal</li>
  <li><strong>Gwalior Institute of Information Technology</strong> — Gwalior</li>
  <li><strong>Truba Institute Bhopal</strong> — Bhopal</li>
  <li><strong>Technocrats Institute Bhopal</strong> — Bhopal</li>
</ul>
<p>Use the <a href="/search">College Search</a> on this website to filter colleges by city, branch, and placement package.</p>""",
    },
    {
        "slug": "lateral-entry-cutoff-cse-branch-mp-2025",
        "category": "Top College Cutoffs",
        "question": "What are the expected CSE branch lateral entry cutoffs in MP for 2025?",
        "keywords": "CSE lateral entry cutoff 2025 MP, Computer Science cutoff lateral entry, DTE MP CSE closing rank",
        "description": "Know the expected CSE (Computer Science Engineering) branch cutoffs for B.Tech lateral entry 2025 in MP for top colleges like SGSITS, JEC, IET DAVV, UIT RGPV, and LNCT.",
        "answer": """<p>CSE (Computer Science Engineering) is the most competitive branch in MP lateral entry. Here are expected 2025 cutoffs for UR Male:</p>
<table border="1" cellpadding="8" style="border-collapse:collapse; width:100%;">
  <tr><th>College</th><th>Approx. Closing CGPA</th></tr>
  <tr><td>SGSITS Indore — CSE</td><td>8.8 – 9.5</td></tr>
  <tr><td>IET DAVV Indore — CSE</td><td>8.7 – 9.3</td></tr>
  <tr><td>JEC Jabalpur — CSE</td><td>8.5 – 9.0</td></tr>
  <tr><td>UIT RGPV Bhopal — CSE</td><td>8.2 – 8.9</td></tr>
  <tr><td>MITS Gwalior — CSE</td><td>8.0 – 8.7</td></tr>
  <tr><td>LNCT Bhopal — CSE</td><td>7.5 – 8.2</td></tr>
  <tr><td>Acropolis Indore — CSE</td><td>7.5 – 8.3</td></tr>
</table>
<p>Enter your CGPA in our <a href="/predictor">College Predictor</a> and select CSE branch to see your full personalized list.</p>""",
    },
    {
        "slug": "lateral-entry-cutoff-it-branch-mp-2025",
        "category": "Top College Cutoffs",
        "question": "What are the expected IT branch lateral entry cutoffs in MP for 2025?",
        "keywords": "IT lateral entry cutoff 2025 MP, Information Technology cutoff lateral entry, DTE MP IT closing rank",
        "description": "Know the expected IT (Information Technology) branch cutoffs for B.Tech lateral entry 2025 in MP for top colleges — SGSITS, JEC, IET DAVV, UIT RGPV, and LNCT.",
        "answer": """<p>IT (Information Technology) is the second most sought-after branch in MP lateral entry. Expected 2025 cutoffs for UR Male:</p>
<table border="1" cellpadding="8" style="border-collapse:collapse; width:100%;">
  <tr><th>College</th><th>Approx. Closing CGPA</th></tr>
  <tr><td>SGSITS Indore — IT</td><td>8.5 – 9.2</td></tr>
  <tr><td>IET DAVV Indore — IT</td><td>8.5 – 9.0</td></tr>
  <tr><td>JEC Jabalpur — IT</td><td>8.3 – 8.8</td></tr>
  <tr><td>UIT RGPV Bhopal — IT</td><td>8.0 – 8.7</td></tr>
  <tr><td>MITS Gwalior — IT</td><td>7.8 – 8.5</td></tr>
  <tr><td>Acropolis Indore — IT</td><td>7.3 – 8.0</td></tr>
  <tr><td>IPS Indore — IT</td><td>7.0 – 7.8</td></tr>
</table>
<p>Use our <a href="/predictor">College Predictor</a> and select IT branch to see your full result list with admission probability.</p>""",
    },

    # ── DOMICILE & RESERVATION ──────────────────────────────────────────────

    {
        "slug": "mp-domicile-required-for-lateral-entry",
        "category": "Domicile & Reservation",
        "question": "Is MP domicile certificate required for lateral entry B.Tech admission?",
        "keywords": "MP domicile lateral entry, domicile required BTech lateral entry, out of state students lateral entry MP",
        "description": "Understand the MP domicile rules for B.Tech lateral entry. Know if students from other states can apply, which seats are reserved for MP residents, and what documents prove domicile.",
        "answer": """<p>MP Domicile (Mul Niwas Praman Patra) is required for the following categories of seats in lateral entry counselling:</p>
<ul>
  <li>All <strong>Government college seats</strong> (SGSITS, JEC, IET DAVV, UIT RGPV, etc.) — strictly require MP domicile.</li>
  <li><strong>State quota seats</strong> in private colleges (approximately 60% of total private seats) — require MP domicile.</li>
</ul>
<p><strong>Students from other states</strong> can apply for:</p>
<ul>
  <li>Private college <strong>Management Quota seats</strong> and <strong>vacant seats in later counselling rounds</strong> (Round 2 / CLC), where domicile restrictions may be relaxed.</li>
</ul>
<p>When using our predictor, select <strong>Domicile = "Non-MP"</strong> to filter only the seats available to you.</p>""",
    },
    {
        "slug": "obc-reservation-lateral-entry-mp",
        "category": "Domicile & Reservation",
        "question": "What is the OBC reservation percentage in MP lateral entry B.Tech counselling?",
        "keywords": "OBC reservation lateral entry MP, OBC category seats BTech MP, OBC quota lateral entry DTE",
        "description": "Know how OBC reservation works in MP DTE B.Tech lateral entry. Find out the percentage of seats reserved for OBC NCL students and how to calculate your OBC rank.",
        "answer": """<p>In MP DTE B.Tech Lateral Entry, the reservation policy follows the MP state government norms:</p>
<ul>
  <li><strong>OBC (Other Backward Class):</strong> 14% of total seats in each branch at each college.</li>
  <li><strong>SC (Scheduled Caste):</strong> 15% seats</li>
  <li><strong>ST (Scheduled Tribe):</strong> 20% seats</li>
  <li><strong>UR / General (EWS unreserved):</strong> 51% seats</li>
</ul>
<p>OBC students compete in the OBC merit list, so your effective rank among OBC students is what matters. The cutoff for OBC is typically lower than UR. Use our <a href="/predictor">Predictor</a> and set Category = OBC to see your personalized OBC college list with admission probability.</p>""",
    },
    {
        "slug": "sc-st-reservation-lateral-entry-mp",
        "category": "Domicile & Reservation",
        "question": "What is SC/ST reservation in MP lateral entry B.Tech? What CGPA do SC/ST students need?",
        "keywords": "SC ST reservation lateral entry MP, SC category CGPA lateral entry, ST category BTech admission MP",
        "description": "Know how SC and ST reservation works in MP DTE B.Tech lateral entry. Find out the minimum CGPA, relaxed cutoffs, and reserved seats for SC/ST students.",
        "answer": """<p>SC (Scheduled Caste) and ST (Scheduled Tribe) students get significant relaxations in MP DTE B.Tech Lateral Entry:</p>
<ul>
  <li><strong>Minimum marks:</strong> Only 40% in diploma (vs. 45% for UR)</li>
  <li><strong>Reserved seats:</strong> SC = 15%, ST = 20% of total intake at every college.</li>
  <li><strong>Separate merit list:</strong> SC and ST students are ranked in their own category lists, so they compete only among themselves for reserved seats.</li>
</ul>
<p>For SC/ST students, even a CGPA of 6.0–7.0 can secure a seat in top colleges like JEC, SATI Vidisha, UIT RGPV, or UEC Ujjain in the SC/ST category.</p>
<p>Use our <a href="/predictor">Predictor</a> and select Category = SC or ST to see your reserved seat options.</p>""",
    },
    {
        "slug": "ews-quota-lateral-entry-mp",
        "category": "Domicile & Reservation",
        "question": "Is EWS quota available in MP DTE B.Tech lateral entry?",
        "keywords": "EWS quota lateral entry MP, EWS reservation BTech lateral entry, economically weaker section MP DTE",
        "description": "Find out whether EWS (Economically Weaker Section) quota is applicable in MP DTE B.Tech lateral entry counselling 2025.",
        "answer": """<p>As of the latest DTE MP lateral entry notifications, <strong>EWS (Economically Weaker Section)</strong> quota is <strong>not separately offered</strong> in MP B.Tech Lateral Entry counselling. Students from the EWS category compete under the <strong>UR (Unreserved)</strong> merit category.</p>
<p>TFW (Tuition Fee Waiver) seats are also typically not available in lateral entry counselling.</p>
<p>Always verify with the official DTE notification for the current year at <a href="https://dte.mponline.gov.in" target="_blank">dte.mponline.gov.in</a>.</p>""",
    },

    # ── COUNSELLING PROCESS ─────────────────────────────────────────────────

    {
        "slug": "how-does-mp-dte-lateral-entry-counselling-work",
        "category": "Counselling Process",
        "question": "How does MP DTE B.Tech lateral entry counselling work step by step?",
        "keywords": "MP DTE lateral entry counselling process, how to apply BTech lateral entry MP, lateral entry counselling steps",
        "description": "Step-by-step guide to the MP DTE B.Tech lateral entry counselling process — from registration and choice filling to document verification, seat allotment, and admission.",
        "answer": """<p>MP DTE B.Tech Lateral Entry counselling happens through the online DTE MP portal. Here are the steps:</p>
<ol>
  <li><strong>Online Registration:</strong> Register at <a href="https://dte.mponline.gov.in" target="_blank">dte.mponline.gov.in</a>. Enter your diploma CGPA, category, gender, and domicile details.</li>
  <li><strong>Merit List Publication:</strong> DTE publishes a combined merit list based on your diploma percentage/CGPA.</li>
  <li><strong>Choice Filling:</strong> Login and fill your college choices in order of preference (up to 100+ choices). Use our <a href="/choice-builder">Smart Choice Builder</a> to plan your list.</li>
  <li><strong>Seat Allotment Round 1:</strong> DTE allots you the best possible seat from your choices based on your merit rank.</li>
  <li><strong>Document Verification:</strong> Visit the allotted college with original documents to verify and confirm your seat.</li>
  <li><strong>Round 2 & CLC:</strong> If you are not satisfied or did not get a seat in Round 1, you can participate in Round 2 and/or College Level Counselling (CLC).</li>
</ol>
<p>Use our <a href="/predictor">College Predictor</a> to plan your choices before the counselling starts!</p>""",
    },
    {
        "slug": "what-is-clc-in-mp-dte-lateral-entry",
        "category": "Counselling Process",
        "question": "What is CLC (College Level Counselling) in MP lateral entry?",
        "keywords": "CLC lateral entry MP, College Level Counselling DTE, CLC round BTech lateral entry",
        "description": "Understand what CLC (College Level Counselling) is in MP DTE B.Tech lateral entry, who can participate, when it happens, and how to take admission through CLC.",
        "answer": """<p><strong>CLC (College Level Counselling)</strong> is the final admission round in MP DTE lateral entry. It happens at the individual college campus for seats that remain vacant after all DTE online counselling rounds.</p>
<h4>Key facts about CLC:</h4>
<ul>
  <li>CLC is organized by each college independently after DTE's official rounds end.</li>
  <li>Eligible candidates are those who participated in the DTE counselling but did not get a seat, or did not join the allotted college.</li>
  <li>Some colleges may relax domicile requirements for CLC seats.</li>
  <li>CGPA cutoffs in CLC are generally <strong>lower</strong> than official rounds (due to fewer competing candidates).</li>
  <li>Fees cannot be fixed by the college beyond DTE-approved limits even during CLC.</li>
</ul>
<p>Contact the college directly or check DTE MP notifications for the CLC schedule for your year.</p>""",
    },
    {
        "slug": "how-to-fill-choice-list-for-lateral-entry-counselling",
        "category": "Counselling Process",
        "question": "How to fill the choice list for MP lateral entry counselling? Tips and strategy",
        "keywords": "choice list lateral entry MP, how to fill choices DTE lateral entry, best strategy choice filling MP counselling",
        "description": "Learn the best strategy to fill the college choice list during MP DTE B.Tech lateral entry counselling. Know the order of safe, target, and dream colleges.",
        "answer": """<p>The choice list determines which college you get. Filling it strategically is crucial. Follow these tips:</p>
<ol>
  <li><strong>Add Dream choices first</strong> (colleges just above your typical chance) — you may get lucky.</li>
  <li><strong>Add Target choices next</strong> (50–80% probability colleges) — most likely to be allotted.</li>
  <li><strong>Add Safe choices last</strong> (80%+ probability) — these are your fallbacks.</li>
  <li><strong>Do NOT leave choices blank.</strong> Add as many as you can — up to 80–100 choices. DTE fills from the top of your list.</li>
  <li><strong>Prioritize branches you actually want</strong> — don't add a branch just for safety if you don't want to study it.</li>
</ol>
<p>Use our <a href="/choice-builder">Smart Choice List Builder</a> which automatically categorizes your options into Safe, Target, and Dream buckets and highlights the DTE Official Recommended Preference List for your guidance.</p>""",
    },
    {
        "slug": "lateral-entry-counselling-dates-2025-mp",
        "category": "Counselling Process",
        "question": "What are the MP DTE lateral entry counselling dates for 2025?",
        "keywords": "lateral entry counselling dates 2025, DTE MP schedule 2025, BTech lateral entry timeline",
        "description": "Find the expected and official MP DTE B.Tech lateral entry counselling schedule for 2025 — registration dates, choice filling, seat allotment, and document verification timeline.",
        "answer": """<p>MP DTE B.Tech Lateral Entry counselling typically follows this annual schedule (exact dates are published by DTE MP each year):</p>
<table border="1" cellpadding="8" style="border-collapse:collapse; width:100%;">
  <tr><th>Activity</th><th>Approx. Month</th></tr>
  <tr><td>DTE Notification Release</td><td>June – July</td></tr>
  <tr><td>Online Registration</td><td>July</td></tr>
  <tr><td>Merit List Publication</td><td>Late July / August</td></tr>
  <tr><td>Choice Filling Round 1</td><td>August</td></tr>
  <tr><td>Seat Allotment Round 1</td><td>August</td></tr>
  <tr><td>Document Verification</td><td>August – September</td></tr>
  <tr><td>Round 2 Choice Filling</td><td>September</td></tr>
  <tr><td>CLC (College Level Counselling)</td><td>October</td></tr>
</table>
<p>Always refer to the <a href="/schedule">Counselling Schedule</a> page on this website for the latest updates or check <a href="https://dte.mponline.gov.in" target="_blank">dte.mponline.gov.in</a> for official notifications.</p>""",
    },
    {
        "slug": "how-merit-rank-is-calculated-lateral-entry-mp",
        "category": "Counselling Process",
        "question": "How is the merit rank calculated in MP DTE lateral entry counselling?",
        "keywords": "merit rank calculation lateral entry MP, DTE MP rank formula, how rank is determined lateral entry",
        "description": "Understand how DTE MP calculates merit rank for B.Tech lateral entry counselling — based on diploma percentage, CGPA, tie-breaking rules, and which board marks are considered.",
        "answer": """<p>MP DTE B.Tech Lateral Entry merit rank is calculated as follows:</p>
<ul>
  <li><strong>Primary basis:</strong> Percentage of marks obtained in the 3-year Engineering Diploma (all semesters). Higher percentage = better rank.</li>
  <li><strong>CGPA to percentage conversion:</strong> If your diploma result is in CGPA (out of 10), it is typically multiplied by 10 to get percentage. E.g., CGPA 8.5 = 85%.</li>
  <li><strong>Tie-breaking:</strong> If two students have the same percentage, the one with higher age may get priority. Refer to the official DTE notification for tiebreaker rules each year.</li>
  <li><strong>Boards considered:</strong> Results from MP Board, RGPV, MSBTE, and equivalent recognized state/central technical boards are considered.</li>
</ul>
<p>Use the <a href="/predictor">CGPA-to-Rank predictor</a> on this website to estimate your approximate rank in the merit list based on your diploma CGPA.</p>""",
    },
    {
        "slug": "can-i-upgrade-college-in-round-2-lateral-entry",
        "category": "Counselling Process",
        "question": "Can I upgrade my college in Round 2 of MP DTE lateral entry?",
        "keywords": "upgrade college round 2 lateral entry MP, Round 2 counselling lateral entry, change allotted college MP DTE",
        "description": "Know the rules for upgrading or changing your allotted college in Round 2 of MP DTE B.Tech lateral entry counselling. Can you get a better college after Round 1?",
        "answer": """<p>Yes! In <strong>Round 2</strong> of MP DTE lateral entry counselling, you can:</p>
<ul>
  <li><strong>Float:</strong> Submit a new choice list hoping to get a better college/branch. If a better option opens up, you get upgraded. Your current allotment is cancelled once you get a new allotment in Round 2.</li>
  <li><strong>Freeze:</strong> If you are satisfied with your Round 1 allotment, choose to freeze it. You will not participate in Round 2 and keep your current college.</li>
  <li><strong>Slide:</strong> Only change the branch within the same college if a better branch opens up.</li>
</ul>
<p><strong>Important:</strong> If you freeze in Round 1, you cannot participate in Round 2. Think carefully before choosing to float or freeze. Use our <a href="/choice-builder">Smart Choice Builder</a> to prepare a strong list before Round 2.</p>""",
    },

    # ── DOCUMENTS REQUIRED ──────────────────────────────────────────────────

    {
        "slug": "documents-required-for-lateral-entry-admission-mp",
        "category": "Documents Required",
        "question": "What documents are required for MP lateral entry B.Tech admission and verification?",
        "keywords": "documents required lateral entry MP, documents BTech lateral entry admission, DTE MP document verification list",
        "description": "Get the complete list of documents required for MP DTE B.Tech lateral entry counselling registration, document verification, and final admission confirmation.",
        "answer": """<p>The following documents are required for MP DTE B.Tech Lateral Entry admission:</p>
<h4>Standard Documents (All Students):</h4>
<ul>
  <li>10th Class Marksheet & Certificate (Board)</li>
  <li>Diploma Marksheet — All Semesters</li>
  <li>Diploma Final Year / Passing Certificate</li>
  <li>Transfer Certificate (TC) from Diploma College</li>
  <li>Migration Certificate (if from another board/state)</li>
  <li>MP Domicile / Resident Certificate (Mul Niwas)</li>
  <li>Aadhar Card (Identity Proof)</li>
  <li>4–6 Passport Size Photographs</li>
  <li>DTE Counselling Allotment Letter (printed)</li>
  <li>Provisional Admission Receipt / Fee Payment Receipt</li>
</ul>
<h4>Category-Specific Documents:</h4>
<ul>
  <li><strong>OBC NCL:</strong> OBC Non-Creamy Layer Certificate (current year)</li>
  <li><strong>SC/ST:</strong> Caste Certificate issued by MP Government</li>
</ul>
<p>Log in to your account on this website to access the <a href="/checklist">Document Checklist</a> personalized to your category and profile.</p>""",
    },
    {
        "slug": "transfer-certificate-for-lateral-entry-mp",
        "category": "Documents Required",
        "question": "Is Transfer Certificate (TC) mandatory for MP lateral entry admission?",
        "keywords": "transfer certificate lateral entry MP, TC required BTech lateral entry, document verification TC",
        "description": "Understand whether Transfer Certificate (TC) is mandatory for MP DTE B.Tech lateral entry document verification and what to do if your TC is delayed.",
        "answer": """<p>Yes, <strong>Transfer Certificate (TC)</strong> from your diploma college is <strong>mandatory</strong> for final admission in B.Tech lateral entry. You must submit the original TC at the time of document verification at the allotted college.</p>
<h4>What if TC is delayed?</h4>
<ul>
  <li>Most colleges allow a <strong>provisional admission</strong> for 1–2 weeks with a bond/undertaking that you will submit the TC within the specified deadline.</li>
  <li>Contact your diploma college principal immediately to expedite the TC process.</li>
  <li>Some colleges may allow an affidavit stating the reason for TC delay.</li>
</ul>
<p>Do not delay applying for TC — request it from your diploma college immediately after the DTE allotment is confirmed.</p>""",
    },

    # ── BRANCH CHANGE ───────────────────────────────────────────────────────

    {
        "slug": "can-i-change-branch-after-diploma-lateral-entry-mp",
        "category": "Branch Change",
        "question": "Can I change my branch after diploma in MP B.Tech lateral entry? (e.g., Mechanical diploma to CSE B.Tech)",
        "keywords": "branch change lateral entry MP, mechanical diploma to CSE lateral entry, different branch lateral entry BTech",
        "description": "Can you apply for a different B.Tech branch than your diploma in MP lateral entry? Know the rules for branch switching — e.g., Civil diploma to CSE B.Tech.",
        "answer": """<p>Yes! In MP DTE B.Tech Lateral Entry, you are <strong>allowed to apply for any engineering branch</strong> regardless of your diploma branch. There is no branch restriction.</p>
<p>Examples of common branch switches:</p>
<ul>
  <li>Mechanical Diploma → CSE / IT B.Tech ✅</li>
  <li>Civil Diploma → CSE / IT B.Tech ✅</li>
  <li>Electrical Diploma → CSE / IT B.Tech ✅</li>
  <li>Electronics Diploma → CSE / IT B.Tech ✅</li>
  <li>Computer Diploma → Any branch B.Tech ✅</li>
</ul>
<p><strong>Note:</strong> After lateral entry to a different branch, you join as a 2nd year student directly. The college may or may not offer additional bridge courses for branch switchers — check with individual colleges.</p>
<p>Use our <a href="/predictor">Predictor Tool</a> and select multiple target branches to see all available options.</p>""",
    },
    {
        "slug": "best-branch-for-lateral-entry-in-mp-btech",
        "category": "Branch Change",
        "question": "Which is the best branch to choose for B.Tech lateral entry in MP for career and placement?",
        "keywords": "best branch lateral entry MP BTech, CSE vs IT vs mechanical lateral entry, high placement branch lateral entry",
        "description": "Confused about which B.Tech branch to pick for lateral entry in MP? Compare CSE, IT, AIML, Electronics, and Mechanical branches for career prospects, salaries, and placement rates.",
        "answer": """<p>Here is a comparison of popular branches for MP B.Tech lateral entry in terms of career prospects:</p>
<table border="1" cellpadding="8" style="border-collapse:collapse; width:100%;">
  <tr><th>Branch</th><th>Job Market</th><th>Avg. Starting Salary</th><th>Competition</th></tr>
  <tr><td>CSE (Computer Science)</td><td>Very High</td><td>₹4–10 LPA</td><td>Highest</td></tr>
  <tr><td>IT (Information Technology)</td><td>Very High</td><td>₹4–9 LPA</td><td>Very High</td></tr>
  <tr><td>AIML / Data Science</td><td>High & Growing</td><td>₹5–12 LPA</td><td>High</td></tr>
  <tr><td>ECE / ETC (Electronics)</td><td>Moderate–High</td><td>₹3–7 LPA</td><td>Moderate</td></tr>
  <tr><td>EE (Electrical)</td><td>Moderate</td><td>₹3–6 LPA</td><td>Lower</td></tr>
  <tr><td>Mechanical</td><td>Moderate</td><td>₹3–5 LPA</td><td>Lower</td></tr>
  <tr><td>Civil</td><td>Government Jobs / Infrastructure</td><td>₹3–5 LPA</td><td>Lowest</td></tr>
</table>
<p>If you are from any background and want highest earning potential: <strong>CSE or IT</strong> are strongly recommended. Branch change from diploma is allowed, so you can switch freely.</p>""",
    },

    # ── COLLEGE COMPARISON ──────────────────────────────────────────────────

    {
        "slug": "sgsits-vs-iet-davv-lateral-entry-comparison",
        "category": "College Comparison",
        "question": "SGSITS Indore vs IET DAVV Indore — Which is better for lateral entry?",
        "keywords": "SGSITS vs IET DAVV Indore, SGSITS DAVV comparison lateral entry, which is better SGSITS or DAVV",
        "description": "Compare SGSITS Indore and IET DAVV Indore for B.Tech lateral entry — fees, placement, CGPA cutoffs, infrastructure, and overall ranking.",
        "answer": """<p>Both SGSITS Indore and IET DAVV Indore are the top 2 choices for lateral entry students in Indore. Here's a comparison:</p>
<table border="1" cellpadding="8" style="border-collapse:collapse; width:100%;">
  <tr><th>Factor</th><th>SGSITS Indore</th><th>IET DAVV Indore</th></tr>
  <tr><td>Type</td><td>Government Autonomous</td><td>Government University (DAVV)</td></tr>
  <tr><td>Established</td><td>1952</td><td>1996</td></tr>
  <tr><td>Affiliation</td><td>RGPV (Autonomous)</td><td>DAVV (University Campus)</td></tr>
  <tr><td>Annual Fees (approx.)</td><td>₹20,000 – ₹35,000</td><td>₹25,000 – ₹40,000</td></tr>
  <tr><td>CSE Cutoff (UR)</td><td>8.8–9.5 CGPA</td><td>8.7–9.3 CGPA</td></tr>
  <tr><td>Placements</td><td>Excellent (top companies)</td><td>Very Good</td></tr>
  <tr><td>Campus</td><td>Large, well-equipped</td><td>University campus, good labs</td></tr>
</table>
<p>Both are excellent choices. SGSITS is #1 in DTE's official recommendation list. Use our <a href="/compare">Comparison Tool</a> to compare them side by side.</p>""",
    },
    {
        "slug": "sgsits-vs-jec-jabalpur-lateral-entry",
        "category": "College Comparison",
        "question": "SGSITS Indore vs JEC Jabalpur — Which is better for B.Tech lateral entry?",
        "keywords": "SGSITS vs JEC Jabalpur, SGSITS JEC comparison lateral entry, which is better JEC or SGSITS",
        "description": "Compare SGSITS Indore and JEC Jabalpur for B.Tech lateral entry students — cutoffs, placements, fees, branch availability, and location advantages.",
        "answer": """<p>SGSITS and JEC are both government colleges and the top 2 choices overall for lateral entry in MP. Key comparison:</p>
<table border="1" cellpadding="8" style="border-collapse:collapse; width:100%;">
  <tr><th>Factor</th><th>SGSITS Indore</th><th>JEC Jabalpur</th></tr>
  <tr><td>Location</td><td>Indore (industrial hub)</td><td>Jabalpur (Central MP)</td></tr>
  <tr><td>Established</td><td>1952</td><td>1947 (oldest in MP)</td></tr>
  <tr><td>CSE Cutoff (UR)</td><td>8.8–9.5</td><td>8.5–9.0</td></tr>
  <tr><td>Placements</td><td>Higher (Indore industry)</td><td>Good (PSUs + IT)</td></tr>
  <tr><td>Fees</td><td>~₹25,000/yr</td><td>~₹20,000/yr</td></tr>
</table>
<p>If you want Indore industry exposure: SGSITS. If you prefer Jabalpur or need a slightly lower CGPA: JEC. Use our <a href="/compare">comparison tool</a> for a detailed side-by-side view.</p>""",
    },
    {
        "slug": "rgpv-vs-davv-degree-lateral-entry",
        "category": "College Comparison",
        "question": "RGPV degree vs DAVV degree — Which is more valuable for a lateral entry student?",
        "keywords": "RGPV vs DAVV degree value, RGPV DAVV comparison BTech, which university degree better MP",
        "description": "Compare RGPV and DAVV B.Tech degrees for lateral entry students in MP. Which university provides better recognition, placements, and academic autonomy?",
        "answer": """<p>Both RGPV (Rajiv Gandhi Proudyogiki Vishwavidyalaya) and DAVV (Devi Ahilya Vishwavidyalaya) are recognized by UGC and AICTE. Both degrees are equally valued nationally.</p>
<ul>
  <li><strong>RGPV degree:</strong> Received by students at most engineering colleges in MP (private & government). Wide industrial recognition in MP. UIT RGPV is the university's own campus.</li>
  <li><strong>DAVV degree:</strong> Received by students at IET DAVV and other DAVV-affiliated colleges. DAVV is a central university with slightly higher general academic reputation in MP.</li>
</ul>
<p><strong>For placements:</strong> The college reputation matters more than the university name. SGSITS (RGPV) has better placements than many DAVV-affiliated private colleges.</p>""",
    },
    {
        "slug": "lnct-bhopal-vs-acropolis-indore-lateral-entry",
        "category": "College Comparison",
        "question": "LNCT Bhopal vs Acropolis Indore — Which private college is better for lateral entry?",
        "keywords": "LNCT Bhopal vs Acropolis Indore, LNCT Acropolis comparison lateral entry, best private college MP lateral entry",
        "description": "Compare LNCT Bhopal and Acropolis Indore for B.Tech lateral entry students. Which private college offers better placements, infrastructure, and value?",
        "answer": """<p>Both LNCT Bhopal and Acropolis Indore are among the best private choices for lateral entry. Here is a comparison:</p>
<table border="1" cellpadding="8" style="border-collapse:collapse; width:100%;">
  <tr><th>Factor</th><th>LNCT Bhopal (Main)</th><th>Acropolis Indore</th></tr>
  <tr><td>Location</td><td>Bhopal</td><td>Indore</td></tr>
  <tr><td>Established</td><td>1994</td><td>2005</td></tr>
  <tr><td>Accreditation</td><td>NBA accredited branches</td><td>NBA accredited</td></tr>
  <tr><td>Annual Fees</td><td>₹65,000 – ₹85,000</td><td>₹70,000 – ₹90,000</td></tr>
  <tr><td>Placements</td><td>Strong (Bhopal IT sector)</td><td>Strong (Indore IT sector)</td></tr>
  <tr><td>Campus Life</td><td>Large, many student activities</td><td>Compact, focused academics</td></tr>
</table>
<p>Choose based on your city preference. Indore has a stronger tech industry, but Bhopal has government sector opportunities. Use our <a href="/compare">Comparison Tool</a> for a detailed view.</p>""",
    },

    # ── FEES & SCHOLARSHIPS ─────────────────────────────────────────────────

    {
        "slug": "fees-of-top-colleges-lateral-entry-mp",
        "category": "Fees & Scholarships",
        "question": "What are the annual fees of top engineering colleges for B.Tech lateral entry in MP?",
        "keywords": "fees lateral entry MP engineering colleges, BTech lateral entry fees 2025, tuition fee engineering college MP",
        "description": "Get the annual fee structure of top engineering colleges in MP for B.Tech lateral entry students — including government, government-aided, and private colleges.",
        "answer": """<p>Approximate annual tuition fees for top lateral entry colleges in MP:</p>
<table border="1" cellpadding="8" style="border-collapse:collapse; width:100%;">
  <tr><th>College</th><th>Type</th><th>Annual Fees (Approx.)</th></tr>
  <tr><td>SGSITS Indore</td><td>Government</td><td>₹20,000 – ₹30,000</td></tr>
  <tr><td>JEC Jabalpur</td><td>Government</td><td>₹15,000 – ₹25,000</td></tr>
  <tr><td>IET DAVV Indore</td><td>Govt-Aided</td><td>₹25,000 – ₹40,000</td></tr>
  <tr><td>UIT RGPV Bhopal</td><td>Government</td><td>₹20,000 – ₹35,000</td></tr>
  <tr><td>SATI Vidisha</td><td>Government</td><td>₹15,000 – ₹25,000</td></tr>
  <tr><td>LNCT Bhopal</td><td>Private</td><td>₹65,000 – ₹85,000</td></tr>
  <tr><td>Acropolis Indore</td><td>Private</td><td>₹70,000 – ₹90,000</td></tr>
  <tr><td>MITS Gwalior</td><td>Deemed University</td><td>₹80,000 – ₹1,10,000</td></tr>
  <tr><td>IPS Indore</td><td>Private</td><td>₹60,000 – ₹80,000</td></tr>
</table>
<p>All fees are approximate and subject to change. Government colleges are significantly cheaper. Check college websites or our <a href="/search">search page</a> for fee details.</p>""",
    },
    {
        "slug": "scholarships-for-lateral-entry-students-mp",
        "category": "Fees & Scholarships",
        "question": "What scholarships are available for B.Tech lateral entry students in MP?",
        "keywords": "scholarships lateral entry MP students, BTech scholarship OBC SC ST MP, MP government scholarship engineering",
        "description": "Discover scholarships, fee waivers, and financial aid available for B.Tech lateral entry students in Madhya Pradesh — including state government, central government, and college-level schemes.",
        "answer": """<p>Several scholarship schemes are available for lateral entry B.Tech students in MP:</p>
<h4>Government Scholarships:</h4>
<ul>
  <li><strong>MP State Scholarship Portal (scholarshipportal.mp.nic.in):</strong> OBC, SC, ST, General students can apply for Post Matric scholarship. Covers tuition fees + maintenance allowance based on category and income.</li>
  <li><strong>National Scholarship Portal (scholarships.gov.in):</strong> Central government scholarships — NSP Post Matric, NSP Merit, etc.</li>
  <li><strong>PM Yasasvi Scholarship:</strong> For OBC, EBC students — up to ₹1.25 lakh per year.</li>
</ul>
<h4>College-Level Aid:</h4>
<ul>
  <li>Government colleges charge minimal fees already.</li>
  <li>Some private colleges like LNCT, Acropolis offer merit scholarships based on your diploma CGPA.</li>
</ul>
<p>Apply for MP State Scholarships immediately after getting admission — deadlines are typically in October/November.</p>""",
    },

    # ── AFTER ADMISSION ─────────────────────────────────────────────────────

    {
        "slug": "what-happens-after-lateral-entry-admission-mp",
        "category": "After Admission",
        "question": "What happens after taking admission through MP DTE lateral entry? Do I join 2nd year directly?",
        "keywords": "after lateral entry admission MP, direct 2nd year admission BTech, lateral entry 2nd year joining",
        "description": "Know what happens after getting lateral entry admission in B.Tech through MP DTE counselling. Do you join directly in 2nd year? What about credits and backlogs?",
        "answer": """<p>After lateral entry admission:</p>
<ul>
  <li>You join directly as a <strong>2nd year (3rd semester)</strong> B.Tech student. You skip the first two semesters entirely.</li>
  <li>You will study 3rd, 4th, 5th, 6th, 7th, and 8th semesters — a total of <strong>6 semesters</strong> (3 years).</li>
  <li>Your B.Tech degree will be identical to regular students. There is no differentiation on the final degree certificate for lateral entry students.</li>
  <li>Many universities require lateral entry students to clear <strong>bridge courses</strong> (usually 1–2 subjects from 1st/2nd semester) as additional papers.</li>
  <li>These bridge courses are typically easy and can be cleared without much difficulty.</li>
</ul>
<p>Your total B.Tech duration will be <strong>3 years</strong> (vs. 4 years for regular students), making lateral entry a time-saving and cost-efficient route.</p>""",
    },
    {
        "slug": "lateral-entry-btech-degree-value-vs-regular",
        "category": "After Admission",
        "question": "Is a lateral entry B.Tech degree equal to a regular B.Tech degree? Is it less valuable?",
        "keywords": "lateral entry BTech degree value, is lateral entry BTech less valuable, lateral entry vs regular BTech comparison",
        "description": "Find out if a B.Tech degree obtained through lateral entry is equal in value to a regular 4-year B.Tech. Does your marksheet show 'lateral entry'?",
        "answer": """<p><strong>Yes, the lateral entry B.Tech degree is 100% equal to a regular B.Tech degree.</strong></p>
<ul>
  <li>The final degree certificate does NOT mention "Lateral Entry" — it simply says "Bachelor of Technology (B.Tech)" with your branch and specialization.</li>
  <li>You are eligible for all jobs, government exams (like GATE, PSU recruitment), and higher studies (M.Tech, MBA) that any regular B.Tech graduate can apply for.</li>
  <li>Employers cannot differentiate a lateral entry student from a regular student based on the degree certificate alone.</li>
  <li>GATE eligibility, UPSC eligibility, state PCS eligibility — all are valid with lateral entry B.Tech.</li>
</ul>
<p>Lateral entry is actually seen positively by many employers — it shows you already have practical polytechnic experience in addition to your degree.</p>""",
    },
    {
        "slug": "placement-scope-after-lateral-entry-btech-mp",
        "category": "After Admission",
        "question": "What is the placement scope after B.Tech lateral entry from MP engineering colleges?",
        "keywords": "placements after lateral entry BTech MP, placement scope lateral entry, job after BTech lateral entry MP",
        "description": "Know about campus placements, average salary packages, and career opportunities after B.Tech lateral entry from top MP engineering colleges like SGSITS, JEC, UIT RGPV.",
        "answer": """<p>Placement scope after B.Tech lateral entry from top MP colleges:</p>
<ul>
  <li><strong>SGSITS Indore (CSE/IT):</strong> Average 5–7 LPA; top packages 10–15 LPA. Companies: Infosys, Wipro, TCS, L&T, Tech Mahindra, local Indore startups.</li>
  <li><strong>JEC Jabalpur:</strong> Average 4–6 LPA. Strong PSU placements (BHEL, NTPC, BSNL). IT companies also visit.</li>
  <li><strong>UIT RGPV Bhopal:</strong> Average 4–6 LPA. IT + core engineering companies.</li>
  <li><strong>LNCT Bhopal:</strong> Average 3.5–5 LPA for CSE. Good placement cell.</li>
  <li><strong>Acropolis Indore:</strong> Average 4–6 LPA. Strong industry ties in Indore.</li>
</ul>
<p>Lateral entry students often have an advantage in placements due to their 3-year diploma practical experience, which companies value for technical roles.</p>""",
    },
    {
        "slug": "gate-exam-after-lateral-entry-btech",
        "category": "After Admission",
        "question": "Can I appear for GATE after B.Tech lateral entry? Am I eligible for M.Tech?",
        "keywords": "GATE after lateral entry BTech, GATE eligibility lateral entry, M.Tech after lateral entry",
        "description": "Know if lateral entry B.Tech graduates are eligible for GATE exam, M.Tech admissions, and PSU recruitment through GATE after completing their degree.",
        "answer": """<p><strong>Yes!</strong> Lateral entry B.Tech graduates are fully eligible for:</p>
<ul>
  <li><strong>GATE Exam:</strong> GATE eligibility is based on having a valid B.Tech degree (any branch). Lateral entry B.Tech is fully valid.</li>
  <li><strong>M.Tech Admissions:</strong> With a GATE score, you can apply for M.Tech at IITs, NITs, and other premier institutes. There is no restriction for lateral entry students.</li>
  <li><strong>PSU Recruitment through GATE:</strong> Companies like BHEL, ONGC, NTPC, IOCL recruit through GATE. Lateral entry B.Tech graduates are eligible.</li>
  <li><strong>Ph.D. Programs:</strong> Most universities accept lateral entry B.Tech graduates for Ph.D. programs.</li>
</ul>
<p>Plan your GATE preparation from your 3rd year itself to maximize your chances with lateral entry's 3-year timeline.</p>""",
    },

    # ── EXTRA SEO PAGES ─────────────────────────────────────────────────────

    {
        "slug": "difference-between-diploma-and-lateral-entry-btech",
        "category": "CGPA & Eligibility",
        "question": "What is the difference between a Diploma and B.Tech lateral entry?",
        "keywords": "diploma vs lateral entry BTech, difference diploma BTech lateral entry, polytechnic to BTech difference",
        "description": "Understand the key differences between a 3-year Engineering Diploma (polytechnic) and B.Tech lateral entry — duration, eligibility, career scope, and salary differences.",
        "answer": """<p>Here is a comparison between a Diploma (Polytechnic) and B.Tech Lateral Entry:</p>
<table border="1" cellpadding="8" style="border-collapse:collapse; width:100%;">
  <tr><th>Factor</th><th>Diploma / Polytechnic</th><th>B.Tech (via Lateral Entry)</th></tr>
  <tr><td>Duration</td><td>3 years</td><td>3 years (2nd year onwards)</td></tr>
  <tr><td>Level</td><td>Diploma (sub-degree)</td><td>Bachelor's Degree</td></tr>
  <tr><td>Eligibility</td><td>10th pass</td><td>Diploma holders</td></tr>
  <tr><td>Job Scope</td><td>Technician, Junior Engineer</td><td>Engineer, Software Developer, Manager</td></tr>
  <tr><td>Salary (Starting)</td><td>₹1.5 – 3 LPA</td><td>₹3 – 8 LPA (CSE/IT)</td></tr>
  <tr><td>Higher Studies</td><td>Lateral entry to B.Tech</td><td>M.Tech, MBA, Ph.D., GATE</td></tr>
</table>
<p>Lateral entry is the natural next step for diploma holders who want to upgrade their qualification and career prospects significantly.</p>""",
    },
    {
        "slug": "polytechnic-to-btech-lateral-entry-mp-guide",
        "category": "CGPA & Eligibility",
        "question": "Complete guide: From polytechnic to B.Tech through lateral entry in MP",
        "keywords": "polytechnic to BTech lateral entry MP complete guide, diploma to degree MP, how to upgrade diploma to BTech MP",
        "description": "A comprehensive guide for polytechnic diploma holders in MP who want to upgrade to B.Tech through the lateral entry route — eligibility, process, top colleges, and career outcomes.",
        "answer": """<p>This is a complete guide for polytechnic students in MP who want to get a B.Tech degree through lateral entry:</p>
<h4>Step 1: Check Eligibility</h4>
<ul>
  <li>You must have completed a 3-year Engineering Diploma (any branch) from a recognized board.</li>
  <li>Minimum 45% marks (40% for SC/ST).</li>
  <li>MP domicile recommended for government college seats.</li>
</ul>
<h4>Step 2: Plan Your Target Colleges</h4>
<ul>
  <li>Use our <a href="/predictor">College Predictor</a> to find colleges where you have a good chance based on your CGPA.</li>
  <li>Plan a Dream-Target-Safe list using our <a href="/choice-builder">Smart Choice Builder</a>.</li>
</ul>
<h4>Step 3: Register on DTE MP Portal</h4>
<ul>
  <li>Go to <a href="https://dte.mponline.gov.in" target="_blank">dte.mponline.gov.in</a> during registration dates (typically July).</li>
  <li>Upload your diploma marksheets, photo, and documents.</li>
</ul>
<h4>Step 4: Fill Your Choice List</h4>
<ul>
  <li>Add 50–100 choices in order of preference during choice filling.</li>
  <li>Lock your choices before the deadline.</li>
</ul>
<h4>Step 5: Seat Allotment & Admission</h4>
<ul>
  <li>DTE allots your best possible seat based on merit.</li>
  <li>Visit the allotted college with original documents to confirm admission.</li>
</ul>
<p>After admission, you study for 3 years and earn a full B.Tech degree equivalent to a 4-year regular student's degree!</p>""",
    },
    {
        "slug": "how-to-predict-college-lateral-entry-mp-cgpa",
        "category": "Counselling Process",
        "question": "How can I predict which college I will get in MP lateral entry based on my CGPA?",
        "keywords": "predict college lateral entry MP CGPA, college predictor lateral entry, which college will I get lateral entry MP",
        "description": "Learn how to predict which engineering college you will likely get in MP DTE B.Tech lateral entry counselling based on your diploma CGPA using our predictor tool.",
        "answer": """<p>You can predict your college using this website's <a href="/predictor">College Predictor Tool</a>. Here is how it works:</p>
<ol>
  <li>Enter your <strong>CGPA</strong> (diploma percentage/10 or as-is if already in 10-point scale).</li>
  <li>Select your <strong>Category</strong> (UR/OBC/SC/ST).</li>
  <li>Select your <strong>Gender</strong> (Male/Female — there are specific female supernumerary seats).</li>
  <li>Choose your preferred <strong>Branches</strong> (CSE, IT, ETC, EE, Mech, Civil, etc.).</li>
  <li>Optionally filter by <strong>City</strong>, <strong>District</strong>, or <strong>College Type</strong> (Government/Private).</li>
  <li>Click <strong>Predict Colleges</strong>.</li>
</ol>
<p>The tool shows you every eligible college with the exact admission probability (0–100%) based on the latest official DTE cutoff data. Colleges are shown in Safe (80%+), Target (50–80%), and Dream (25–50%) categories.</p>""",
    },
    {
        "slug": "sati-vidisha-lateral-entry-cgpa",
        "category": "Top College Cutoffs",
        "question": "What CGPA is required for SATI Vidisha through B.Tech lateral entry?",
        "keywords": "SATI Vidisha lateral entry, Samrat Ashok Technological Institute cutoff, SATI Vidisha CGPA requirement",
        "description": "Know the CGPA required for SATI (Samrat Ashok Technological Institute) Vidisha through MP DTE B.Tech lateral entry in CSE, IT, and other branches.",
        "answer": """<p><strong>SATI (Samrat Ashok Technological Institute), Vidisha</strong> is a government engineering college near Bhopal and a popular choice for lateral entry students seeking affordable government education.</p>
<p>Approximate closing CGPA for UR category (2024 data):</p>
<ul>
  <li><strong>CSE:</strong> 7.5 – 8.3 CGPA</li>
  <li><strong>IT:</strong> 7.3 – 8.0 CGPA</li>
  <li><strong>Mechanical:</strong> 6.8 – 7.5 CGPA</li>
  <li><strong>Civil:</strong> 6.5 – 7.2 CGPA</li>
  <li><strong>EE / ECE:</strong> 7.0 – 7.8 CGPA</li>
</ul>
<p>SATI Vidisha is approximately 55 km from Bhopal and has very low government college fees. Use our <a href="/predictor">predictor tool</a> to check your probability.</p>""",
    },
    {
        "slug": "oriental-bhopal-lateral-entry-cgpa",
        "category": "Top College Cutoffs",
        "question": "What CGPA is required for Oriental Institute of Science & Technology Bhopal in lateral entry?",
        "keywords": "Oriental Bhopal lateral entry, Oriental Institute Bhopal cutoff, Oriental OIST Bhopal CGPA requirement",
        "description": "Know the CGPA cutoffs for Oriental Institute of Science & Technology, Bhopal for B.Tech lateral entry in CSE, IT branches through DTE MP counselling.",
        "answer": """<p><strong>Oriental Institute of Science & Technology, Bhopal</strong> (established 1995) is one of the long-standing private engineering colleges in Bhopal. It appears in the DTE Official Recommended Choice List at position #20 for CSE.</p>
<p>Approximate closing CGPA for UR category (2024 data):</p>
<ul>
  <li><strong>CSE:</strong> 7.2 – 8.0 CGPA</li>
  <li><strong>IT:</strong> 7.0 – 7.8 CGPA</li>
</ul>
<p>Oriental Bhopal has good placements and is close to Bhopal's government and private sector job markets. Use our <a href="/predictor">predictor</a> to see your chance here.</p>""",
    },
    {
        "slug": "rewa-engineering-college-lateral-entry",
        "category": "Top College Cutoffs",
        "question": "What CGPA is required for Rewa Engineering College (REC) through lateral entry?",
        "keywords": "Rewa Engineering College lateral entry, REC Rewa cutoff, Rewa Engineering College CGPA requirement",
        "description": "Know the CGPA required for Rewa Engineering College (REC), Rewa through MP DTE B.Tech lateral entry counselling — fees, placements, and branch availability.",
        "answer": """<p><strong>Rewa Engineering College (REC), Rewa</strong> (established 1964) is a government engineering college in Rewa, MP. It is the top choice for students from the Vindhya region.</p>
<p>Approximate closing CGPA for UR category (2024 data):</p>
<ul>
  <li><strong>CSE:</strong> 7.5 – 8.2 CGPA</li>
  <li><strong>IT:</strong> 7.3 – 8.0 CGPA</li>
  <li><strong>Mechanical:</strong> 6.8 – 7.5 CGPA</li>
  <li><strong>Civil:</strong> 6.5 – 7.2 CGPA</li>
</ul>
<p>REC Rewa has very affordable government fees and reasonable placements. A great choice for students from the Rewa/Satna region. Use our <a href="/predictor">predictor</a> to check your chance.</p>""",
    },
    {
        "slug": "ujjain-engineering-college-lateral-entry",
        "category": "Top College Cutoffs",
        "question": "What CGPA is required for Ujjain Engineering College (UEC) through lateral entry?",
        "keywords": "Ujjain Engineering College lateral entry, UEC Ujjain cutoff, Ujjain Engineering CGPA requirement",
        "description": "Know the CGPA required for Ujjain Engineering College (UEC), Ujjain through MP DTE B.Tech lateral entry. Fees, placements, and branch options.",
        "answer": """<p><strong>Ujjain Engineering College (formerly Govt. Engineering College, Ujjain)</strong> (established 1966) is a government college in Ujjain, near Indore. It is a good option for students from the Malwa region.</p>
<p>Approximate closing CGPA for UR category (2024 data):</p>
<ul>
  <li><strong>CSE:</strong> 7.3 – 8.0 CGPA</li>
  <li><strong>Mechanical:</strong> 6.5 – 7.3 CGPA</li>
  <li><strong>Civil:</strong> 6.2 – 7.0 CGPA</li>
</ul>
<p>UEC Ujjain is close to Indore (approximately 55 km) and provides government college fees and education quality. Use our <a href="/predictor">predictor</a> to check your options.</p>""",
    },
    {
        "slug": "ips-indore-lateral-entry-cgpa",
        "category": "Top College Cutoffs",
        "question": "What CGPA is required for IPS Academy Indore through lateral entry?",
        "keywords": "IPS Academy Indore lateral entry CGPA, IPS Indore cutoff lateral entry, IPS Academy Institute Engineering Indore",
        "description": "Know the CGPA required for IPS Academy Institute of Engineering and Science, Indore through MP DTE B.Tech lateral entry counselling.",
        "answer": """<p><strong>IPS Academy, Institute of Engineering and Science, Indore</strong> (established 1999) is a popular private engineering college in Indore's Rajendra Nagar area. It ranks #31-32 in DTE's official recommendation list.</p>
<p>Approximate closing CGPA for UR category (2024 data):</p>
<ul>
  <li><strong>CSE:</strong> 7.2 – 8.0 CGPA</li>
  <li><strong>IT:</strong> 7.0 – 7.8 CGPA</li>
</ul>
<p>IPS Indore has reasonable placements for Indore-based companies. It is a good Target-range college for students with 7.0–8.0 CGPA. Use our <a href="/predictor">predictor</a> to see your chance here.</p>""",
    },
    {
        "slug": "female-candidates-lateral-entry-mp-rules",
        "category": "Domicile & Reservation",
        "question": "Are there any special rules or seats for female candidates in MP lateral entry?",
        "keywords": "female candidates lateral entry MP, girls lateral entry BTech MP, supernumerary seats female lateral entry",
        "description": "Know the rules for female (women) candidates in MP DTE B.Tech lateral entry — supernumerary seats, reservation, cutoffs, and hostel availability.",
        "answer": """<p>Female candidates have specific advantages in MP DTE B.Tech Lateral Entry:</p>
<ul>
  <li><strong>Supernumerary Seats:</strong> Many government and private colleges have additional supernumerary seats exclusively for female candidates. These seats do not compete with male candidates.</li>
  <li><strong>Lower Cutoffs:</strong> Female merit lists are separate, so cutoffs for female students are generally lower than for male students. A female student with 7.5 CGPA may get the same college where a male student needs 8.2+.</li>
  <li><strong>Reservation within reservation:</strong> Female SC/ST/OBC candidates get the dual benefit of their category reservation AND female category seats.</li>
</ul>
<p>When using our <a href="/predictor">predictor</a>, select <strong>Gender = Female</strong> to see your personalized female-category results.</p>""",
    },
    {
        "slug": "which-diploma-branch-is-best-for-lateral-entry-cse",
        "category": "Branch Change",
        "question": "Which diploma branch is best to get CSE admission in B.Tech lateral entry in MP?",
        "keywords": "diploma branch for CSE lateral entry, which polytechnic branch for BTech CSE, best diploma for computer science lateral entry",
        "description": "If you are planning for CSE B.Tech through lateral entry in MP, which diploma branch should you take? Does your diploma branch affect your eligibility or admission chances?",
        "answer": """<p>In MP DTE B.Tech Lateral Entry, <strong>any diploma branch can apply for any B.Tech branch</strong> — there is no restriction.</p>
<p>So if you want CSE in B.Tech, you can have a diploma in:</p>
<ul>
  <li>Computer Science / CSE Diploma ✅</li>
  <li>Electronics / ECE Diploma ✅</li>
  <li>Mechanical Engineering Diploma ✅</li>
  <li>Civil Engineering Diploma ✅</li>
  <li>Electrical Engineering Diploma ✅</li>
  <li>Any other recognized engineering diploma ✅</li>
</ul>
<p>Your admission depends only on your <strong>CGPA/percentage in diploma</strong> — not on which branch your diploma was in. So focus on getting a high CGPA in whatever diploma you are studying to maximize your lateral entry chances.</p>""",
    },
    {
        "slug": "mp-dte-lateral-entry-vs-direct-btech-admission",
        "category": "CGPA & Eligibility",
        "question": "Is B.Tech lateral entry admission better or worse than direct (regular) B.Tech admission?",
        "keywords": "lateral entry vs direct BTech admission, regular vs lateral entry BTech comparison, should I take lateral entry or direct BTech",
        "description": "Compare B.Tech lateral entry admission with direct (regular) 4-year B.Tech admission in MP. Which route is better for career, savings, and time efficiency?",
        "answer": """<p>Here is an honest comparison of both routes:</p>
<table border="1" cellpadding="8" style="border-collapse:collapse; width:100%;">
  <tr><th>Factor</th><th>Regular B.Tech (4 years)</th><th>Lateral Entry B.Tech (3 years)</th></tr>
  <tr><td>Duration</td><td>4 years</td><td>3 years</td></tr>
  <tr><td>Prerequisite</td><td>12th Science (PCM)</td><td>3-year Engineering Diploma</td></tr>
  <tr><td>Fees Total</td><td>Higher (4 years)</td><td>Lower (3 years)</td></tr>
  <tr><td>Time to Degree</td><td>4 years after 12th</td><td>3 years after Diploma</td></tr>
  <tr><td>Degree Value</td><td>Same B.Tech degree</td><td>Same B.Tech degree</td></tr>
  <tr><td>Practical Experience</td><td>Less practical focus in 1st year</td><td>Strong polytechnic practical base</td></tr>
  <tr><td>Competition</td><td>Via JEE/State CET</td><td>Via DTE Merit List (less competitive)</td></tr>
</table>
<p><strong>Verdict:</strong> Lateral entry is highly recommended if you already have a diploma. You save 1 year of time + fees, yet get the same B.Tech degree. The only downside is you miss the foundation courses from 1st year, but bridge courses cover this.</p>""",
    },
]


def get_faq_by_slug(slug):
    """Return FAQ entry matching the given slug, or None."""
    for faq in FAQ_LIST:
        if faq["slug"] == slug:
            return faq
    return None


def get_faqs_by_category(category):
    """Return all FAQs in the given category."""
    return [f for f in FAQ_LIST if f["category"] == category]


def get_all_categories():
    """Return list of categories in order, only those with at least one entry."""
    seen = []
    for faq in FAQ_LIST:
        if faq["category"] not in seen:
            seen.append(faq["category"])
    return seen
