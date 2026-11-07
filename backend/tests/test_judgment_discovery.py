"""Offline regression checks; never contact production or publish."""
from hashlib import sha256

from app.services.judgment_discovery import (
    Evidence, SourceConfig, contradictions, discover, prepare_draft, run_batch,
)


def sample(text="محكمة النقض الطعن رقم 123 لسنة 90 جلسة 01/02/2020"):
    return Evidence("https://example.org/judgment/123", text, sha256(text.encode()).hexdigest())


def test_draft_never_auto_publishes():
    draft = prepare_draft(sample())
    assert draft["judgment_schema"]["status"] == "draft"
    assert draft["publication_eligible"] is False
    assert draft["review_status"] == "pending_admin_review"
    assert draft["evidence"]["case_number"] == "123"


def test_missing_fields_blocked():
    draft = prepare_draft(sample("محكمة النقض"))
    assert "missing_case_number" in draft["blockers"]


def test_conflicting_dates_detected():
    a = prepare_draft(sample())["evidence"]
    b = dict(a, judgment_date_literal="02/02/2020")
    assert contradictions([a, b]) == ["judgment_date_literal"]


def test_duplicate_hash_and_case_number():
    drafts = run_batch([sample(), sample()])
    assert "duplicate_judgment" in drafts[1]["blockers"]


def test_ten_offline_fixtures_never_published():
    items = [sample(f"محكمة النقض الطعن رقم {100+i} لسنة 90 جلسة 01/02/2020") for i in range(10)]
    drafts = run_batch(items)
    assert len(drafts) == 10
    assert all(not draft["publication_eligible"] for draft in drafts)
    assert len({d["duplicate_key"] for d in drafts}) == 10


def test_source_disabled_by_default():
    import httpx
    source = SourceConfig("example", "https://example.org", ("example.org",))
    with httpx.Client() as client:
        assert discover(source, client) == []
