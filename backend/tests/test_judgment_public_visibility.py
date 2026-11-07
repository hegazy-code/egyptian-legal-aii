"""Public search must never leak drafts, approvals or unpublished rulings."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models import Base, Judgment
from app.search.keyword import keyword_search_judgments


@pytest.fixture
def db():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


def test_only_published_judgments_are_visible(db):
    for status in ("draft", "approved", "unpublished", "published"):
        db.add(Judgment(case_number=status, year=2026,
                        full_text="محكمة النقض اختبار الخصوصية", status=status))
    db.commit()
    results = keyword_search_judgments(db, "اختبار الخصوصية", limit=20)
    assert len(results) == 1
    assert "published" in results[0].title
    assert "unpublished" not in results[0].title


def test_new_judgment_is_draft_by_default(db):
    judgment = Judgment(case_number="new", year=2026, full_text="محكمة النقض")
    db.add(judgment)
    db.commit()
    assert judgment.status == "draft"
    assert keyword_search_judgments(db, "محكمة النقض") == []
