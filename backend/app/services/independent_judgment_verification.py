"""Independent, fail-closed corroboration of court judgments.

This verifies two *retrieved* documents, not reviewer assertions. The retrieval
adapter must independently authenticate provenance and prevent SSRF. No
automatic approval/publication is performed here.
"""
from dataclasses import dataclass
from hashlib import sha256
from urllib.parse import urlsplit
from datetime import datetime, timezone
from app.services.judgment_evidence_checks import normalized


@dataclass(frozen=True)
class RetrievedDocument:
    url: str
    raw: bytes
    extracted_text: str
    fetched_at: datetime
    trusted_source: bool = False


@dataclass(frozen=True)
class VerificationResult:
    passed: bool
    blockers: tuple[str, ...]
    primary_sha256: str
    independent_sha256: str
    primary_fetched_at: str
    independent_fetched_at: str


def _hostname(url: str) -> str:
    try:
        parsed = urlsplit(url)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            return ""
        if parsed.port not in (None, 443):
            return ""
        return parsed.hostname.lower().rstrip(".")
    except ValueError:
        return ""


def verify_retrieved_documents(
    judgment_text: str,
    primary: RetrievedDocument,
    independent: RetrievedDocument,
    *,
    primary_excerpt: str,
    independent_excerpt: str,
    expected_primary_url: str,
) -> VerificationResult:
    blockers = []
    primary_host = _hostname(primary.url)
    independent_host = _hostname(independent.url)
    if not primary_host or not independent_host or primary_host == independent_host:
        blockers.append("sources_not_independent")
    if primary.url != expected_primary_url:
        blockers.append("primary_url_mismatch")
    if not primary.trusted_source or not independent.trusted_source:
        blockers.append("source_authentication_missing")
    for name, document in (("primary", primary), ("independent", independent)):
        if not document.raw or not document.extracted_text:
            blockers.append(name + "_document_empty")
        if document.fetched_at.tzinfo is None or document.fetched_at > datetime.now(timezone.utc):
            blockers.append(name + "_invalid_retrieval_time")
    staged = normalized(judgment_text)
    first = normalized(primary_excerpt)
    second = normalized(independent_excerpt)
    if len(first) < 30 or first not in staged or first not in normalized(primary.extracted_text):
        blockers.append("primary_quote_not_corroborrated")
    if len(second) < 30 or second not in normalized(independent.extracted_text):
        blockers.append("independent_quote_not_corroborrated")
    return VerificationResult(
        passed=not blockers,
        blockers=tuple(blockers),
        primary_sha256=sha256(primary.raw).hexdigest(),
        independent_sha256=sha256(independent.raw).hexdigest(),
        primary_fetched_at=primary.fetched_at.isoformat(),
        independent_fetched_at=independent.fetched_at.isoformat(),
    )
