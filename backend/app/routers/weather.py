from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db, save_analysis
from ..schemas import Envelope, WeatherAdvisory, WeatherReport, WeatherRequest
from ..services.fallbacks import weather_advisory_fallback
from ..services.llm import generate_structured
from ..services.weather import CityNotFound, WeatherUnavailable, fetch_weather

router = APIRouter(prefix="/weather", tags=["Weather advisory"])

SYSTEM = (
    "Task: weather-aware construction advisory. Using the current conditions and 3-day forecast, "
    "state whether work is good / caution / stop for the given activity, and give specific "
    "recommendations (what to schedule, postpone or protect) and worker/material precautions."
)


@router.post("/advisory", response_model=Envelope[WeatherReport])
def weather_advisory(req: WeatherRequest, db: Session = Depends(get_db)):
    try:
        snapshot = fetch_weather(req.city)
    except CityNotFound:
        raise HTTPException(404, f"City '{req.city}' was not found.")
    except WeatherUnavailable:
        raise HTTPException(502, "Weather service is currently unreachable. Try again shortly.")

    advisory, source = generate_structured(
        system=SYSTEM,
        prompt=f"Activity: {req.activity}\nWeather: {snapshot.model_dump_json()}",
        model_cls=WeatherAdvisory,
        fallback=lambda: weather_advisory_fallback(snapshot, req.activity),
    )
    report = WeatherReport(weather=snapshot, advisory=advisory)
    analysis_id = save_analysis(db, "weather", advisory.summary, source, report.model_dump())
    return Envelope[WeatherReport](source=source, result=report, analysis_id=analysis_id)
