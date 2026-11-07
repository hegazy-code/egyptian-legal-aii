"""URL validation is fail-closed and never contacts a remote host."""
import pytest
from app.api.judgment_review import _valid_evidence_url, StageJudgment


@pytest.mark.parametrize("url", [
    "https://www.example.org/judgments/123",
    "https://judgments.example.org:443/case",
])
def test_valid_public_provenance_urls(url):
    assert _valid_evidence_url(url)


@pytest.mark.parametrize("url", [
    "http://example.org/case", "https://127.0.0.1/case",
    "https://[::1]/case", "https://localhost/case",
    "https://example.org:8080/case", "https://user:password@example.org/case",
    "https://example.org@127.0.0.1/case",
    "https://bad..example.org/case", "https://example.org:broken/case",
    "javascript:alert(1)", "https://-example.org/case",
])
def test_invalid_provenance_urls(url):
    assert not _valid_evidence_url(url)


def test_judicial_year_allowed():
    assert StageJudgment(source_id="source", case_number="123", year=90, full_text="x" * 100).year == 90
