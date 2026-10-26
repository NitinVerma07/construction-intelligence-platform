"""FastAPI entry point.  Run from /backend:  uvicorn app.main:app --reload"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import init_db
from .routers import assistant, cracks, history, knowledge, planning, safety, valuation, weather


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="AI-Powered Multimodal Construction Intelligence Platform",
    description="Safety monitoring, crack analysis, valuation, planning, weather advisory and "
                "knowledge assistance powered by a multimodal LLM with strict JSON contracts.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

for module in (safety, cracks, valuation, planning, assistant, knowledge, weather, history):
    app.include_router(module.router, prefix="/api")


@app.get("/api/health", tags=["System"])
def health():
    return {
        "status": "ok",
        "llm_mode": "demo" if settings.use_mock else "live",
        "model": settings.LLM_MODEL,
    }
