"""LLM access layer.

Single entry point `generate_structured` that:
  1. calls the multimodal LLM (text + optional images),
  2. extracts a JSON object from the reply,
  3. validates it against a Pydantic model (the strict JSON data contract),
  4. retries once, then degrades to a deterministic fallback so the UI never breaks.
"""
import base64
import json
import logging
import re
from typing import Callable, Type, TypeVar

from pydantic import BaseModel

from ..config import settings
from .images import ImageInput

logger = logging.getLogger("llm")
M = TypeVar("M", bound=BaseModel)

SYSTEM_BASE = (
    "You are a senior construction engineer and project manager with 20+ years of experience "
    "in Indian and international construction practice (IS codes, NBC, OSHA). "
    "Be specific, practical and conservative on safety. Use INR for money and metric units "
    "unless the user says otherwise. "
    "You MUST reply with a single JSON object and nothing else: no markdown, no code fences, "
    "no commentary."
)


class LLMError(RuntimeError):
    pass


def extract_json(text: str) -> dict:
    """Pull the first JSON object out of a model reply (tolerates code fences)."""
    text = text.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if fenced:
        text = fenced.group(1).strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        raise LLMError("Model output contained no JSON object")
    return json.loads(text[start : end + 1])


def _call_anthropic(system: str, prompt: str, images: list[ImageInput] | None) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY, timeout=60.0)
    content: list[dict] = []
    for img in images or []:
        content.append(
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": img.media_type,
                    "data": base64.b64encode(img.data).decode(),
                },
            }
        )
    content.append({"type": "text", "text": prompt})
    resp = client.messages.create(
        model=settings.LLM_MODEL,
        max_tokens=2500,
        system=system,
        messages=[{"role": "user", "content": content}],
    )
    return "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")


def generate_structured(
    *,
    system: str,
    prompt: str,
    model_cls: Type[M],
    fallback: Callable[[], dict],
    images: list[ImageInput] | None = None,
) -> tuple[M, str]:
    """Return (validated_model, source) where source is 'llm', 'mock' or 'fallback'."""
    if settings.use_mock:
        return model_cls.model_validate(fallback()), "mock"

    schema = json.dumps(model_cls.model_json_schema())
    full_prompt = f"{prompt}\n\nReturn ONLY a JSON object that validates against this JSON Schema:\n{schema}"
    for attempt in (1, 2):
        try:
            raw = _call_anthropic(f"{SYSTEM_BASE}\n{system}", full_prompt, images)
            return model_cls.model_validate(extract_json(raw)), "llm"
        except Exception as exc:  # network, auth, parse or validation errors
            logger.warning("LLM attempt %d failed: %s", attempt, exc)
    return model_cls.model_validate(fallback()), "fallback"
