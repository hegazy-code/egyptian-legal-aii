#!/usr/bin/env python3
"""
Ingest one source law document (download or local copy) into data/raw/.

Given a URL or local file path plus registry metadata for that document,
this script:
  1. Fetches the file (HTTP download, or a local filesystem copy).
  2. Computes its sha256.
  3. Writes it to data/raw/<area>/<law_slug>/original.<ext>
  4. Writes a metadata.json alongside it with the schema:
     {law_number, year, name, source, source_url, download_date, sha256, status}

This is REAL download/hashing/write logic, not a stub -- it will work
correctly today against a real URL or local file. What it explicitly does
NOT do is figure out *which* URL to ingest for a given law, or what
area/law_slug that URL belongs to -- those come in as CLI arguments,
sourced by a human from data/inventory/legal_sources.xlsx (see
scripts/validate_sources.py for what's registered and what still needs
Tier-1 confirmation before being trusted as an ingest source).

# TODO: needs real source documents in data/raw/ first -- this script is
# ready to run the moment a Tier-1-confirmed URL or file exists for one of
# the 4 registered laws (see docs/legal-source-policy.md); until then there
# is nothing safe to ingest, since ingesting an unconfirmed secondary-source
# copy would violate the no-hallucination / verified-source policy this
# whole project is built around.

Usage:
    python scripts/ingest_documents.py \\
        --source-url https://www.eastlaws.com/legislation-full-text/... \\
        --law-number 58 --year 1937 --area criminal \\
        --law-slug penal-code --name "قانون العقوبات"

    python scripts/ingest_documents.py \\
        --local-file /path/to/downloaded.pdf \\
        --law-number 131 --year 1948 --area civil \\
        --law-slug civil-code --name "القانون المدني" \\
        --source-url https://www.eastlaws.com/...
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None  # only required for the --source-url path; checked at call time

DATA_RAW_ROOT = Path("data/raw")

VALID_STATUSES = {"downloaded", "verified", "failed"}


def compute_sha256(file_path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Stream-hash a file so large PDFs don't need to fit in memory at once."""
    digest = hashlib.sha256()
    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def guess_extension(source_url: Optional[str], local_file: Optional[Path]) -> str:
    """Best-effort extension guess from a URL path or local file, defaulting to .pdf
    (the overwhelmingly common format for gazette/legislation text)."""
    if local_file is not None and local_file.suffix:
        return local_file.suffix.lstrip(".")
    if source_url:
        path = urlparse(source_url).path
        suffix = Path(path).suffix
        if suffix:
            return suffix.lstrip(".")
    return "pdf"


def download_file(source_url: str, dest_path: Path, timeout: int = 60) -> None:
    """Download `source_url` to `dest_path`, streaming to disk."""
    if requests is None:
        raise RuntimeError(
            "The 'requests' package is required for URL downloads. "
            "Install it: pip install -r scripts/requirements.txt"
        )
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(source_url, stream=True, timeout=timeout) as response:
        response.raise_for_status()
        with dest_path.open("wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 256):
                if chunk:
                    f.write(chunk)


def copy_local_file(local_file: Path, dest_path: Path) -> None:
    """Copy a local source file into the ingestion tree."""
    if not local_file.exists():
        raise FileNotFoundError(f"--local-file does not exist: {local_file}")
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(local_file, dest_path)


def build_metadata(
    law_number: str,
    year: int,
    name: str,
    source: str,
    source_url: Optional[str],
    sha256: str,
    status: str,
) -> dict:
    """Build the metadata.json record. Schema matches docs/legal-source-policy.md
    and README's ingestion contract:
    law_number, year, name, source, source_url, download_date, sha256, status."""
    if status not in VALID_STATUSES:
        raise ValueError(f"status must be one of {VALID_STATUSES}, got {status!r}")
    return {
        "law_number": law_number,
        "year": year,
        "name": name,
        "source": source,
        "source_url": source_url,
        "download_date": datetime.now(timezone.utc).isoformat(),
        "sha256": sha256,
        "status": status,
    }


def ingest(
    area: str,
    law_slug: str,
    law_number: str,
    year: int,
    name: str,
    source: str,
    source_url: Optional[str] = None,
    local_file: Optional[Path] = None,
    data_raw_root: Path = DATA_RAW_ROOT,
) -> Path:
    """
    Run the full ingest: fetch (download or copy) + hash + write metadata.json.
    Returns the directory the document was written into.
    """
    if not source_url and not local_file:
        raise ValueError("Exactly one of source_url or local_file must be given.")

    ext = guess_extension(source_url, local_file)
    law_dir = data_raw_root / area / law_slug
    dest_path = law_dir / f"original.{ext}"

    status = "downloaded"
    try:
        if local_file is not None:
            copy_local_file(local_file, dest_path)
        else:
            download_file(source_url, dest_path)
    except Exception as exc:
        status = "failed"
        print(f"ERROR: ingestion failed for {law_slug}: {exc}", file=sys.stderr)
        # Still write a metadata.json documenting the failed attempt, without
        # a sha256 (nothing was successfully written to hash).
        law_dir.mkdir(parents=True, exist_ok=True)
        metadata = build_metadata(
            law_number=law_number,
            year=year,
            name=name,
            source=source,
            source_url=source_url,
            sha256="",
            status=status,
        )
        (law_dir / "metadata.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        raise

    sha256 = compute_sha256(dest_path)
    metadata = build_metadata(
        law_number=law_number,
        year=year,
        name=name,
        source=source,
        source_url=source_url,
        sha256=sha256,
        status=status,
    )
    (law_dir / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"Ingested -> {dest_path}")
    print(f"sha256: {sha256}")
    print(f"metadata -> {law_dir / 'metadata.json'}")
    return law_dir


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Download or copy a source law document into data/raw/<area>/<law_slug>/, "
            "computing its sha256 and writing metadata.json alongside it."
        )
    )
    fetch_src = parser.add_mutually_exclusive_group(required=True)
    fetch_src.add_argument("--source-url", help="URL to download the document from.")
    fetch_src.add_argument(
        "--local-file", type=Path, help="Path to an already-downloaded local file to ingest."
    )
    # If --local-file is used, --source-url can still be supplied separately
    # to record provenance (where the local copy originally came from).
    parser.add_argument(
        "--provenance-url",
        help="When using --local-file, the original URL the file came from (for metadata.json).",
    )

    parser.add_argument("--area", required=True, help="Legal area, e.g. 'criminal', 'civil'.")
    parser.add_argument(
        "--law-slug", required=True, help="Filesystem-safe slug for this law, e.g. 'penal-code'."
    )
    parser.add_argument("--law-number", required=True, help="Law number, e.g. '58'.")
    parser.add_argument("--year", required=True, type=int, help="Law year, e.g. 1937.")
    parser.add_argument("--name", required=True, help="Law name (Arabic and/or English).")
    parser.add_argument(
        "--source",
        default=None,
        help="Human-readable source label, e.g. 'eastlaws.com' or 'الوقائع المصرية'. "
        "Defaults to the domain of --source-url if not given.",
    )
    parser.add_argument(
        "--data-raw-root",
        type=Path,
        default=DATA_RAW_ROOT,
        help=f"Root directory for raw ingested documents (default: {DATA_RAW_ROOT}).",
    )
    return parser


def main(argv: Optional[list] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    source_url = args.source_url or args.provenance_url
    source_label = args.source or (
        urlparse(source_url).netloc if source_url else "local file (no provenance URL given)"
    )

    try:
        ingest(
            area=args.area,
            law_slug=args.law_slug,
            law_number=args.law_number,
            year=args.year,
            name=args.name,
            source=source_label,
            source_url=source_url,
            local_file=args.local_file,
            data_raw_root=args.data_raw_root,
        )
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001 - top-level CLI error boundary
        print(f"ERROR: ingestion failed: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
