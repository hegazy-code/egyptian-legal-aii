"""Admin-only judgment review. Manual staging, approval and emergency unpublish.

No public ingestion route. No background publishing. Every state transition
is recorded in the existing audit_logs table in the same DB transaction.
"""
import json
import ipaddress
from datetime import date
from hashlib import sha256

from fastapi import APIRouter, Depends, HTTPException, Query
from urllib.parse import urlparse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.api.deps import get_current_admin_user
from app.database import get_db
from app.models.judgments import Judgment, Court
from app.models.judgment_evidence import JudgmentEvidence
from app.models.legal import Source
from app.models.system import AuditLog
from app.models.users import User

router = APIRouter(prefix="/admin/judgments", tags=["admin-judgments"])


class StageJudgment(BaseModel):
    source_id: str
    court_id: str
    case_number: str = Field(min_length=1, max_length=100)
    year: int = Field(ge=1, le=2200)
    judgment_date: date
    full_text: str = Field(min_length=100)
    summary: str | None = None


class ReviewDecision(BaseModel):
    reason: str = Field(min_length=10, max_length=2000)
    verified_source_url: str = Field(min_length=8, max_length=1000)
    independent_source_url: str = Field(min_length=8, max_length=1000)
    citation_verified: bool
    personal_data_cleared: bool
    source_authenticity_verified: bool = False
    verified_excerpt: str = Field(min_length=30, max_length=5000)
    independent_excerpt: str = Field(min_length=30, max_length=5000)


def _valid_evidence_url(value: str) -> bool:
    """Allow only public DNS hostnames over HTTPS without credentials or custom ports."""
    try:
        parsed = urlparse(value)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            return False
        if parsed.port not in (None, 443):
            return False
        try:
            ipaddress.ip_address(parsed.hostname)
            return False
        except ValueError:
            pass
        labels = parsed.hostname.split(".")
        return len(labels) >= 2 and all(
            label and len(label) <= 63 and label[0].isalnum()
            and label[-1].isalnum() and all(c.isalnum() or c == "-" for c in label)
            for label in labels
        )
    except ValueError:
        return False


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
    if not source or not source.url or not _valid_evidence_url(source.url):
        raise HTTPException(422, "Verified HTTPS source record required")
    court = db.query(Court).filter(Court.id == payload.court_id).first()
    if not court:
        raise HTTPException(422, "Registered court required")
    existing = db.query(Judgment).filter(
        Judgment.court_id == court.id,
        Judgment.case_number == payload.case_number,
        Judgment.year == payload.year,
    ).first()
    if existing:
        raise HTTPException(409, "Possible duplicate judgment; review existing record")
    judgment = Judgment(
        source_id=source.id, court_id=court.id, case_number=payload.case_number,
        year=payload.year, judgment_date=payload.judgment_date, full_text=payload.full_text,
        summary=payload.summary, status="draft",
    )
    db.add(judgment)
    db.flush()
    _audit(db, admin, judgment, "judgment_draft_created", {"source_id": source.id, "court_id": court.id, "text_sha256": sha256(payload.full_text.encode("utf-8")).hexdigest()})
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Judgment already exists for this court, number and year")
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
    if not judgment.full_text or not judgment.source_id or not judgment.court_id:
        raise HTTPException(422, "Judgment text and source required")
    if not payload.citation_verified or not payload.personal_data_cleared or not payload.source_authenticity_verified:
        raise HTTPException(422, "Citation and privacy checks must pass")
    if not _valid_evidence_url(payload.verified_source_url) or not _valid_evidence_url(payload.independent_source_url):
        raise HTTPException(422, "Valid HTTPS evidence URLs with public hostnames required")
    if urlparse(payload.verified_source_url).hostname.lower() == urlparse(payload.independent_source_url).hostname.lower():
        raise HTTPException(422, "Independent corroboration must come from a different publisher host")
    source = db.query(Source).filter(Source.id == judgment.source_id).first()
    if not source or source.url != payload.verified_source_url:
        raise HTTPException(422, "Source URL must match registered provenance")
    if payload.verified_excerpt.strip() not in judgment.full_text:
        raise HTTPException(422, "Primary evidence excerpt must appear verbatim in judgment text")
    db.add(JudgmentEvidence(
        judgment_id=judgment.id,
        reviewer_id=admin.id,
        source_url=payload.verified_source_url,
        independent_url=payload.independent_source_url,
        text_sha256=sha256(judgment.full_text.encode("utf-8")).hexdigest(),
        source_excerpt=payload.verified_excerpt,
        independent_excerpt=payload.independent_excerpt,
        review_reason=payload.reason,
    ))
    judgment.status = "approved"
    _audit(db, admin, judgment, "judgment_approved", {**payload.model_dump(), "court_id": judgment.court_id, "text_sha256": sha256(judgment.full_text.encode("utf-8")).hexdigest()})
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
