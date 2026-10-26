"""Live weather via the free Open-Meteo API (no API key required)."""
import httpx

from ..schemas import DayForecast, WeatherSnapshot

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


class CityNotFound(Exception):
    pass


class WeatherUnavailable(Exception):
    pass


def fetch_weather(city: str) -> WeatherSnapshot:
    try:
        with httpx.Client(timeout=8.0) as client:
            geo = client.get(GEO_URL, params={"name": city, "count": 1}).json()
            places = geo.get("results") or []
            if not places:
                raise CityNotFound(city)
            p = places[0]
            data = client.get(
                FORECAST_URL,
                params={
                    "latitude": p["latitude"],
                    "longitude": p["longitude"],
                    "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
                    "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
                    "forecast_days": 3,
                    "timezone": "auto",
                },
            ).json()
        cur, daily = data["current"], data["daily"]
        forecast = [
            DayForecast(
                date=daily["time"][i],
                temp_max_c=daily["temperature_2m_max"][i],
                temp_min_c=daily["temperature_2m_min"][i],
                rain_mm=daily["precipitation_sum"][i] or 0,
                wind_max_kmh=daily["wind_speed_10m_max"][i],
            )
            for i in range(len(daily["time"]))
        ]
        return WeatherSnapshot(
            city=f"{p['name']}, {p.get('country', '')}".strip(", "),
            temperature_c=cur["temperature_2m"],
            humidity_pct=cur["relative_humidity_2m"],
            wind_kmh=cur["wind_speed_10m"],
            precipitation_mm=cur["precipitation"],
            forecast=forecast,
        )
    except CityNotFound:
        raise
    except Exception as exc:
        raise WeatherUnavailable(str(exc)) from exc
