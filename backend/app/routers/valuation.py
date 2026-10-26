import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import Envelope, ValuationReport, ValuationRequest
from ..services.fallbacks import valuation_baseline
from ..services.pipeline import run_module

router = APIRouter(prefix="/valuation", tags=["Real estate valuation"])

SYSTEM = (
    "Task: real estate valuation for the Indian market. You receive property details and a "
    "rule-based baseline estimate. Refine it using your knowledge of the city/locality, stay within "
    "+/-35% of the baseline unless you clearly justify more, list the key value drivers, and give a "
    "realistic low-high range. State that this is indicative, not a certified valuation."
)


@router.post("/estimate", response_model=Envelope[ValuationReport])
def estimate(req: ValuationRequest, db: Session = Depends(get_db)):
    baseline = valuation_baseline(req)
    prompt = (
        f"Property: {req.model_dump_json()}\n"
        f"Baseline estimate: {json.dumps(baseline)}\n"
        "Return the refined valuation."
    )
    return run_module(
        db,
        module="valuation",
        system=SYSTEM,
        prompt=prompt,
        model_cls=ValuationReport,
        fallback=lambda: baseline,
    )
