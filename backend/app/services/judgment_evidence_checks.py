"""Offline consistency checks for reviewer-supplied judicial evidence.

These checks do not fetch URLs and do not establish authenticity. The caller
must obtain documents from independently authenticated, permitted sources.
"""
from hashlib import sha256
import re
import unicodedata


def normalized(value: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", value)).strip()


def check_review_evidence(
    judgment_text: str,
    primary_excerpt: str,
    independent_excerpt: str,
) -> tuple[bool, tuple[str, ...]]:
    """Reject quotations not supported by staged text; never claim authenticity."""
    issues = []
    text = normalized(judgment_text)
    primary = normalized(primary_excerpt)
    independent = normalized(independent_excerpt)
    if len(primary) < 30 or primary not in text:
        issues.append("primary_excerpt_not_in_judgment")
    if len(independent) < 30:
        issues.append("independent_excerpt_too_short")
    # A second publisher may quote exactly the same ruling; equality is valid.
    return not issues, tuple(issues)


def evidence_fingerprint(raw: bytes) -> str:
    """Content fingerprint; callers must preserve the raw source bytes."""
    return sha256(raw).hexdigest()
