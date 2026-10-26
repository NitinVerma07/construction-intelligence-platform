from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import CrackReport, Envelope
from ..services.fallbacks import crack_fallback
from ..services.images import read_image
from ..services.pipeline import run_module

router = APIRouter(prefix="/cracks", tags=["Crack detection"])

SYSTEM = (
    "Task: crack detection and analysis on concrete, masonry or plaster. Classify the crack "
    "(hairline, shrinkage, map/craze, vertical, horizontal, diagonal/shear, stair-step, settlement, "
    "flexural), judge severity and whether it indicates structural distress, list probable causes and "
    "concrete next steps. If the image does not show a crack, say so, set confidence low and "
    "crack_type 'No crack visible'. Always recommend a structural engineer for high or critical severity."
)


@router.post("/analyze", response_model=Envelope[CrackReport])
def analyze_crack(
    file: UploadFile = File(...),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    image = read_image(file)
    return run_module(
        db,
        module="cracks",
        system=SYSTEM,
        prompt=f"Analyse the crack in this photo. Extra notes from the user (location, width, age): {notes or 'none'}",
        model_cls=CrackReport,
        fallback=lambda: crack_fallback(notes),
        images=[image],
    )
