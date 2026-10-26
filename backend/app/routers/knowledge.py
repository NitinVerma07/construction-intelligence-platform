from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import Envelope, KnowledgeReply, KnowledgeRequest
from ..services.fallbacks import knowledge_fallback
from ..services.pipeline import run_module

router = APIRouter(prefix="/knowledge", tags=["Construction knowledge"])

SYSTEM = (
    "Task: construction knowledge assistant. Answer technical questions on materials, methods, "
    "codes (IS, NBC, ACI, Eurocode where relevant), testing and best practice. Be accurate and concise; "
    "cite code names/clauses only when you are confident, and otherwise leave 'standards' empty. "
    "Recommend a licensed engineer for design decisions."
)


@router.post("/ask", response_model=Envelope[KnowledgeReply])
def ask_knowledge(req: KnowledgeRequest, db: Session = Depends(get_db)):
    return run_module(
        db,
        module="knowledge",
        system=SYSTEM,
        prompt=f"Question: {req.question}",
        model_cls=KnowledgeReply,
        fallback=lambda: knowledge_fallback(req.question),
        summary_of=lambda r: r.answer,
    )
