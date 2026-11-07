"""Review API regression: quoted primary evidence must match staged text."""
from datetime import date
from types import SimpleNamespace
import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.models import Base, Court, Judgment, Source, User, JudgmentEvidence
from app.api.judgment_review import ReviewDecision, approve_judgment


@pytest.fixture
def db():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


def test_approval_rejects_unmatched_primary_excerpt(db):
    court = Court(name="Test Court")
    source = Source(name="Primary", source_type="court", url="https://court.example.org/case")
    admin = User(email="admin@example.org", hashed_password="!", role="admin")
    db.add_all([court, source, admin])
    db.flush()
    judgment = Judgment(
        court_id=court.id, source_id=source.id, case_number="1", year=90,
        judgment_date=date(2025, 1, 1), full_text="A" * 120, status="draft",
    )
    db.add(judgment)
    db.commit()
    decision = ReviewDecision(
        reason="Manual review of source materials",
        verified_source_url=source.url,
        independent_source_url="https://independent.example.org/case",
        citation_verified=True, personal_data_cleared=True,
        source_authenticity_verified=True,
        verified_excerpt="This phrase does not exist in the judgment text.",
        independent_excerpt="A separate supporting source excerpt for the judgment.",
    )
    with pytest.raises(HTTPException) as exc:
        approve_judgment(judgment.id, decision, db, admin)
    assert exc.value.status_code == 422
    assert db.query(JudgmentEvidence).count() == 0
    assert db.get(Judgment, judgment.id).status == "draft"
