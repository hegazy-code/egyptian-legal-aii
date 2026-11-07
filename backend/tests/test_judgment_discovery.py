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


def test_arabic_indic_year_supported():
    draft = prepare_draft(sample("محكمة النقض الطعن رقم ١٢٣ لسنة ٩٠ جلسة 01/02/2020"))
    assert draft["judgment_schema"]["year"] == 90


def test_script_content_is_not_evidence():
    import httpx
    from app.services.judgment_discovery import retrieve
    html = ('<html><script>محكمة النقض الطعن رقم 999 لسنة 90</script>'
            '<body>محكمة النقض الطعن رقم 123 لسنة 90 جلسة 01/02/2020</body></html>')
    def handler(request):
        return httpx.Response(200, headers={"content-type": "text/html"}, text=html)
    source = SourceConfig("fixture", "https://example.org", ("example.org",), enabled=True)
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        evidence = retrieve("https://example.org/test", source, client)
    assert "999" not in evidence.text
    assert prepare_draft(evidence)["evidence"]["case_number"] == "123"


def test_streaming_size_limit_rejects_oversized_response():
    import httpx
    import pytest
    from app.services.judgment_discovery import retrieve
    def handler(request):
        return httpx.Response(200, headers={"content-type": "text/html"},
                              content=b"a" * 2_000_001)
    source = SourceConfig("fixture", "https://example.org", ("example.org",), enabled=True)
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(ValueError, match="Oversized"):
            retrieve("https://example.org/large", source, client)


def test_redirects_rejected_even_if_destination_is_allowed():
    import httpx
    import pytest
    from app.services.judgment_discovery import retrieve
    def handler(request):
        return httpx.Response(302, headers={"location": "https://example.org/other"})
    source = SourceConfig("fixture", "https://example.org", ("example.org",), enabled=True)
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(ValueError, match="Redirect"):
            retrieve("https://example.org/redirect", source, client)
