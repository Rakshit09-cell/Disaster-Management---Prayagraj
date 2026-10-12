"""
============================================================
Multi-Agent Disaster Management System
============================================================
Prayagraj District, Uttar Pradesh, India

Tech Stack: Flask + LangChain + Groq AI
Agents:    7 Specialized AI Agents + 1 Coordinator
Data:      Simulated realistic data for Prayagraj

Author:    Final Year Project
============================================================
"""

from flask import Flask, render_template, request, Response, jsonify
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.tools import tool
import json
import traceback
import copy

app = Flask(__name__)


# ============================================================
#  GROQ MODEL — with fallback list
# ============================================================
GROQ_MODELS = [
    "openai/gpt-oss-120b",
    "llama-3.3-70b-versatile",
    "llama3-70b-8192",
    "llama-3.1-70b-versatile",
    "mixtral-8x7b-32768",
]


# ============================================================
#  SIMULATED DATA — Prayagraj District, Uttar Pradesh
# ============================================================

PRAYAGRAJ_DATA = {

    "district_info": {
        "name": "Prayagraj (Allahabad)",
        "state": "Uttar Pradesh",
        "population": 6810000,
        "area_sq_km": 5482,
        "major_rivers": ["Ganga", "Yamuna"],
        "confluence": "Triveni Sangam — Ganga, Yamuna & mythical Saraswati",
        "tehsils": ["Sadar", "Soraon", "Handia", "Meja", "Koraon", "Bara", "Phulpur", "Pratappur"],
        "dm_name": "Shri Anil Kumar Singh (IAS)",
    },

    "areas": {
        "flood_prone": [
            {"name": "Daraganj",      "population": 45000, "risk": "Very High", "near_river": "Ganga", "elevation_m": 82},
            {"name": "Jhunsi",        "population": 62000, "risk": "High",      "near_river": "Ganga & Yamuna", "elevation_m": 83},
            {"name": "Phaphamau",     "population": 55000, "risk": "High",      "near_river": "Ganga", "elevation_m": 83},
            {"name": "Naini",         "population": 78000, "risk": "Moderate",  "near_river": "Yamuna", "elevation_m": 85},
            {"name": "Arail",         "population": 32000, "risk": "Very High", "near_river": "Sangam area", "elevation_m": 81},
            {"name": "Salori",        "population": 28000, "risk": "High",      "near_river": "Ganga", "elevation_m": 83},
            {"name": "Bakshi Bandh",  "population": 18000, "risk": "Very High", "near_river": "Ganga", "elevation_m": 81},
            {"name": "Rasoolabad",    "population": 22000, "risk": "High",      "near_river": "Ganga", "elevation_m": 83},
            {"name": "Chhatnag",      "population": 15000, "risk": "Moderate",  "near_river": "Yamuna", "elevation_m": 85},
        ],
        "safe_zones": [
            {"name": "Civil Lines",   "capacity": 15000, "facilities": ["Minto Hall", "Govt. Schools", "Community Hall"]},
            {"name": "George Town",   "capacity": 12000, "facilities": ["Madan Mohan Malviya Stadium", "Govt. Buildings"]},
            {"name": "Tagore Town",   "capacity": 8000,  "facilities": ["Central Academy School", "Parks"]},
            {"name": "Lukerganj",     "capacity": 10000, "facilities": ["Municipal Community Centers", "Temples"]},
            {"name": "Kydganj",       "capacity": 7000,  "facilities": ["Government Inter College", "Open Grounds"]},
            {"name": "Allapur",       "capacity": 9000,  "facilities": ["University Grounds", "Hostels"]},
            {"name": "Bamrauli",      "capacity": 6000,  "facilities": ["Air Force Station grounds (civilian area)"]},
        ],
    },

    "hospitals": [
        {"name": "Swaroop Rani Nehru Hospital",  "location": "Lowther Road",  "beds": 800, "available_beds": 120, "icu_beds": 45, "icu_available": 8,  "ambulances": 8, "blood_bank": True,  "distance_from_sangam_km": 3.5},
        {"name": "MLN Medical College & Hospital","location": "George Town",   "beds": 600, "available_beds": 85,  "icu_beds": 30, "icu_available": 5,  "ambulances": 5, "blood_bank": True,  "distance_from_sangam_km": 4.0},
        {"name": "Beli Hospital",                 "location": "Beli Gaon",     "beds": 250, "available_beds": 45,  "icu_beds": 15, "icu_available": 3,  "ambulances": 3, "blood_bank": False, "distance_from_sangam_km": 5.2},
        {"name": "Colvin Hospital",               "location": "Civil Lines",   "beds": 200, "available_beds": 35,  "icu_beds": 12, "icu_available": 4,  "ambulances": 2, "blood_bank": False, "distance_from_sangam_km": 4.8},
        {"name": "United Medicity",               "location": "Naini",         "beds": 350, "available_beds": 60,  "icu_beds": 25, "icu_available": 7,  "ambulances": 4, "blood_bank": True,  "distance_from_sangam_km": 6.0},
        {"name": "Tej Hospital",                  "location": "Tagore Town",   "beds": 150, "available_beds": 30,  "icu_beds": 10, "icu_available": 2,  "ambulances": 2, "blood_bank": False, "distance_from_sangam_km": 5.5},
        {"name": "Kamla Nehru Hospital",          "location": "Tagore Town",   "beds": 180, "available_beds": 40,  "icu_beds": 8,  "icu_available": 3,  "ambulances": 2, "blood_bank": False, "distance_from_sangam_km": 5.0},
    ],

    "emergency_resources": {
        "NDRF": {"teams": 3, "personnel_per_team": 45, "total_personnel": 135, "boats": 12, "base": "Lucknow — 3hr deployment", "status": "Standby"},
        "SDRF": {"teams": 2, "personnel_per_team": 45, "total_personnel": 90, "boats": 8, "base": "Prayagraj", "status": "Active"},
        "fire_brigade": {"stations": 4, "personnel": 120, "fire_tenders": 10, "rescue_vehicles": 5, "locations": ["Civil Lines", "Naini", "Phaphamau", "George Town"]},
        "police": {"stations": 18, "total_personnel": 2500, "patrol_vehicles": 80, "wireless_sets": 45, "PAC_battalions": 2},
        "district_admin": {
            "relief_camps_ready": 25,
            "total_camp_capacity": 50000,
            "boats_available": 20,
            "tarpaulins": 5000,
            "food_packets_ready": 100000,
            "water_tankers": 15,
            "generators": 20,
            "medical_kits": 500,
        },
        "ngo_volunteers": {"organizations": ["Red Cross Prayagraj", "Ganga Seva Abhiyan", "Lions Club", "Rotary Club"], "total_volunteers": 350},
    },

    "weather": {
        "current": {
            "date": "2024-08-15",
            "rainfall_last_24h_mm": 185,
            "rainfall_last_48h_mm": 310,
            "temperature_c": 32,
            "humidity_pct": 92,
            "wind_speed_kmh": 45,
            "wind_direction": "East-Southeast",
            "visibility_km": 2,
        },
        "river_levels": {
            "ganga": {"current_level_m": 84.73, "danger_level_m": 84.734, "highest_flood_level_m": 85.129, "trend": "Rising"},
            "yamuna": {"current_level_m": 82.10, "danger_level_m": 82.553, "highest_flood_level_m": 83.82, "trend": "Rising"},
        },
        "imd_alert": "RED ALERT — Heavy to very heavy rainfall (>200mm) expected in next 24 hours",
        "forecast_24h": "Heavy to very heavy rainfall expected. Thunderstorms likely. Rivers expected to breach danger marks.",
        "forecast_48h": "Moderate rainfall. Water levels expected to remain above danger mark for 48-72 hours.",
        "upstream_status": "Heavy discharge from Kanpur barrage — 6.5 lakh cusecs. Expected to reach Prayagraj in 18-24 hours.",
    },

    "evacuation_routes": [
        {"from": "Daraganj",     "to": "Civil Lines",   "route": "Daraganj → MG Marg → Civil Lines",              "distance_km": 4.5, "status": "Open",              "road_condition": "Waterlogged in patches"},
        {"from": "Jhunsi",       "to": "Bamrauli",      "route": "Jhunsi → NH-19 → Bamrauli",                      "distance_km": 8.0, "status": "Partially Flooded",  "road_condition": "NH-19 elevated — usable"},
        {"from": "Phaphamau",    "to": "Teliyarganj",   "route": "Phaphamau Bridge → GT Road → Teliyarganj",       "distance_km": 6.0, "status": "Open",              "road_condition": "Good"},
        {"from": "Naini",        "to": "George Town",   "route": "Naini → Old Naini Bridge → George Town",         "distance_km": 5.0, "status": "Open",              "road_condition": "Moderate"},
        {"from": "Arail",        "to": "George Town",   "route": "Arail → Boat Bridge → George Town",              "distance_km": 3.0, "status": "Submerged",         "road_condition": "Impassable — boat rescue only"},
        {"from": "Bakshi Bandh", "to": "Kydganj",       "route": "Bakshi Bandh → MG Marg → Kydganj",              "distance_km": 3.5, "status": "Open",              "road_condition": "Usable"},
        {"from": "Salori",       "to": "Lukerganj",     "route": "Salori → Kamla Nehru Road → Lukerganj",          "distance_km": 5.0, "status": "Partially Flooded",  "road_condition": "Waterlogged — slow traffic"},
        {"from": "Rasoolabad",   "to": "Allapur",       "route": "Rasoolabad → University Road → Allapur",         "distance_km": 4.0, "status": "Open",              "road_condition": "Good"},
    ],

    "control_rooms": {
        "District DM Control Room": "0532-2623030",
        "Flood Control Room":       "0532-2504045",
        "Police Control Room":      "112 / 0532-2624270",
        "Fire Emergency":           "101",
        "Ambulance (108)":          "108",
        "NDRF Helpline":            "011-24363260",
        "UP Helpline":              "1070",
        "Child Helpline":           "1098",
        "Women Helpline":           "181",
    },
}

DEFAULT_PRAYAGRAJ_DATA = copy.deepcopy(PRAYAGRAJ_DATA)


# ============================================================
#  LANGCHAIN TOOLS — Data Access Layer
# ============================================================

@tool
def get_weather_data(query: str = "all") -> str:
    """Retrieve current weather, river levels, IMD alerts, and forecasts for Prayagraj district."""
    return json.dumps(PRAYAGRAJ_DATA["weather"], indent=2, ensure_ascii=False)


@tool
def get_location_data(query: str = "all") -> str:
    """Retrieve flood-prone areas, safe zones, and district info for Prayagraj."""
    return json.dumps({
        "district_info": PRAYAGRAJ_DATA["district_info"],
        "flood_prone_areas": PRAYAGRAJ_DATA["areas"]["flood_prone"],
        "safe_zones": PRAYAGRAJ_DATA["areas"]["safe_zones"],
    }, indent=2, ensure_ascii=False)


@tool
def get_hospital_data(query: str = "all") -> str:
    """Retrieve hospital information including beds, ICU, ambulances, blood banks in Prayagraj."""
    return json.dumps(PRAYAGRAJ_DATA["hospitals"], indent=2, ensure_ascii=False)


@tool
def get_resource_data(query: str = "all") -> str:
    """Retrieve emergency resources including NDRF, SDRF, police, fire brigade, district admin supplies."""
    return json.dumps(PRAYAGRAJ_DATA["emergency_resources"], indent=2, ensure_ascii=False)


@tool
def get_evacuation_data(query: str = "all") -> str:
    """Retrieve evacuation routes with current status and road conditions."""
    return json.dumps(PRAYAGRAJ_DATA["evacuation_routes"], indent=2, ensure_ascii=False)


@tool
def get_control_room_numbers(query: str = "all") -> str:
    """Retrieve all emergency control room phone numbers for Prayagraj district."""
    return json.dumps(PRAYAGRAJ_DATA["control_rooms"], indent=2, ensure_ascii=False)


# ============================================================
#  LANGCHAIN AGENT CHAIN CONFIGS
# ============================================================

AGENT_CONFIGS = [
    {
        "id": "weather",
        "name": "Weather & Disaster Monitoring Agent",
        "icon": "🌦️",
        "tool": get_weather_data,
        "system_prompt": """You are the Weather & Disaster Monitoring Agent for Prayagraj District, Uttar Pradesh.

Your job: Analyze the disaster scenario using real-time weather data.

Report these points concisely (use bullet points):
• Disaster TYPE and SEVERITY (scale 1-5, where 5 is catastrophic)
• Current rainfall and conditions
• Ganga river level vs danger mark (84.734m) — how close/above?
• Yamuna river level vs danger mark (82.553m) — how close/above?
• IMD alert status
• Upstream water release impact
• 24-48 hour forecast and what it means

Keep it to 6-8 bullet points. Be factual, use numbers from the data.""",
    },
    {
        "id": "gis",
        "name": "GIS & Location Analysis Agent",
        "icon": "🗺️",
        "tool": get_location_data,
        "system_prompt": """You are the GIS & Location Analysis Agent for Prayagraj District, Uttar Pradesh.

Your job: Identify affected locations and population at risk.

Report these points concisely:
• List each affected area with population and risk level
• Total estimated population at risk
• Which areas are MOST CRITICAL (Very High risk first)
• Nearest safe zones for each flood-prone area
• Total shelter capacity available
• Any areas that may get cut off (surrounded by water)

Use the location data provided. Reference specific locality names. Keep it factual with numbers.""",
    },
    {
        "id": "resource",
        "name": "Emergency Resource Agent",
        "icon": "🚑",
        "tool": get_resource_data,
        "system_prompt": """You are the Emergency Resource Agent for Prayagraj District.

Your job: Assess and recommend resource deployment.

Using the previous agents' findings and resource data, report:
• NDRF status and deployment recommendation
• SDRF current deployment
• Boats available and where to deploy them
• Police and PAC deployment for crowd/traffic management
• Fire brigade positioning
• Relief supplies status (food packets, water, tarpaulins, medical kits)
• NGO volunteer coordination
• Any resource GAPS that need urgent procurement

Be specific — mention numbers and locations.""",
    },
    {
        "id": "hospital",
        "name": "Hospital & Medical Agent",
        "icon": "🏥",
        "tool": get_hospital_data,
        "system_prompt": """You are the Hospital & Medical Response Agent for Prayagraj District.

Your job: Coordinate medical response.

Report:
• List hospitals with AVAILABLE beds and ICU capacity
• Total ambulances deployable
• Which hospitals serve which affected areas (proximity-based)
• Blood bank availability
• Recommended medical staging points near flood zones
• Medical teams needed for relief camps
• Special needs: pregnant women, elderly, children, dialysis patients in affected areas

Prioritize hospitals closest to high-risk zones.""",
    },
    {
        "id": "rescue",
        "name": "Rescue Operations Agent",
        "icon": "🚒",
        "tool": get_evacuation_data,
        "system_prompt": """You are the Rescue Operations Agent for Prayagraj District.

Your job: Create a detailed rescue and evacuation plan.

Using evacuation route data and previous agents' reports:
• PRIORITY ORDER of areas to evacuate (most critical first)
• Evacuation routes — which are open, which are flooded
• Alternative routes for submerged/blocked roads
• Boat rescue plan for cut-off areas (like Arail)
• Timeline: when to start, phase-wise evacuation schedule
• Special evacuation: elderly, disabled, pregnant women, children
• Traffic management on evacuation routes
• Assembly points for each area

Be very specific with route names and timings.""",
    },
    {
        "id": "alert",
        "name": "Public Alert Agent",
        "icon": "📢",
        "tool": get_control_room_numbers,
        "system_prompt": """You are the Public Alert & Communication Agent for Prayagraj District.

Your job: Draft emergency alerts for the public.

Create TWO versions:

**ENGLISH ALERT:**
A clear emergency message covering: what happened, who is affected, what to do, where to go, helpline numbers.

**HINDI ALERT:**
Same information in Hindi for local population.

Also include:
• DO's and DON'Ts for the situation
• Social media advisory
• Rumor control message

Use the control room numbers from the data. Make alerts CLEAR, URGENT, and ACTIONABLE.""",
    },
    {
        "id": "coordinator",
        "name": "Crisis Coordinator",
        "icon": "🧠",
        "tool": get_control_room_numbers,
        "system_prompt": """You are the CRISIS COORDINATOR — the central command authority for Prayagraj District Disaster Management.

You have received reports from ALL 6 specialist agents. Your job is to synthesize everything into a UNIFIED ACTION PLAN for the District Magistrate.

Structure your response as:

## SITUATION SUMMARY
(2-3 line overview)

## SEVERITY ASSESSMENT
(Overall severity, affected population, critical areas)

## IMMEDIATE ACTIONS (0-6 Hours)
(Numbered list of urgent actions)

## SHORT-TERM ACTIONS (6-24 Hours)
(Numbered list)

## RESOURCE DEPLOYMENT MATRIX
(Who goes where)

## MEDICAL RESPONSE PLAN
(Hospital coordination)

## COMMUNICATION PLAN
(Public alerts, media briefing)

## COMMAND STRUCTURE
(Who reports to whom)

## HELPLINE NUMBERS
(Quick reference)

This is the FINAL AUTHORITATIVE response. Be decisive, specific, and actionable.
Address it to: District Magistrate, Prayagraj.""",
    },
]


# ============================================================
#  HELPER: Get a working Groq LLM (tries multiple models)
# ============================================================

def get_working_llm(api_key, preferred_model=None):
    """Try to create a ChatGroq instance. Falls back through model list."""
    models_to_try = []
    if preferred_model:
        models_to_try.append(preferred_model)
    models_to_try.extend(GROQ_MODELS)

    last_error = None
    for model_name in models_to_try:
        try:
            llm = ChatGroq(
                api_key=api_key,
                model_name=model_name,
                temperature=0.3,
                max_tokens=1500,
            )
            return llm, model_name
        except Exception as e:
            last_error = e
            continue

    raise Exception(f"Could not initialize any Groq model. Last error: {_format_error(last_error)}")


def _format_error(e):
    """Extract a meaningful error message from various exception types."""
    # Try different attributes that Groq/HTTP errors might use
    msg = ""
    if hasattr(e, 'message'):
        msg = str(e.message)
    if not msg and hasattr(e, 'body') and isinstance(e.body, dict):
        msg = e.body.get('error', {}).get('message', '') if isinstance(e.body.get('error'), dict) else str(e.body.get('error', ''))
    if not msg and hasattr(e, 'args') and e.args:
        msg = str(e.args[0])
    if not msg:
        msg = repr(e)
    return msg


# ============================================================
#  CREATE LANGCHAIN CHAINS
# ============================================================

def create_agent_chains(api_key, model_name=None):
    """Create all LangChain agent chains with Groq LLM."""

    llm, used_model = get_working_llm(api_key, model_name)
    parser = StrOutputParser()
    chains = []

    print(f"  ✓ Using Groq model: {used_model}")

    for config in AGENT_CONFIGS:
        if config["id"] == "coordinator":
            prompt = ChatPromptTemplate.from_messages([
                ("system", config["system_prompt"]),
                ("human",
                 "DISASTER SCENARIO:\n{scenario}\n\n"
                 "AGENT REPORTS:\n{all_reports}\n\n"
                 "CONTROL ROOM NUMBERS:\n{data}\n\n"
                 "Now produce the final unified action plan."),
            ])
        else:
            prompt = ChatPromptTemplate.from_messages([
                ("system", config["system_prompt"]),
                ("human",
                 "DISASTER SCENARIO:\n{scenario}\n\n"
                 "DATA:\n{data}\n\n"
                 "PREVIOUS AGENT REPORTS (for context):\n{context}\n\n"
                 "Produce your analysis now."),
            ])

        # LangChain LCEL pipe syntax: prompt | llm | parser
        chain = prompt | llm | parser

        chains.append({
            "id":    config["id"],
            "name":  config["name"],
            "icon":  config["icon"],
            "tool":  config["tool"],
            "chain": chain,
        })

    return chains


# ============================================================
#  RUN ANALYSIS — Sequential Agent Pipeline
# ============================================================

def run_analysis(scenario, api_key, model_name=None):
    """Run all agents sequentially, yielding results one by one."""

    print(f"\n{'='*60}")
    print(f"  🚨 New Analysis Request")
    print(f"  Scenario: {scenario[:80]}...")
    print(f"{'='*60}")

    try:
        chains = create_agent_chains(api_key, model_name)
    except Exception as e:
        error_msg = _format_error(e)
        print(f"  ✗ Failed to initialize LLM: {error_msg}")
        yield {
            "agent_id": "weather",
            "agent_name": "System",
            "agent_icon": "⚠️",
            "result": f"Failed to connect to Groq API: {error_msg}\n\nPlease check:\n1. Is your API key correct?\n2. Do you have credits/access?\n3. Try a different model.",
            "status": "error",
        }
        return

    results = {}
    agent_num = 0

    for agent in chains:
        agent_num += 1
        agent_id = agent["id"]
        print(f"\n  Agent {agent_num}/7: {agent['name']}...")

        try:
            # Step 1: Call the LangChain Tool to get data
            data = agent["tool"].invoke("fetch")
            print(f"    ✓ Data loaded ({len(data)} chars)")

            # Step 2: Build input for the chain
            if agent_id == "coordinator":
                all_reports = "\n\n".join(
                    f"=== {aid.upper()} AGENT ===\n{text}"
                    for aid, text in results.items()
                )
                chain_input = {
                    "scenario":    scenario,
                    "all_reports": all_reports,
                    "data":        data,
                }
            else:
                context = "\n\n".join(
                    f"[{aid.upper()}]: {text[:500]}"
                    for aid, text in results.items()
                ) if results else "No previous reports yet."

                chain_input = {
                    "scenario": scenario,
                    "data":     data,
                    "context":  context,
                }

            # Step 3: Invoke the LangChain chain
            result = agent["chain"].invoke(chain_input)
            results[agent_id] = result
            print(f"    ✓ Response received ({len(result)} chars)")

            yield {
                "agent_id":   agent_id,
                "agent_name": agent["name"],
                "agent_icon": agent["icon"],
                "result":     result,
                "status":     "complete",
            }

        except Exception as e:
            error_msg = _format_error(e)
            full_traceback = traceback.format_exc()
            print(f"    ✗ ERROR: {error_msg}")
            print(f"    Traceback:\n{full_traceback}")

            results[agent_id] = f"[ERROR: {error_msg}]"

            yield {
                "agent_id":   agent_id,
                "agent_name": agent["name"],
                "agent_icon": agent["icon"],
                "result":     f"Agent error: {error_msg}",
                "status":     "error",
            }


# ============================================================
#  FLASK ROUTES
# ============================================================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/test", methods=["POST"])
def test_connection():
    """Test Groq API connection before running full analysis."""
    data = request.json
    api_key = data.get("api_key", "")
    model = data.get("model", None)

    if not api_key:
        return jsonify({"success": False, "error": "API key is required"}), 400

    try:
        llm, used_model = get_working_llm(api_key, model)
        # Quick test call
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Reply with exactly: OK"),
            ("human", "Test"),
        ])
        chain = prompt | llm | StrOutputParser()
        result = chain.invoke({})
        return jsonify({
            "success": True,
            "model": used_model,
            "message": f"Connected to Groq ({used_model})"
        })
    except Exception as e:
        error_msg = _format_error(e)
        return jsonify({"success": False, "error": error_msg}), 400


@app.route("/api/analyze", methods=["POST"])
def analyze():
    """SSE endpoint — streams agent results one by one."""
    data = request.json
    scenario = data.get("scenario", "")
    api_key = data.get("api_key", "")
    model = data.get("model", None)

    if not scenario or not api_key:
        return jsonify({"error": "Scenario and API key are required"}), 400

    def generate():
        try:
            for agent_result in run_analysis(scenario, api_key, model):
                yield f"data: {json.dumps(agent_result, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'status': 'done'})}\n\n"
        except Exception as e:
            error_msg = _format_error(e)
            print(f"  ✗ FATAL ERROR: {error_msg}")
            print(traceback.format_exc())
            yield f"data: {json.dumps({'status': 'error', 'result': error_msg})}\n\n"

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control":     "no-cache",
            "X-Accel-Buffering": "no",
            "Connection":        "keep-alive",
        },
    )


@app.route("/api/models")
def list_models():
    """Return available model list."""
    return jsonify({"models": GROQ_MODELS})


@app.route("/api/data")
def get_data():
    """Return raw simulated data for reference."""
    return jsonify(PRAYAGRAJ_DATA)


@app.route("/api/data/update", methods=["POST"])
def update_data():
    """Update Prayagraj district database in memory."""
    global PRAYAGRAJ_DATA
    try:
        new_data = request.json
        if not new_data or not isinstance(new_data, dict):
            return jsonify({"success": False, "error": "Invalid data format"}), 400

        for key, val in new_data.items():
            if key in PRAYAGRAJ_DATA:
                PRAYAGRAJ_DATA[key] = val

        return jsonify({"success": True, "message": "Database updated successfully", "data": PRAYAGRAJ_DATA})
    except Exception as e:
        return jsonify({"success": False, "error": _format_error(e)}), 400


@app.route("/api/data/reset", methods=["POST"])
def reset_data():
    """Reset Prayagraj district database to baseline defaults."""
    global PRAYAGRAJ_DATA
    try:
        PRAYAGRAJ_DATA = copy.deepcopy(DEFAULT_PRAYAGRAJ_DATA)
        return jsonify({"success": True, "message": "Database reset to baseline defaults", "data": PRAYAGRAJ_DATA})
    except Exception as e:
        return jsonify({"success": False, "error": _format_error(e)}), 400



# ============================================================
#  ENTRY POINT
# ============================================================
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  🚨 Multi-Agent Disaster Management System")
    print("  📍 Prayagraj District, Uttar Pradesh")
    print("  🔗 http://localhost:5000")
    print("  " + "-" * 56)
    print("  Available Groq models (will try in order):")
    for m in GROQ_MODELS:
        print(f"    • {m}")
    print("=" * 60 + "\n")
    app.run(debug=True, port=5000)
