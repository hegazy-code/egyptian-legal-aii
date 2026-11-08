"""Admin-only judgment review. Manual staging, approval and emergency unpublish.

No public ingestion route. No background publishing. Every state transition
is recorded in the existing audit_logs table in the same DB transaction.
"""
import json
import ipaddress
import os
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
from app.services.judgment_evidence_checks import check_review_evidence
from app.services.secure_judgment_retrieval import fetch_verified_html
from app.services.independent_judgment_verification import verify_retrieved_documents

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
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Judgment already exists for this court, number and year")
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
    if not judgment.full_text or not judgment.source_id or not judgment.court_id or not judgment.judgment_date:
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
    evidence_ok, issues = check_review_evidence(judgment.full_text, payload.verified_excerpt, payload.independent_excerpt)
    if not evidence_ok:
        raise HTTPException(422, {"evidence_issues": issues})
    approved_hosts = frozenset(
        host.strip().lower() for host in
        os.environ.get("JUDGMENT_VERIFIED_EVIDENCE_HOSTS", "").split(",")
        if host.strip()
    )
    primary_host = urlparse(payload.verified_source_url).hostname.lower()
    independent_host = urlparse(payload.independent_source_url).hostname.lower()
    if primary_host not in approved_hosts or independent_host not in approved_hosts:
        raise HTTPException(422, "Both publishers must be configured as trusted evidence hosts")
    # Distinct hostnames do not establish independent ownership. The operator
    # must explicitly map each trusted host to its verified publisher identity.
    try:
        publishers = json.loads(os.environ.get("JUDGMENT_EVIDENCE_PUBLISHER_IDS", "{}"))
    except (ValueError, TypeError):
        raise HTTPException(422, "Invalid publisher identity configuration")
    if not isinstance(publishers, dict):
        raise HTTPException(422, "Invalid publisher identity configuration")
    primary_publisher = publishers.get(primary_host)
    secondary_publisher = publishers.get(independent_host)
    if (not isinstance(primary_publisher, str) or not primary_publisher.strip()
            or not isinstance(secondary_publisher, str) or not secondary_publisher.strip()
            or primary_publisher.strip().casefold() == secondary_publisher.strip().casefold()):
        raise HTTPException(422, "Verified independent publisher identities required")
    # Server retrieves both documents independently; client-provided trust flags
    # and excerpts cannot bypass these network and content checks.
    try:
        primary = fetch_verified_html(
            payload.verified_source_url,
            allowed_hosts=approved_hosts,
        )
        secondary = fetch_verified_html(
            payload.independent_source_url,
            allowed_hosts=approved_hosts,
        )
    except Exception:
        raise HTTPException(422, "Independent source retrieval or TLS validation failed")
    verification = verify_retrieved_documents(
        judgment.full_text, primary, secondary,
        primary_excerpt=payload.verified_excerpt,
        independent_excerpt=payload.independent_excerpt,
        expected_primary_url=source.url,
    )
    if not verification.passed:
        raise HTTPException(422, {"verification_blockers": verification.blockers})
    db.add(JudgmentEvidence(
        judgment_id=judgment.id,
        reviewer_id=admin.id,
        source_url=payload.verified_source_url,
        independent_url=payload.independent_source_url,
        text_sha256=sha256(judgment.full_text.encode("utf-8")).hexdigest(),
        source_excerpt=payload.verified_excerpt,
        independent_excerpt=payload.independent_excerpt,
        review_reason=payload.reason,
        primary_sha256=verification.primary_sha256,
        independent_sha256=verification.independent_sha256,
        primary_fetched_at=primary.fetched_at,
        independent_fetched_at=secondary.fetched_at,
        verification_outcome="passed",
    ))
    judgment.status = "approved"
    _audit(db, admin, judgment, "judgment_approved", {"court_id": judgment.court_id, "text_sha256": sha256(judgment.full_text.encode("utf-8")).hexdigest(), "primary_sha256": verification.primary_sha256, "independent_sha256": verification.independent_sha256, "reviewer_id": admin.id})
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    return {"id": judgment.id, "status": "approved", "published": False}



class PublishDecision(BaseModel):
    reason: str = Field(min_length=10, max_length=2000)
    confirm_public_release: bool = False


@router.post("/{judgment_id}/publish")
def publish_judgment(
    judgment_id: str,
    payload: PublishDecision,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    """Explicit admin publication; public search only indexes published status."""
    if os.environ.get("JUDGMENT_MANUAL_PUBLICATION_ENABLED", "").lower() != "true":
        raise HTTPException(403, "Manual judgment publication is disabled")
    if not payload.confirm_public_release:
        raise HTTPException(422, "Explicit publication confirmation required")
    judgment = db.query(Judgment).filter(Judgment.id == judgment_id).with_for_update().first()
    if not judgment:
        raise HTTPException(404, "Judgment not found")
    if judgment.status != "approved":
        raise HTTPException(409, "Only approved judgments may be published")
    if not all((judgment.source_id, judgment.court_id, judgment.case_number,
                judgment.year, judgment.judgment_date, judgment.full_text)):
        raise HTTPException(422, "Judgment identity and full text required")
    evidence = (db.query(JudgmentEvidence)
                .filter(JudgmentEvidence.judgment_id == judgment.id,
                        JudgmentEvidence.verification_outcome == "passed")
                .order_by(JudgmentEvidence.recorded_at.desc()).first())
    if not evidence or evidence.text_sha256 != sha256(judgment.full_text.encode("utf-8")).hexdigest():
        raise HTTPException(422, "Matching verified evidence required")
    if not evidence.primary_sha256 or not evidence.independent_sha256:
        raise HTTPException(422, "Both retrieved source fingerprints required")
    judgment.status = "published"
    _audit(db, admin, judgment, "judgment_published", {
        "evidence_id": evidence.id, "text_sha256": evidence.text_sha256,
        "reason_sha256": sha256(payload.reason.encode("utf-8")).hexdigest(),
    })
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    return {"id": judgment.id, "status": "published"}


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
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    return {"id": judgment.id, "status": "unpublished"}
