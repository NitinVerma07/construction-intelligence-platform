import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import Envelope, PlanningRequest, ProjectPlan
from ..services.fallbacks import planning_baseline
from ..services.pipeline import run_module

router = APIRouter(prefix="/planning", tags=["Construction planning"])

SYSTEM = (
    "Task: construction project planning. You receive project parameters and a rule-based baseline "
    "plan. Produce a realistic phase-wise schedule (durations in weeks, concrete tasks per phase), "
    "material quantity estimates, a cost breakdown whose percents sum to 100 and amounts that sum "
    "to total_estimated_cost_inr, and the main project risks for the location and season. "
    "If a budget is given, total_estimated_cost_inr must equal it unless clearly infeasible (explain in summary)."
)


@router.post("/generate", response_model=Envelope[ProjectPlan])
def generate_plan(req: PlanningRequest, db: Session = Depends(get_db)):
    baseline = planning_baseline(req)
    prompt = f"Project: {req.model_dump_json()}\nBaseline plan: {json.dumps(baseline)}\nReturn the refined plan."
    return run_module(
        db,
        module="planning",
        system=SYSTEM,
        prompt=prompt,
        model_cls=ProjectPlan,
        fallback=lambda: baseline,
    )
