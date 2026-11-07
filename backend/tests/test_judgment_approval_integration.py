"""Offline approval integration: network retrieval is mocked, DB writes are real."""
from datetime import date, datetime, timezone
import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.models import Base, Court, Judgment, Source, User, JudgmentEvidence
from app.models.system import AuditLog
from app.api import judgment_review
from app.services.independent_judgment_verification import RetrievedDocument

QUOTE = "This is an authentic passage of the original judicial decision."


@pytest.fixture
def prepared(monkeypatch):
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    monkeypatch.setenv("JUDGMENT_VERIFIED_EVIDENCE_HOSTS", "court.example.org,publisher.example.org")
    monkeypatch.setenv("JUDGMENT_EVIDENCE_PUBLISHER_IDS", '{"court.example.org":"court-operator","publisher.example.org":"independent-publisher"}')
    with Session(engine) as db:
        court = Court(name="Test Court")
        source = Source(name="Court", source_type="court", url="https://court.example.org/case")
        admin = User(email="review@example.org", hashed_password="!", role="admin")
        db.add_all([court, source, admin])
        db.flush()
        judgment = Judgment(
            court_id=court.id, source_id=source.id, case_number="77", year=90,
            judgment_date=date(2025, 1, 1), full_text=QUOTE * 3, status="draft",
        )
        db.add(judgment)
        db.commit()
        decision = judgment_review.ReviewDecision(
            reason="Original and independent source content reviewed",
            verified_source_url=source.url,
            independent_source_url="https://publisher.example.org/case",
            citation_verified=True, personal_data_cleared=True,
            source_authenticity_verified=True,
            verified_excerpt=QUOTE, independent_excerpt=QUOTE,
        )
        yield db, judgment, admin, decision
    engine.dispose()


def test_approval_saves_verified_documents_and_never_publishes(prepared, monkeypatch):
    db, judgment, admin, decision = prepared
    def fake_fetch(url, *, allowed_hosts):
        assert allowed_hosts == frozenset({"court.example.org", "publisher.example.org"})
        return RetrievedDocument(url, QUOTE.encode(), QUOTE, datetime.now(timezone.utc), True)
    monkeypatch.setattr(judgment_review, "fetch_verified_html", fake_fetch)
    response = judgment_review.approve_judgment(judgment.id, decision, db, admin)
    assert response["status"] == "approved"
    assert response["published"] is False
    evidence = db.query(JudgmentEvidence).filter_by(judgment_id=judgment.id).one()
    assert evidence.verification_outcome == "passed"
    assert len(evidence.primary_sha256) == 64
    audit = db.query(AuditLog).filter_by(action="judgment_approved").one()
    assert QUOTE not in audit.details
    assert decision.reason not in audit.details
    assert evidence.primary_sha256 in audit.details


def test_untrusted_second_document_blocks_approval(prepared, monkeypatch):
    db, judgment, admin, decision = prepared
    def fake_fetch(url, *, allowed_hosts):
        trusted = url.startswith("https://court.")
        return RetrievedDocument(url, QUOTE.encode(), QUOTE, datetime.now(timezone.utc), trusted)
    monkeypatch.setattr(judgment_review, "fetch_verified_html", fake_fetch)
    with pytest.raises(HTTPException) as exc:
        judgment_review.approve_judgment(judgment.id, decision, db, admin)
    assert exc.value.status_code == 422
    assert db.query(JudgmentEvidence).count() == 0
    assert db.get(Judgment, judgment.id).status == "draft"


def test_unconfigured_hosts_block_before_any_network_call(prepared, monkeypatch):
    db, judgment, admin, decision = prepared
    monkeypatch.delenv("JUDGMENT_VERIFIED_EVIDENCE_HOSTS")
    def no_fetch(*args, **kwargs):
        raise AssertionError("Network retrieval must not occur")
    monkeypatch.setattr(judgment_review, "fetch_verified_html", no_fetch)
    with pytest.raises(HTTPException) as exc:
        judgment_review.approve_judgment(judgment.id, decision, db, admin)
    assert exc.value.status_code == 422
    assert db.get(Judgment, judgment.id).status == "draft"


def test_same_publisher_operating_two_hosts_is_not_independent(prepared, monkeypatch):
    db, judgment, admin, decision = prepared
    monkeypatch.setenv("JUDGMENT_EVIDENCE_PUBLISHER_IDS",
                       '{"court.example.org":"same-company","publisher.example.org":"same-company"}')
    def no_fetch(*args, **kwargs):
        raise AssertionError("Publisher gate must block before network access")
    monkeypatch.setattr(judgment_review, "fetch_verified_html", no_fetch)
    with pytest.raises(HTTPException) as exc:
        judgment_review.approve_judgment(judgment.id, decision, db, admin)
    assert exc.value.status_code == 422
    assert db.query(JudgmentEvidence).count() == 0


def test_public_search_only_after_explicit_verified_publication(prepared, monkeypatch):
    from app.search.keyword import keyword_search_judgments
    db, judgment, admin, decision = prepared
    def fake_fetch(url, *, allowed_hosts):
        return RetrievedDocument(url, QUOTE.encode(), QUOTE, datetime.now(timezone.utc), True)
    monkeypatch.setattr(judgment_review, "fetch_verified_html", fake_fetch)
    judgment_review.approve_judgment(judgment.id, decision, db, admin)
    assert keyword_search_judgments(db, "authentic passage") == []
    payload = judgment_review.PublishDecision(reason="Approved for public legal reference", confirm_public_release=True)
    with pytest.raises(HTTPException) as disabled:
        judgment_review.publish_judgment(judgment.id, payload, db, admin)
    assert disabled.value.status_code == 403
    monkeypatch.setenv("JUDGMENT_MANUAL_PUBLICATION_ENABLED", "true")
    assert judgment_review.publish_judgment(judgment.id, payload, db, admin)["status"] == "published"
    assert len(keyword_search_judgments(db, "authentic passage")) == 1
    judgment_review.unpublish_judgment(judgment.id, reason="Emergency withdrawal for review", db=db, admin=admin)
    assert keyword_search_judgments(db, "authentic passage") == []


def test_publish_requires_matching_verified_evidence(prepared, monkeypatch):
    db, judgment, admin, decision = prepared
    monkeypatch.setenv("JUDGMENT_MANUAL_PUBLICATION_ENABLED", "true")
    payload = judgment_review.PublishDecision(reason="Approved for public legal reference", confirm_public_release=True)
    with pytest.raises(HTTPException) as draft:
        judgment_review.publish_judgment(judgment.id, payload, db, admin)
    assert draft.value.status_code == 409
    judgment.status = "approved"
    db.commit()
    with pytest.raises(HTTPException) as missing:
        judgment_review.publish_judgment(judgment.id, payload, db, admin)
    assert missing.value.status_code == 422
    assert db.get(Judgment, judgment.id).status == "approved"
