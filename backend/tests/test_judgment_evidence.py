"""Offline checks for court-scoped identity and private evidence persistence."""
from datetime import date, datetime, timezone
import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models import Base, Court, Judgment, JudgmentEvidence, User


@pytest.fixture
def db():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


def test_same_court_case_year_is_unique(db):
    court = Court(name="Court A")
    db.add(court)
    db.flush()
    db.add(Judgment(court_id=court.id, case_number="123", year=90, judgment_date=date(2025, 1, 1)))
    db.commit()
    db.add(Judgment(court_id=court.id, case_number="123", year=90, judgment_date=date(2025, 1, 1)))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_same_case_number_in_different_courts_is_allowed(db):
    a, b = Court(name="A"), Court(name="B")
    db.add_all([a, b])
    db.flush()
    db.add_all([
        Judgment(court_id=a.id, case_number="123", year=90),
        Judgment(court_id=b.id, case_number="123", year=90),
    ])
    db.commit()


def test_evidence_is_private_database_record(db):
    court = Court(name="A")
    reviewer = User(email="reviewer@example.org", hashed_password="!", role="admin")
    db.add_all([court, reviewer])
    db.flush()
    judgment = Judgment(court_id=court.id, case_number="12", year=90, status="approved", full_text="x" * 100)
    db.add(judgment)
    db.flush()
    evidence = JudgmentEvidence(
        judgment_id=judgment.id, reviewer_id=reviewer.id,
        source_url="https://court.example.org/case",
        independent_url="https://publisher.example.org/case",
        text_sha256="a" * 64, source_excerpt="court text", independent_excerpt="independent text",
        review_reason="Reviewed against documents",
        primary_sha256="b" * 64, independent_sha256="c" * 64,
        primary_fetched_at=datetime.now(timezone.utc),
        independent_fetched_at=datetime.now(timezone.utc),
        verification_outcome="passed",
    )
    db.add(evidence)
    db.commit()
    assert db.query(JudgmentEvidence).filter_by(judgment_id=judgment.id).count() == 1
    from app.search.keyword import keyword_search_judgments
    assert keyword_search_judgments(db, "x" * 10) == []
