"""FastAPI entry point.  Run from /backend:  uvicorn app.main:app --reload"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import ROOT, settings
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


# Serve built frontend when present (e.g. unified deployment on Render/Railway)
DIST_DIR = ROOT / "frontend" / "dist"
if (DIST_DIR / "index.html").is_file():
    if (DIST_DIR / "assets").is_dir():
        app.mount("/assets", StaticFiles(directory=DIST_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        file_path = DIST_DIR / full_path
        if full_path and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(DIST_DIR / "index.html")
