#!/usr/bin/env python3
"""
Fetch and ingest Egyptian law source documents from confirmed Tier-1 sources.

This script downloads law PDFs/texts from the trusted domain allowlist and
runs them through ingest_documents.py's pipeline. Run this BEFORE
split_articles.py and create_embeddings.py.

Sources used (all Tier 1 per docs/legal-source-policy.md):
  - eastlaws.com        — Official Gazette text database (primary)
  - manshurat.org       — Legal publications (secondary cross-check)
  - moj.gov.eg          — Ministry of Justice (official government)
  - manpower.gov.eg     — Ministry of Labour (Labor Law 14/2025)
  - fra.gov.eg          — Financial Regulatory Authority

Laws registered here (matches data/inventory/legal_sources.xlsx + additions):
  LAW-001  قانون العقوبات       Penal Code           58/1937   (criminal)
  LAW-002  القانون المدني        Civil Code           131/1948  (civil)
  LAW-003  قانون الشركات        Companies Law        159/1981  (commercial)
  LAW-004  قانون حماية المستهلك Consumer Protection  181/2018  (consumer)
  LAW-005  قانون العمل          Labor Law            14/2025   (labor)      ← new
  LAW-006  قانون التجارة        Commercial Code      17/1999   (commercial) ← new
  LAW-007  قانون سوق المال      Capital Markets Law  95/1992   (financial)  ← new (FRA)

Usage:
    # Ingest everything registered here
    python scripts/fetch_law_sources.py

    # Ingest one specific law by its ID
    python scripts/fetch_law_sources.py --law-id LAW-005

    # Dry run: print what would be fetched without downloading
    python scripts/fetch_law_sources.py --dry-run

    # Use a specific output directory (default: data/raw/)
    python scripts/fetch_law_sources.py --data-raw-root data/raw/
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    print("ERROR: requests not installed. Run: pip install -r scripts/requirements.txt", file=sys.stderr)
    sys.exit(1)

DATA_RAW_ROOT = Path("data/raw")

# ---------------------------------------------------------------------------
# Source registry
# Each entry maps to one law document we want to ingest.
# primary_url: best confirmed Tier-1 URL (direct PDF or HTML text page).
# fallback_url: secondary source if primary fails or requires auth.
# notes: human-readable reminder about this source's status.
# ---------------------------------------------------------------------------

@dataclass
class LawSource:
    id: str
    law_number: str
    year: int
    name_ar: str
    name_en: str
    area: str
    slug: str
    primary_url: str
    fallback_url: str = ""
    gazette_issue: str = ""
    gazette_date: str = ""
    tier: int = 1
    notes: str = ""
    # Set to False if the URL is known to require auth or block bots
    downloadable: bool = True


LAW_SOURCES: List[LawSource] = [
    LawSource(
        id="LAW-001",
        law_number="58",
        year=1937,
        name_ar="قانون العقوبات",
        name_en="Penal Code",
        area="criminal",
        slug="penal-code",
        primary_url="https://www.eastlaws.com/data/laws/details/261",
        fallback_url="https://manshurat.org/node/14675",
        gazette_issue="71",
        gazette_date="1937-08-05",
        notes="Eastlaws confirmed Tier-1. 395 articles. Check if PDF export available.",
    ),
    LawSource(
        id="LAW-002",
        law_number="131",
        year=1948,
        name_ar="القانون المدني",
        name_en="Civil Code",
        area="civil",
        slug="civil-code",
        primary_url="https://www.eastlaws.com/data/laws/details/199",
        fallback_url="https://manshurat.org/node/14603",
        gazette_issue="108 مكرر",
        gazette_date="1948-07-29",
        notes="Eastlaws confirmed Tier-1. 1149 articles. Core civil law.",
    ),
    LawSource(
        id="LAW-003",
        law_number="159",
        year=1981,
        name_ar="قانون الشركات",
        name_en="Companies Law",
        area="commercial",
        slug="companies-law",
        primary_url="https://www.eastlaws.com/data/laws/details/351",
        fallback_url="https://manshurat.org/node/14805",
        gazette_issue="",
        gazette_date="1981-01-01",
        notes="NOT YET fully Tier-1 confirmed on eastlaws -- verify URL before trusting.",
    ),
    LawSource(
        id="LAW-004",
        law_number="181",
        year=2018,
        name_ar="قانون حماية المستهلك",
        name_en="Consumer Protection Law",
        area="consumer",
        slug="consumer-protection",
        primary_url="https://www.eastlaws.com/data/laws/details/1009",
        fallback_url="https://manshurat.org/node/56893",
        gazette_issue="",
        gazette_date="2018-07-04",
        notes="76 articles. Consumer rights: 14-day return, 2-year warranty etc.",
    ),
    LawSource(
        id="LAW-005",
        law_number="14",
        year=2025,
        name_ar="قانون العمل",
        name_en="Labor Law",
        area="labor",
        slug="labor-law-2025",
        # Ministry of Labour official legislation page
        primary_url="https://www.manpower.gov.eg/ar-EG/Legislation/Pages/Legislation.aspx",
        # Eastlaws secondary (newest law, may not be indexed yet)
        fallback_url="https://ar.wikisource.org/wiki/قانون_العمل_المصري_رقم_14_لسنة_2025",
        gazette_issue="18",
        gazette_date="2025-05-03",
        notes=(
            "298 articles. Replaces Law 12/2003. Effective Sept 1 2025. "
            "Published Official Gazette issue 18 dated 3/5/2025. "
            "Verify direct PDF download URL from manpower.gov.eg before ingesting."
        ),
    ),
    LawSource(
        id="LAW-006",
        law_number="17",
        year=1999,
        name_ar="قانون التجارة",
        name_en="Commercial Code",
        area="commercial",
        slug="commercial-code",
        primary_url="https://www.eastlaws.com/data/laws/details/468",
        fallback_url="https://manshurat.org/node/14735",
        gazette_issue="",
        gazette_date="1999-05-17",
        notes="772 articles. Commercial obligations, contracts, securities, bankruptcy.",
    ),
    LawSource(
        id="LAW-007",
        law_number="95",
        year=1992,
        name_ar="قانون سوق المال",
        name_en="Capital Markets Law",
        area="financial",
        slug="capital-markets-law",
        primary_url="https://www.fra.gov.eg/content/fra/ar/Legislation/Legist2.html",
        fallback_url="https://www.eastlaws.com/data/laws/details/404",
        gazette_issue="",
        gazette_date="1992-06-22",
        notes="FRA (Financial Regulatory Authority) official source. Regulates capital markets, securities.",
    ),
]


# ---------------------------------------------------------------------------
# Court of Cassation -- judicial decisions (Tier 3)
# These are not laws but judicial principles; they go into a separate
# data/raw/cassation/ tree and feed the judgments table, not the articles table.
# ---------------------------------------------------------------------------

CASSATION_SEARCH_BASE = "https://www.cc.gov.eg/judgments/search"
CASSATION_AREAS = [
    "civil",        # أحكام مدنية
    "commercial",   # أحكام تجارية
    "labor",        # أحكام عمالية
    "criminal",     # أحكام جنائية
]


def compute_sha256(file_path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def get_headers() -> dict:
    """Minimal browser-like headers to avoid trivial bot detection."""
    return {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "ar,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/pdf,*/*",
    }


def try_download_pdf(url: str, dest_path: Path, timeout: int = 60) -> bool:
    """
    Attempt to download a PDF from `url` to `dest_path`.
    Returns True on success, False if the response isn't a PDF or download fails.
    Note: many Egyptian legal sites serve HTML pages rather than raw PDFs.
    If this returns False, you'll need to manually download the PDF and use
    ingest_documents.py --local-file instead.
    """
    try:
        response = requests.get(url, headers=get_headers(), stream=True, timeout=timeout)
        response.raise_for_status()

        content_type = response.headers.get("content-type", "")
        is_pdf = "pdf" in content_type.lower() or url.lower().endswith(".pdf")

        if not is_pdf:
            # Check magic bytes
            first_bytes = b""
            for chunk in response.iter_content(chunk_size=5):
                first_bytes = chunk
                break
            if not first_bytes.startswith(b"%PDF"):
                return False  # Not a PDF -- HTML page, needs manual extraction

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        # Re-fetch properly (we consumed some of the stream)
        response2 = requests.get(url, headers=get_headers(), stream=True, timeout=timeout)
        response2.raise_for_status()
        with dest_path.open("wb") as f:
            for chunk in response2.iter_content(chunk_size=256 * 1024):
                if chunk:
                    f.write(chunk)
        return True

    except requests.RequestException:
        return False


def write_metadata(law_dir: Path, law: LawSource, sha256: str, status: str) -> None:
    metadata = {
        "law_id": law.id,
        "law_number": law.law_number,
        "year": law.year,
        "name_ar": law.name_ar,
        "name_en": law.name_en,
        "area": law.area,
        "source": urlparse(law.primary_url).netloc,
        "source_url": law.primary_url,
        "fallback_url": law.fallback_url,
        "gazette_issue": law.gazette_issue,
        "gazette_date": law.gazette_date,
        "tier": law.tier,
        "download_date": datetime.now(timezone.utc).isoformat(),
        "sha256": sha256,
        "status": status,
        "notes": law.notes,
    }
    law_dir.mkdir(parents=True, exist_ok=True)
    (law_dir / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def ingest_one(law: LawSource, data_raw_root: Path, dry_run: bool = False) -> str:
    """
    Try to ingest one law. Returns one of: 'downloaded', 'manual_needed', 'skipped', 'failed'.
    """
    law_dir = data_raw_root / law.area / law.slug
    dest_pdf = law_dir / "original.pdf"

    if dest_pdf.exists():
        print(f"  [{law.id}] Already exists at {dest_pdf} -- skipping.")
        return "skipped"

    if dry_run:
        print(f"  [{law.id}] DRY RUN: would fetch {law.primary_url}")
        print(f"           Fallback: {law.fallback_url}")
        return "dry_run"

    print(f"  [{law.id}] {law.name_ar} ({law.law_number}/{law.year})")
    print(f"           Trying {law.primary_url} ...")

    success = try_download_pdf(law.primary_url, dest_pdf)
    if not success and law.fallback_url:
        print(f"           Primary not a direct PDF. Trying fallback: {law.fallback_url} ...")
        time.sleep(1)
        success = try_download_pdf(law.fallback_url, dest_pdf)

    if success:
        sha256 = compute_sha256(dest_pdf)
        write_metadata(law_dir, law, sha256, "downloaded")
        print(f"           ✓ Downloaded ({dest_pdf.stat().st_size // 1024} KB) sha256: {sha256[:16]}...")
        return "downloaded"
    else:
        # Write a metadata.json documenting that manual download is needed
        write_metadata(law_dir, law, "", "manual_needed")
        print(
            f"           ✗ Could not auto-download (site likely serves HTML, not raw PDF).\n"
            f"             Manual step: download the PDF yourself and run:\n"
            f"               python scripts/ingest_documents.py \\\n"
            f"                 --local-file <path/to/downloaded.pdf> \\\n"
            f"                 --law-number {law.law_number} --year {law.year} \\\n"
            f"                 --area {law.area} --law-slug {law.slug} \\\n"
            f"                 --name \"{law.name_ar}\" \\\n"
            f"                 --provenance-url {law.primary_url}"
        )
        return "manual_needed"


def print_next_steps(results: dict) -> None:
    manual = [lid for lid, status in results.items() if status == "manual_needed"]
    downloaded = [lid for lid, status in results.items() if status == "downloaded"]
    skipped = [lid for lid, status in results.items() if status == "skipped"]

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Downloaded automatically : {len(downloaded)}")
    print(f"  Need manual download     : {len(manual)}")
    print(f"  Already existed (skipped): {len(skipped)}")

    if manual:
        print("\nLaws needing manual download:")
        for law in LAW_SOURCES:
            if law.id in manual:
                print(f"  {law.id}: {law.name_ar}")
                print(f"    URL: {law.primary_url}")
                if law.notes:
                    print(f"    Note: {law.notes}")

    if downloaded or skipped:
        print("\nNext steps (run in order):")
        print("  1. python scripts/extract_text.py     # extract text from PDFs")
        print("  2. python scripts/normalize_arabic.py # normalize Arabic text")
        print("  3. python scripts/split_articles.py   # split into article chunks")
        print("  4. python scripts/create_embeddings.py # create vector embeddings")
        print("\nFor Court of Cassation judicial decisions, run:")
        print("  python scripts/fetch_cassation.py     # scrape judicial decisions")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download Egyptian law source documents from confirmed Tier-1 sources."
    )
    parser.add_argument(
        "--law-id",
        help="Ingest only this law ID (e.g. LAW-005). Omit to ingest all.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be fetched without downloading anything.",
    )
    parser.add_argument(
        "--data-raw-root",
        type=Path,
        default=DATA_RAW_ROOT,
        help=f"Root directory for raw ingested documents (default: {DATA_RAW_ROOT}).",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all registered law sources and exit.",
    )
    return parser


def main(argv: Optional[list] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.list:
        print(f"{'ID':<10} {'Number/Year':<15} {'Area':<12} {'Name'}")
        print("-" * 70)
        for law in LAW_SOURCES:
            print(f"{law.id:<10} {law.law_number}/{law.year:<10}  {law.area:<12} {law.name_ar}")
        return 0

    # Filter by --law-id if given
    sources_to_run = LAW_SOURCES
    if args.law_id:
        sources_to_run = [s for s in LAW_SOURCES if s.id == args.law_id]
        if not sources_to_run:
            valid_ids = [s.id for s in LAW_SOURCES]
            print(f"ERROR: unknown law ID {args.law_id!r}. Valid IDs: {valid_ids}", file=sys.stderr)
            return 1

    if args.dry_run:
        print("DRY RUN -- nothing will be downloaded.\n")

    print(f"Fetching {len(sources_to_run)} law source(s) into {args.data_raw_root}/...\n")

    results = {}
    for law in sources_to_run:
        result = ingest_one(law, data_raw_root=args.data_raw_root, dry_run=args.dry_run)
        results[law.id] = result
        time.sleep(0.5)  # polite delay between requests

    if not args.dry_run:
        print_next_steps(results)

    failures = [lid for lid, status in results.items() if status == "failed"]
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
