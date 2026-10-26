import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import Analysis, get_db
from ..schemas import HistoryItem

router = APIRouter(prefix="/history", tags=["History"])


@router.get("", response_model=list[HistoryItem])
def list_history(
    module: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    query = select(Analysis).order_by(Analysis.id.desc()).limit(limit)
    if module:
        query = query.where(Analysis.module == module)
    return [
        HistoryItem(
            id=r.id, module=r.module, summary=r.summary, source=r.source,
            created_at=r.created_at, result=json.loads(r.result_json),
        )
        for r in db.scalars(query).all()
    ]


@router.delete("/{item_id}", status_code=204)
def delete_history(item_id: int, db: Session = Depends(get_db)):
    row = db.get(Analysis, item_id)
    if not row:
        raise HTTPException(404, "History item not found.")
    db.delete(row)
    db.commit()
