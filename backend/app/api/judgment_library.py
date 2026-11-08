"""Public, read-only judicial library. Never exposes drafts or user case files."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.judgments import Judgment

router = APIRouter(prefix="/library/judgments", tags=["judgment-library"])


def serialize(j):
    return {
        "id": j.id,
        "court": j.court.name if j.court else None,
        "case_number": j.case_number,
        "judicial_year": j.year,
        "judgment_date": j.judgment_date.isoformat() if j.judgment_date else None,
        "summary": j.summary,
        "source_url": j.source.url if j.source else None,
        "status": "published",
    }


@router.get("")
def list_published_judgments(
    q: str = Query("", max_length=120),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Judgment).options(joinedload(Judgment.court), joinedload(Judgment.source)).filter(Judgment.status == "published")
    if q.strip():
        term = f"%{q.strip()}%"
        query = query.filter(Judgment.case_number.ilike(term) | Judgment.summary.ilike(term))
    rows = query.order_by(Judgment.judgment_date.desc(), Judgment.id).offset(offset).limit(limit).all()
    return {"items": [serialize(j) for j in rows], "limit": limit, "offset": offset}


@router.get("/{judgment_id}")
def get_published_judgment(judgment_id: str, db: Session = Depends(get_db)):
    item = db.query(Judgment).options(joinedload(Judgment.court), joinedload(Judgment.source)).filter(Judgment.id == judgment_id, Judgment.status == "published").first()
    if not item:
        raise HTTPException(status_code=404, detail="Judgment not found")
    return serialize(item)
