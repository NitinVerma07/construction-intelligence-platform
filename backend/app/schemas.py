"""Strict JSON data contracts shared by the API, the LLM prompts and the React frontend."""
from datetime import datetime
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, Field

Severity = Literal["low", "medium", "high", "critical"]
Source = Literal["llm", "mock", "fallback"]
T = TypeVar("T")


class Envelope(BaseModel, Generic[T]):
    """Every module returns {source, analysis_id, result}."""

    source: Source
    result: T
    analysis_id: int | None = None


# ---------- Site safety ----------
class SafetyFinding(BaseModel):
    issue: str
    severity: Severity
    recommendation: str


class SafetyReport(BaseModel):
    risk_level: Severity
    risk_score: int = Field(ge=0, le=100, description="0 = safe, 100 = extreme hazard")
    ppe_detected: list[str] = Field(default_factory=list)
    ppe_missing: list[str] = Field(default_factory=list)
    findings: list[SafetyFinding] = Field(default_factory=list)
    summary: str


# ---------- Crack detection ----------
class CrackReport(BaseModel):
    crack_type: str
    severity: Severity
    structural_risk: bool
    probable_causes: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    urgency: Literal["monitor", "repair_soon", "immediate"]
    confidence: float = Field(ge=0, le=1)
    summary: str


# ---------- Real estate valuation ----------
class ValuationRequest(BaseModel):
    city: str = Field(min_length=2, max_length=80)
    locality: str = Field("", max_length=120)
    property_type: Literal["apartment", "independent_house", "villa", "plot", "commercial"] = "apartment"
    area_sqft: float = Field(gt=100, le=1_000_000)
    bedrooms: int = Field(2, ge=0, le=20)
    age_years: int = Field(0, ge=0, le=150)
    quality: Literal["basic", "standard", "premium", "luxury"] = "standard"
    amenities: list[str] = Field(default_factory=list, max_length=20)


class ValuationFactor(BaseModel):
    name: str
    impact: Literal["positive", "negative", "neutral"]
    note: str


class ValuationReport(BaseModel):
    estimated_value_inr: float
    price_per_sqft_inr: float
    range_low_inr: float
    range_high_inr: float
    confidence: Literal["low", "medium", "high"]
    factors: list[ValuationFactor] = Field(default_factory=list)
    summary: str


# ---------- Construction planning ----------
class PlanningRequest(BaseModel):
    project_type: Literal["residential", "commercial", "industrial", "infrastructure"] = "residential"
    location: str = Field(min_length=2, max_length=80)
    built_up_area_sqft: float = Field(gt=100, le=5_000_000)
    floors: int = Field(1, ge=1, le=100)
    budget_inr: float | None = Field(None, gt=0)
    duration_months: int | None = Field(None, ge=1, le=120)


class Phase(BaseModel):
    name: str
    duration_weeks: int = Field(ge=1)
    tasks: list[str] = Field(default_factory=list)


class MaterialEstimate(BaseModel):
    material: str
    quantity: float
    unit: str


class CostItem(BaseModel):
    category: str
    percent: float
    amount_inr: float


class ProjectPlan(BaseModel):
    total_estimated_cost_inr: float
    total_duration_weeks: int
    phases: list[Phase]
    materials: list[MaterialEstimate] = Field(default_factory=list)
    cost_breakdown: list[CostItem] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    summary: str


# ---------- Daily site assistant ----------
class AssistantRequest(BaseModel):
    query: str = Field(min_length=3, max_length=2000)
    site_context: str = Field("", max_length=2000)


class AssistantReply(BaseModel):
    answer: str
    priority: Literal["low", "normal", "high"] = "normal"
    checklist: list[str] = Field(default_factory=list)
    follow_ups: list[str] = Field(default_factory=list)


# ---------- Knowledge assistant ----------
class KnowledgeRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)


class KnowledgeReply(BaseModel):
    answer: str
    key_points: list[str] = Field(default_factory=list)
    standards: list[str] = Field(default_factory=list)


# ---------- Weather advisory ----------
class WeatherRequest(BaseModel):
    city: str = Field(min_length=2, max_length=80)
    activity: str = Field("general construction", max_length=120)


class DayForecast(BaseModel):
    date: str
    temp_max_c: float
    temp_min_c: float
    rain_mm: float
    wind_max_kmh: float


class WeatherSnapshot(BaseModel):
    city: str
    temperature_c: float
    humidity_pct: float
    wind_kmh: float
    precipitation_mm: float
    forecast: list[DayForecast] = Field(default_factory=list)


class WeatherAdvisory(BaseModel):
    work_suitability: Literal["good", "caution", "stop"]
    recommendations: list[str] = Field(default_factory=list)
    precautions: list[str] = Field(default_factory=list)
    summary: str


class WeatherReport(BaseModel):
    weather: WeatherSnapshot
    advisory: WeatherAdvisory


# ---------- History ----------
class HistoryItem(BaseModel):
    id: int
    module: str
    summary: str
    source: str
    created_at: datetime
    result: dict
