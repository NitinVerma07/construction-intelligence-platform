"""SQLite (SQLAlchemy 2.0) persistence for analysis history."""
import json
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from .config import settings

_is_sqlite = settings.DATABASE_URL.startswith("sqlite")
if settings.DATABASE_URL.startswith("sqlite:///"):
    Path(settings.DATABASE_URL.replace("sqlite:///", "", 1)).parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if _is_sqlite else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    module: Mapped[str] = mapped_column(String(32), index=True)
    summary: Mapped[str] = mapped_column(String(255))
    source: Mapped[str] = mapped_column(String(16))  # llm | mock | fallback
    result_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )


def init_db() -> None:
    Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def save_analysis(db: Session, module: str, summary: str, source: str, result: dict) -> int:
    row = Analysis(
        module=module,
        summary=(summary or "")[:250],
        source=source,
        result_json=json.dumps(result, default=str),
    )
    db.add(row)
    db.commit()
    return row.id
