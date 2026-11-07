"""Admin-only judgment review. Manual staging, approval and emergency unpublish.

No public ingestion route. No background publishing. Every state transition
is recorded in the existing audit_logs table in the same DB transaction.
"""
import json

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin_user
from app.database import get_db
from app.models.judgments import Judgment
from app.models.legal import Source
from app.models.system import AuditLog
from app.models.users import User

router = APIRouter(prefix="/admin/judgments", tags=["admin-judgments"])


class StageJudgment(BaseModel):
    source_id: str
    case_number: str = Field(min_length=1, max_length=100)
    year: int = Field(ge=1800, le=2200)
    full_text: str = Field(min_length=100)
    summary: str | None = None


class ReviewDecision(BaseModel):
    reason: str = Field(min_length=10, max_length=2000)
    verified_source_url: str = Field(min_length=8, max_length=1000)
    independent_source_url: str = Field(min_length=8, max_length=1000)
    citation_verified: bool
    personal_data_cleared: bool


def _audit(db, admin, judgment, action, details):
    db.add(AuditLog(
        user_id=admin.id, action=action, entity_type="judgment",
        entity_id=judgment.id, details=json.dumps(details, ensure_ascii=False),
    ))


@router.post("/drafts", status_code=201)
def stage_judgment(
    payload: StageJudgment,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    source = db.query(Source).filter(Source.id == payload.source_id).first()
    if not source or not source.url or not source.url.startswith("https://"):
        raise HTTPException(422, "Verified HTTPS source record required")
    existing = db.query(Judgment).filter(
        Judgment.case_number == payload.case_number, Judgment.year == payload.year
    ).first()
    if existing:
        raise HTTPException(409, "Possible duplicate judgment; review existing record")
    judgment = Judgment(
        source_id=source.id, case_number=payload.case_number,
        year=payload.year, full_text=payload.full_text,
        summary=payload.summary, status="draft",
    )
    db.add(judgment)
    db.flush()
    _audit(db, admin, judgment, "judgment_draft_created", {"source_id": source.id})
    db.commit()
    return {"id": judgment.id, "status": judgment.status}


@router.get("/drafts")
def list_drafts(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    items = db.query(Judgment).filter(Judgment.status == "draft").limit(100).all()
    return [{"id": j.id, "case_number": j.case_number, "year": j.year, "source_id": j.source_id} for j in items]


@router.post("/{judgment_id}/approve")
def approve_judgment(
    judgment_id: str,
    payload: ReviewDecision,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    # Approval records human verification, but NEVER publishes.
    judgment = db.query(Judgment).filter(Judgment.id == judgment_id).with_for_update().first()
    if not judgment:
        raise HTTPException(404, "Judgment not found")
    if judgment.status != "draft":
        raise HTTPException(409, "Only draft judgments can be approved")
    if not judgment.full_text or not judgment.source_id:
        raise HTTPException(422, "Judgment text and source required")
    if not payload.citation_verified or not payload.personal_data_cleared:
        raise HTTPException(422, "Citation and privacy checks must pass")
    if payload.verified_source_url == payload.independent_source_url:
        raise HTTPException(422, "Independent corroborating source required")
    source = db.query(Source).filter(Source.id == judgment.source_id).first()
    if not source or source.url != payload.verified_source_url:
        raise HTTPException(422, "Source URL must match registered provenance")
    judgment.status = "approved"
    _audit(db, admin, judgment, "judgment_approved", payload.model_dump())
    db.commit()
    return {"id": judgment.id, "status": "approved", "published": False}


@router.post("/{judgment_id}/unpublish")
def unpublish_judgment(
    judgment_id: str,
    reason: str = Query(min_length=10),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    judgment = db.query(Judgment).filter(Judgment.id == judgment_id).with_for_update().first()
    if not judgment:
        raise HTTPException(404, "Judgment not found")
    prior = judgment.status
    judgment.status = "unpublished"
    _audit(db, admin, judgment, "judgment_unpublished", {"prior_status": prior, "reason": reason})
    db.commit()
    return {"id": judgment.id, "status": "unpublished"}
