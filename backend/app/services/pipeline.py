"""Shared request pipeline: LLM -> validated contract -> history -> envelope."""
from typing import Callable, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import save_analysis
from ..schemas import Envelope
from .images import ImageInput
from .llm import generate_structured

M = TypeVar("M", bound=BaseModel)


def run_module(
    db: Session,
    *,
    module: str,
    system: str,
    prompt: str,
    model_cls: Type[M],
    fallback: Callable[[], dict],
    images: list[ImageInput] | None = None,
    summary_of: Callable[[M], str] = lambda r: getattr(r, "summary", ""),
) -> Envelope:
    result, source = generate_structured(
        system=system, prompt=prompt, model_cls=model_cls, fallback=fallback, images=images
    )
    analysis_id = save_analysis(db, module, summary_of(result), source, result.model_dump())
    return Envelope[model_cls](source=source, result=result, analysis_id=analysis_id)
