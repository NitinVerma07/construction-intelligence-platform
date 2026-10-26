import base64

from app.routers import weather as weather_router
from app.schemas import DayForecast, WeatherSnapshot
from app.services.llm import extract_json

# 1x1 transparent PNG
PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
)


def test_health(client):
    body = client.get("/api/health").json()
    assert body["status"] == "ok" and body["llm_mode"] == "demo"


def test_valuation(client):
    r = client.post("/api/valuation/estimate", json={
        "city": "Indore", "area_sqft": 1200, "property_type": "apartment",
        "bedrooms": 2, "age_years": 5, "quality": "standard", "amenities": ["parking", "lift"],
    })
    assert r.status_code == 200
    res = r.json()["result"]
    assert res["range_low_inr"] < res["estimated_value_inr"] < res["range_high_inr"]
    assert res["price_per_sqft_inr"] > 0


def test_valuation_validation(client):
    r = client.post("/api/valuation/estimate", json={"city": "Indore", "area_sqft": 10})
    assert r.status_code == 422


def test_planning_contract(client):
    r = client.post("/api/planning/generate", json={
        "project_type": "residential", "location": "Bhopal", "built_up_area_sqft": 1500,
        "floors": 2, "budget_inr": 4000000,
    })
    assert r.status_code == 200
    plan = r.json()["result"]
    assert plan["total_estimated_cost_inr"] == 4000000
    assert sum(p["duration_weeks"] for p in plan["phases"]) == plan["total_duration_weeks"]
    assert abs(sum(c["percent"] for c in plan["cost_breakdown"]) - 100) < 0.01


def test_safety_upload(client):
    r = client.post("/api/safety/analyze", files={"file": ("site.png", PNG, "image/png")}, data={"notes": "slab edge"})
    assert r.status_code == 200
    assert r.json()["result"]["risk_level"] in {"low", "medium", "high", "critical"}


def test_crack_upload(client):
    r = client.post("/api/cracks/analyze", files={"file": ("wall.png", PNG, "image/png")})
    assert r.status_code == 200
    assert r.json()["result"]["urgency"] in {"monitor", "repair_soon", "immediate"}


def test_rejects_non_image(client):
    r = client.post("/api/cracks/analyze", files={"file": ("x.txt", b"hello", "text/plain")})
    assert r.status_code == 415


def test_assistant_and_knowledge(client):
    a = client.post("/api/assistant/ask", json={"query": "Checklist before pouring a slab today"})
    assert a.status_code == 200 and a.json()["result"]["checklist"]
    k = client.post("/api/knowledge/ask", json={"question": "How long should concrete be cured?"})
    assert k.status_code == 200 and "7 days" in k.json()["result"]["answer"]


def test_weather_advisory(client, monkeypatch):
    snap = WeatherSnapshot(
        city="Indore, India", temperature_c=31, humidity_pct=70, wind_kmh=12, precipitation_mm=0,
        forecast=[DayForecast(date="2026-10-27", temp_max_c=33, temp_min_c=22, rain_mm=14, wind_max_kmh=20)],
    )
    monkeypatch.setattr(weather_router, "fetch_weather", lambda city: snap)
    r = client.post("/api/weather/advisory", json={"city": "Indore"})
    assert r.status_code == 200
    assert r.json()["result"]["advisory"]["work_suitability"] == "stop"


def test_history_roundtrip(client):
    client.post("/api/knowledge/ask", json={"question": "What is slump test?"})
    items = client.get("/api/history", params={"module": "knowledge"}).json()
    assert items and items[0]["module"] == "knowledge"
    assert client.delete(f"/api/history/{items[0]['id']}").status_code == 204
    assert client.delete(f"/api/history/{items[0]['id']}").status_code == 404


def test_extract_json_handles_fences():
    assert extract_json('Here you go:\n```json\n{"a": 1}\n```') == {"a": 1}
