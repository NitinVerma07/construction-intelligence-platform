from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import AssistantReply, AssistantRequest, Envelope
from ..services.fallbacks import assistant_fallback
from ..services.pipeline import run_module

router = APIRouter(prefix="/assistant", tags=["Daily site assistant"])

SYSTEM = (
    "Task: daily site assistant for a site engineer or supervisor. Give a direct, practical answer "
    "followed by a short actionable checklist (max 8 items) and up to 3 follow-up questions that "
    "would sharpen the advice. priority is 'high' if safety or structural quality is at stake."
)


@router.post("/ask", response_model=Envelope[AssistantReply])
def ask(req: AssistantRequest, db: Session = Depends(get_db)):
    return run_module(
        db,
        module="assistant",
        system=SYSTEM,
        prompt=f"Site context: {req.site_context or 'not provided'}\nQuestion: {req.query}",
        model_cls=AssistantReply,
        fallback=lambda: assistant_fallback(req.query, req.site_context),
        summary_of=lambda r: r.answer,
    )
