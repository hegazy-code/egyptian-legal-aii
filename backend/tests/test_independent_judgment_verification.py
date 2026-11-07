"""Independent document corroboration, without network or publication."""
from dataclasses import replace
from datetime import datetime, timezone
from app.services.independent_judgment_verification import (
    RetrievedDocument, verify_retrieved_documents,
)

PASSAGE = "Judgment number 123 of judicial year 90 issued by the court."


def documents():
    now = datetime.now(timezone.utc)
    primary = RetrievedDocument("https://court.example.org/123", PASSAGE.encode(), PASSAGE, now, True)
    independent = RetrievedDocument("https://publisher.example.org/123", ("Independent record: " + PASSAGE).encode(), "Independent record: " + PASSAGE, now, True)
    return primary, independent


def check(primary, independent):
    return verify_retrieved_documents(
        PASSAGE, primary, independent, primary_excerpt=PASSAGE,
        independent_excerpt=PASSAGE, expected_primary_url=primary.url,
    )


def test_two_authenticated_retrieved_documents_can_corroborate():
    assert check(*documents()).passed


def test_untrusted_reviewer_supplied_documents_fail():
    a, b = documents()
    result = check(replace(a, trusted_source=False), b)
    assert not result.passed
    assert "source_authentication_missing" in result.blockers


def test_second_source_must_contain_actual_quotation():
    a, b = documents()
    result = check(a, replace(b, extracted_text="Different text entirely"))
    assert not result.passed
    assert "independent_quote_not_corroborated" in result.blockers


def test_two_paths_on_same_host_are_not_independent():
    a, b = documents()
    result = check(a, replace(b, url="https://court.example.org/other"))
    assert not result.passed
    assert "sources_not_independent" in result.blockers


def test_fingerprints_match_actual_raw_bytes():
    from hashlib import sha256
    a, b = documents()
    result = check(a, b)
    assert result.primary_sha256 == sha256(a.raw).hexdigest()
    assert result.independent_sha256 == sha256(b.raw).hexdigest()
