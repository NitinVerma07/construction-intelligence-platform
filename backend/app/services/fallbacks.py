"""Deterministic rule-based outputs.

Used (a) in offline demo mode (no API key) and (b) as a safety net when the LLM call fails.
Valuation and planning baselines are also passed to the LLM as an anchor.
All figures are indicative rules of thumb, not a substitute for a site survey or valuer.
"""
from ..schemas import PlanningRequest, ValuationRequest, WeatherSnapshot

DEMO_NOTE = "Demo mode output - add ANTHROPIC_API_KEY to .env for live AI analysis."

# ---------------------------------------------------------------- valuation
CITY_RATES_INR_SQFT = {
    "mumbai": 22000, "delhi": 11000, "new delhi": 11000, "gurgaon": 10000, "gurugram": 10000,
    "noida": 7000, "bengaluru": 8500, "bangalore": 8500, "hyderabad": 7500, "chennai": 7500,
    "pune": 7500, "kolkata": 6000, "ahmedabad": 5500, "jaipur": 4500, "indore": 4500,
    "bhopal": 3800, "lucknow": 4500, "chandigarh": 7000, "kochi": 6500, "nagpur": 4000,
}
DEFAULT_RATE = 3500
TYPE_MULT = {"apartment": 1.0, "independent_house": 1.15, "villa": 1.35, "plot": 0.7, "commercial": 1.5}
QUALITY_MULT = {"basic": 0.9, "standard": 1.0, "premium": 1.2, "luxury": 1.4}


def valuation_baseline(req: ValuationRequest) -> dict:
    base = CITY_RATES_INR_SQFT.get(req.city.strip().lower(), DEFAULT_RATE)
    age_factor = 1.0 if req.property_type == "plot" else 1 - min(req.age_years * 0.01, 0.30)
    amenity_factor = 1 + min(len(req.amenities) * 0.015, 0.10)
    rate = base * TYPE_MULT[req.property_type] * QUALITY_MULT[req.quality] * age_factor * amenity_factor
    value = rate * req.area_sqft
    known = req.city.strip().lower() in CITY_RATES_INR_SQFT
    factors = [
        {"name": "Location", "impact": "positive" if base >= 7000 else "neutral",
         "note": f"Reference market rate about INR {base:,}/sq ft" + ("" if known else " (generic city rate)")},
        {"name": "Property type", "impact": "positive" if TYPE_MULT[req.property_type] > 1 else "neutral",
         "note": f"{req.property_type.replace('_', ' ').title()} multiplier x{TYPE_MULT[req.property_type]}"},
        {"name": "Construction quality", "impact": "positive" if QUALITY_MULT[req.quality] > 1 else
         ("negative" if QUALITY_MULT[req.quality] < 1 else "neutral"),
         "note": f"{req.quality.title()} finish multiplier x{QUALITY_MULT[req.quality]}"},
    ]
    if req.age_years:
        factors.append({"name": "Age", "impact": "negative",
                        "note": f"{req.age_years} years -> {round((1 - age_factor) * 100)}% depreciation (capped at 30%)"})
    if req.amenities:
        factors.append({"name": "Amenities", "impact": "positive",
                        "note": f"{len(req.amenities)} amenities add about {round((amenity_factor - 1) * 100, 1)}%"})
    return {
        "estimated_value_inr": round(value, -3),
        "price_per_sqft_inr": round(rate),
        "range_low_inr": round(value * 0.9, -3),
        "range_high_inr": round(value * 1.1, -3),
        "confidence": "medium" if known else "low",
        "factors": factors,
        "summary": f"Indicative value of INR {round(value, -3):,.0f} (about INR {round(rate):,}/sq ft) "
                   f"for a {req.property_type.replace('_', ' ')} in {req.city.title()}. {DEMO_NOTE}",
    }


# ----------------------------------------------------------------- planning
PHASE_TEMPLATE = [
    ("Planning, design & approvals", 0.10,
     ["Soil investigation", "Architectural & structural design", "Statutory approvals and permits", "Budget and procurement plan"]),
    ("Site preparation & foundation", 0.15,
     ["Site clearing and layout marking", "Excavation", "PCC and footing reinforcement", "Footing/raft concreting and plinth beams"]),
    ("Superstructure (RCC frame)", 0.25,
     ["Column and beam reinforcement", "Shuttering and slab casting", "Curing for minimum 7 days", "Floor-by-floor repetition"]),
    ("Masonry, MEP rough-in & plastering", 0.20,
     ["Brick/block masonry", "Electrical conduits and plumbing lines", "Internal and external plastering", "Waterproofing of wet areas and terrace"]),
    ("Finishing & fittings", 0.22,
     ["Flooring and tiling", "Doors, windows and railings", "Painting", "Fixtures, sanitaryware and electrical fittings"]),
    ("Testing, snagging & handover", 0.08,
     ["Electrical and plumbing testing", "Snag list closure", "Completion certificate", "Handover and documentation"]),
]
COST_SPLIT = [
    ("Foundation & structure", 35), ("Masonry & plastering", 15), ("MEP (electrical, plumbing)", 15),
    ("Finishing & fixtures", 25), ("Approvals, supervision & contingency", 10),
]
RATE_PER_SQFT = {"residential": 2200, "commercial": 2800, "industrial": 2000, "infrastructure": 3200}


def planning_baseline(req: PlanningRequest) -> dict:
    if req.duration_months:
        weeks = round(req.duration_months * 4.345)
    else:
        weeks = round(max(20, 18 + req.built_up_area_sqft / 120) + (req.floors - 1) * 6)
    weeks = max(weeks, len(PHASE_TEMPLATE))
    phases = [
        {"name": n, "duration_weeks": max(1, round(weeks * share)), "tasks": tasks}
        for n, share, tasks in PHASE_TEMPLATE
    ]
    total_weeks = sum(p["duration_weeks"] for p in phases)
    total_cost = req.budget_inr or req.built_up_area_sqft * RATE_PER_SQFT[req.project_type]
    area = req.built_up_area_sqft
    return {
        "total_estimated_cost_inr": round(total_cost),
        "total_duration_weeks": total_weeks,
        "phases": phases,
        "materials": [
            {"material": "Cement", "quantity": round(area * 0.4), "unit": "bags (50 kg)"},
            {"material": "Steel reinforcement", "quantity": round(area * 4), "unit": "kg"},
            {"material": "Sand", "quantity": round(area * 1.2), "unit": "cft"},
            {"material": "Coarse aggregate", "quantity": round(area * 1.35), "unit": "cft"},
            {"material": "Bricks / blocks", "quantity": round(area * 8), "unit": "nos"},
        ],
        "cost_breakdown": [
            {"category": c, "percent": p, "amount_inr": round(total_cost * p / 100)} for c, p in COST_SPLIT
        ],
        "risks": [
            "Monsoon season can delay excavation, concreting and plastering.",
            "Cement and steel price volatility can push the budget up.",
            "Approval or utility-connection delays can stall the start.",
            "Skilled labour availability affects finishing quality and schedule.",
        ],
        "summary": f"{req.project_type.title()} project of {area:,.0f} sq ft over about {total_weeks} weeks "
                   f"with an estimated cost of INR {round(total_cost):,}. {DEMO_NOTE}",
    }


# ------------------------------------------------------------------- safety
def safety_fallback(notes: str = "") -> dict:
    return {
        "risk_level": "medium",
        "risk_score": 55,
        "ppe_detected": [],
        "ppe_missing": ["Hard hat", "High-visibility vest", "Safety footwear"],
        "findings": [
            {"issue": "Image not analysed by AI (demo mode)", "severity": "low",
             "recommendation": "Enable the LLM key to detect PPE usage, working-at-height hazards and housekeeping issues."},
            {"issue": "Generic site check", "severity": "medium",
             "recommendation": "Verify PPE for all workers, edge protection on slabs, and clear walkways."},
        ],
        "summary": f"Placeholder safety assessment. {DEMO_NOTE}",
    }


# --------------------------------------------------------------------- crack
def crack_fallback(notes: str = "") -> dict:
    return {
        "crack_type": "Undetermined (demo mode)",
        "severity": "medium",
        "structural_risk": False,
        "probable_causes": ["Shrinkage or thermal movement (most common)", "Differential settlement", "Overloading or poor curing"],
        "recommended_actions": [
            "Mark crack ends with dates and measure width weekly",
            "Install a crack gauge or tell-tale",
            "Call a structural engineer if width exceeds 3 mm, the crack is diagonal, or it keeps growing",
        ],
        "urgency": "monitor",
        "confidence": 0.2,
        "summary": f"Placeholder crack assessment. {DEMO_NOTE}",
    }


# ----------------------------------------------------------------- assistant
def assistant_fallback(query: str, context: str = "") -> dict:
    q = query.lower()
    if any(k in q for k in ("concrete", "pour", "slab", "curing", "cast")):
        return {
            "answer": "Before casting: confirm reinforcement and cover blocks, shuttering stability and cleanliness, "
                      "mix design and slump, vibrator availability, and plan continuous pouring. Cure for at least 7 days.",
            "priority": "high",
            "checklist": ["Reinforcement checked and signed off", "Shuttering tight and supported", "Slump test done on arrival",
                          "Vibrators and backup available", "Curing arrangement ready"],
            "follow_ups": ["What mix grade is specified?", "What is the forecast for the next 24 hours?"],
        }
    if any(k in q for k in ("safety", "ppe", "height", "scaffold", "accident")):
        return {
            "answer": "Run a toolbox talk first thing, check PPE, inspect scaffolds and edge protection, and stop any work that lacks a permit.",
            "priority": "high",
            "checklist": ["Toolbox talk done and signed", "Scaffold tags checked", "Edge protection and openings covered",
                          "First-aid kit and fire extinguisher in place"],
            "follow_ups": ["Which activities are at height today?"],
        }
    return {
        "answer": "A good daily routine: review the plan, confirm labour and material availability, run a safety briefing, "
                  "record progress with photos, and log issues for tomorrow. " + DEMO_NOTE,
        "priority": "normal",
        "checklist": ["Review today's work plan", "Confirm labour and materials", "Safety briefing", "Quality checks on completed work",
                      "Progress photos and daily report"],
        "follow_ups": ["Which activity is on the critical path today?"],
    }


# ----------------------------------------------------------------- knowledge
KNOWLEDGE_BASE = [
    (("curing", "cure"),
     "Curing keeps concrete moist so cement hydrates fully. Start once the surface is hard (about 10-12 hours) and continue for at least 7 days for OPC (10 days where mineral admixtures are used).",
     ["Ponding, wet hessian or curing compound all work", "Never let slabs dry out in the first days", "Longer curing in hot, windy weather"],
     ["IS 456:2000 clause 13.5"]),
    (("grade", "m20", "m25", "mix"),
     "Concrete grade (e.g. M20, M25) is the characteristic compressive strength in MPa at 28 days. M20 is common for residential RCC; M25 or higher for severe exposure and heavier loads.",
     ["M20 nominal mix 1:1.5:3", "Design mixes are used for M25 and above", "Test cubes at 7 and 28 days"],
     ["IS 456:2000", "IS 10262"]),
    (("slump",),
     "The slump test measures workability of fresh concrete using a standard cone. Typical RCC slump is 75-125 mm depending on placement method.",
     ["Reject mixes outside the specified range", "Do not add water on site to fix slump", "Take cubes from the same batch"],
     ["IS 1199"]),
    (("cover", "rebar", "reinforcement"),
     "Nominal concrete cover protects steel from corrosion and fire. Typical values: 20 mm slabs, 25 mm beams, 40 mm columns and 50 mm footings in mild to moderate exposure.",
     ["Use cover blocks of the same grade", "Increase cover for severe exposure", "Check cover before every pour"],
     ["IS 456:2000 clause 26.4"]),
    (("waterproof", "leak", "seepage"),
     "Waterproof terraces, toilets, sunken slabs and basement walls. Cementitious coating or membrane over a properly sloped screed, followed by a 24-48 hour ponding test, is the standard approach.",
     ["Slope at least 1:100 to outlets", "Treat pipe penetrations and junctions", "Ponding test before tiling"],
     ["IS 3067"]),
    (("foundation", "footing", "raft", "pile"),
     "Foundation choice depends on soil bearing capacity, load and water table. Isolated footings suit good soil, raft for weak or uneven soil, piles when firm strata is deep.",
     ["Do a soil investigation first", "Keep foundations below the scour/frost zone", "Provide PCC bed and damp-proofing"],
     ["IS 1904", "IS 6403"]),
]


def knowledge_fallback(question: str) -> dict:
    q = question.lower()
    for keys, answer, points, standards in KNOWLEDGE_BASE:
        if any(k in q for k in keys):
            return {"answer": answer, "key_points": points, "standards": standards}
    return {
        "answer": "The offline knowledge base only covers curing, concrete grades, slump, rebar cover, waterproofing and foundations. " + DEMO_NOTE,
        "key_points": [],
        "standards": [],
    }


# ------------------------------------------------------------------- weather
def weather_advisory_fallback(w: WeatherSnapshot, activity: str = "") -> dict:
    rain_next = max([w.precipitation_mm] + [d.rain_mm for d in w.forecast[:2]])
    wind = max([w.wind_kmh] + [d.wind_max_kmh for d in w.forecast[:1]])
    temp = max([w.temperature_c] + [d.temp_max_c for d in w.forecast[:1]])
    recs, precautions, level = [], [], "good"
    if rain_next >= 10 or wind >= 45:
        level = "stop"
    elif rain_next >= 2 or wind >= 30 or temp >= 38:
        level = "caution"
    if rain_next >= 2:
        recs.append("Postpone concreting, plastering and painting; cover stacked cement and sand.")
        precautions.append("Keep excavations dewatered and protect open reinforcement from water pooling.")
    if wind >= 30:
        recs.append("Suspend crane lifts and work on scaffolds or open edges.")
        precautions.append("Secure loose sheets, formwork and material on upper floors.")
    if temp >= 35:
        recs.append("Cast concrete early morning or evening and increase curing frequency.")
        precautions.append("Provide drinking water, shade and rest breaks for workers.")
    if not recs:
        recs.append("Conditions are suitable for normal work; keep routine weather checks.")
    return {
        "work_suitability": level,
        "recommendations": recs,
        "precautions": precautions,
        "summary": f"{level.title()} conditions in {w.city}: up to {rain_next:.1f} mm rain, wind {wind:.0f} km/h, {temp:.0f} C.",
    }
