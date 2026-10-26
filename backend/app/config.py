"""Central configuration, loaded from environment variables / the root .env file."""
import os
from pathlib import Path

from dotenv import load_dotenv

# <project root>/backend/app/config.py -> parents[2] is the project root
ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")


class Settings:
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "claude-sonnet-5-5")
    # auto  -> live LLM if an API key is present, otherwise offline demo mode
    # live  -> always call the LLM
    # mock  -> never call the LLM (deterministic offline output)
    LLM_MODE: str = os.getenv("LLM_MODE", "auto").lower()
    DATABASE_URL: str = os.getenv("DATABASE_URL") or f"sqlite:///{ROOT / 'db' / 'construction.db'}"
    CORS_ORIGINS: list[str] = [
        o.strip()
        for o in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
        if o.strip()
    ]
    MAX_IMAGE_MB: int = int(os.getenv("MAX_IMAGE_MB", "5"))

    @property
    def use_mock(self) -> bool:
        if self.LLM_MODE == "mock":
            return True
        if self.LLM_MODE == "live":
            return False
        return not self.ANTHROPIC_API_KEY


settings = Settings()
