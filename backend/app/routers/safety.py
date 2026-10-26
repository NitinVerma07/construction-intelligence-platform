from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import Envelope, SafetyReport
from ..services.fallbacks import safety_fallback
from ..services.images import read_image
from ..services.pipeline import run_module

router = APIRouter(prefix="/safety", tags=["Site safety"])

SYSTEM = (
    "Task: construction site safety monitoring. Inspect the photo for PPE (hard hat, hi-vis vest, "
    "safety shoes, gloves, harness), working-at-height hazards, unprotected edges and openings, "
    "scaffold condition, electrical hazards, housekeeping, machinery and fire risks. "
    "Only report what is visible; do not invent hazards. risk_score: 0 safe to 100 extreme."
)


@router.post("/analyze", response_model=Envelope[SafetyReport])
def analyze_safety(
    file: UploadFile = File(...),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    image = read_image(file)
    return run_module(
        db,
        module="safety",
        system=SYSTEM,
        prompt=f"Assess the safety of this construction site photo. Extra notes from the user: {notes or 'none'}",
        model_cls=SafetyReport,
        fallback=lambda: safety_fallback(notes),
        images=[image],
    )
