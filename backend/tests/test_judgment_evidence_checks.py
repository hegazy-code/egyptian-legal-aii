"""Deterministic offline evidence checks; no network calls."""
from app.services.judgment_evidence_checks import check_review_evidence, evidence_fingerprint


def test_valid_primary_quote_with_arabic_spacing():
    text = "حكم المحكمة   بشأن الدعوى رقم 123 لسنة 90. " * 5
    excerpt = "حكم المحكمة بشأن الدعوى رقم 123 لسنة 90."
    ok, issues = check_review_evidence(text, excerpt, "A separately sourced passage describing this judgment.")
    assert ok and not issues


def test_rejects_fabricated_primary_quote():
    ok, issues = check_review_evidence("A" * 120, "This quotation is absent from the original judgment.", "Independent evidence")
    assert not ok
    assert "primary_excerpt_not_in_judgment" in issues


def test_equal_excerpts_are_not_automatically_fraudulent():
    passage = "The same official ruling may be quoted by two different publishers."
    ok, issues = check_review_evidence(passage * 3, passage, passage)
    assert ok and not issues


def test_raw_bytes_fingerprint_is_stable():
    assert evidence_fingerprint(b"abc") == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
