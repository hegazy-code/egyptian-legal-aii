"""Conservative, read-only court judgment discovery and draft verification.

No database writes, AI fabrication, or publication side effects.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
from html.parser import HTMLParser
from urllib.parse import urlparse, urljoin
import re
import unicodedata
import ipaddress

import httpx


@dataclass(frozen=True)
class SourceConfig:
    name: str
    index_url: str
    allowed_hosts: tuple[str, ...]
    enabled: bool = False


@dataclass(frozen=True)
class Evidence:
    source_url: str
    text: str
    sha256: str


class _HTMLText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.links = []
        self.href = None
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self.skip_depth += 1
        if tag == "a" and not self.skip_depth:
            self.href = dict(attrs).get("href")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self.skip_depth:
            self.skip_depth -= 1
        if tag == "a":
            self.href = None

    def handle_data(self, data):
        if self.skip_depth:
            return
        self.parts.append(data)
        if self.href and data.strip():
            self.links.append((data.strip(), self.href))


def _host_allowed(url: str, hosts: tuple[str, ...]) -> bool:
    p = urlparse(url)
    if p.scheme != "https" or not p.hostname or p.username or p.password:
        return False
    try:
        if p.port not in (None, 443):
            return False
    except ValueError:
        return False
    try:
        ipaddress.ip_address(p.hostname)
        return False
    except ValueError:
        pass
    return p.hostname.lower().rstrip(".") in {h.lower().rstrip(".") for h in hosts}


def _bounded_html(url: str, client: httpx.Client) -> tuple[str, bytes]:
    """Read no more than 2 MB from the network; reject redirects and non-HTML."""
    chunks = []
    total = 0
    with client.stream("GET", url, follow_redirects=False, timeout=15) as response:
        if response.is_redirect:
            raise ValueError("Redirect rejected")
        response.raise_for_status()
        if "text/html" not in response.headers.get("content-type", "").lower():
            raise ValueError("HTML response required")
        for chunk in response.iter_bytes():
            total += len(chunk)
            if total > 2_000_000:
                raise ValueError("Oversized source rejected")
            chunks.append(chunk)
        encoding = response.encoding or "utf-8"
    raw = b"".join(chunks)
    return raw.decode(encoding, errors="replace"), raw


def discover(source: SourceConfig, client: httpx.Client, max_links: int = 25) -> list[str]:
    """Discover links only from explicitly enabled, HTTPS allowlisted indexes."""
    if not source.enabled or not _host_allowed(source.index_url, source.allowed_hosts):
        return []
    html, _ = _bounded_html(source.index_url, client)
    parser = _HTMLText()
    parser.feed(html)
    links = []
    for _, href in parser.links:
        url = urljoin(source.index_url, href).split("#")[0]
        if _host_allowed(url, source.allowed_hosts) and url not in links:
            links.append(url)
        if len(links) >= max_links:
            break
    return links


def retrieve(url: str, source: SourceConfig, client: httpx.Client) -> Evidence:
    if not source.enabled or not _host_allowed(url, source.allowed_hosts):
        raise ValueError("Source not enabled or URL outside allowlist")
    html, raw = _bounded_html(url, client)
    parser = _HTMLText()
    parser.feed(html)
    text = re.sub(r"\s+", " ", " ".join(parser.parts)).strip()
    return Evidence(url, text, sha256(raw).hexdigest())


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[\u064b-\u065f\u0670]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def extract(evidence: Evidence) -> dict:
    """Only literal text matches; all fields remain unverified until reviewed."""
    text = normalize(evidence.text)
    number = re.search(r"(?:الطعن|الدعوى)\s+رقم\s+([0-9٠-٩]+)\s+لسنة\s+([0-9٠-٩]+)", text)
    date = re.search(r"(?:جلسة|بتاريخ)\s+([0-9٠-٩]{1,2}[/\-][0-9٠-٩]{1,2}[/\-][0-9٠-٩]{4})", text)
    court = next((name for name in ("محكمة النقض", "المحكمة الدستورية العليا", "المحكمة الإدارية العليا") if name in text), None)
    return {
        "case_number": number.group(1) if number else None,
        "year": number.group(2) if number else None,
        "court": court,
        "judgment_date_literal": date.group(1) if date else None,
        "source_url": evidence.source_url,
        "source_sha256": evidence.sha256,
        "evidence_excerpt": text[:600],
    }


def duplicate_key(fields: dict) -> str | None:
    if not all(fields.get(k) for k in ("case_number", "year", "court")):
        return None
    return "|".join(normalize(str(fields[k])) for k in ("court", "case_number", "year"))


def contradictions(records: list[dict]) -> list[str]:
    conflicts = []
    for field in ("court", "case_number", "year", "judgment_date_literal"):
        values = {normalize(str(r[field])) for r in records if r.get(field)}
        if len(values) > 1:
            conflicts.append(field)
    return conflicts


def prepare_draft(evidence: Evidence, comparisons: list[dict] | None = None) -> dict:
    fields = extract(evidence)
    conflicts = contradictions([fields] + (comparisons or []))
    blockers = []
    for field in ("court", "case_number", "year", "judgment_date_literal"):
        if not fields.get(field):
            blockers.append("missing_" + field)
    if conflicts:
        blockers.append("contradictory_sources")
    blockers.extend(["independent_source_verification_required", "human_legal_review_required"])
    return {
        "judgment_schema": {
            "case_number": fields["case_number"],
            "year": int(fields["year"]) if fields["year"] and fields["year"].isdecimal() else None,
            "summary": None,
            "full_text": evidence.text,
            "status": "draft",
        },
        "evidence": fields,
        "duplicate_key": duplicate_key(fields),
        "contradictions": conflicts,
        "publication_eligible": False,
        "blockers": blockers,
        "review_status": "pending_admin_review",
    }


def run_batch(evidence_items: list[Evidence]) -> list[dict]:
    seen_hashes = set()
    seen_keys = set()
    output = []
    for evidence in evidence_items:
        draft = prepare_draft(evidence)
        key = draft["duplicate_key"]
        if evidence.sha256 in seen_hashes or (key and key in seen_keys):
            draft["blockers"].append("duplicate_judgment")
        seen_hashes.add(evidence.sha256)
        if key:
            seen_keys.add(key)
        output.append(draft)
    return output
