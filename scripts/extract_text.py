#!/usr/bin/env python3
"""
Extract text from a PDF in data/raw/ and write it (plus a quality-signal
JSON) to the matching data/processed/ path.

Tries direct text extraction first (pypdf, falling back to pdfplumber if
pypdf gets nothing useful), since that's fast and exact for born-digital
PDFs. If the extracted text is suspiciously short relative to the page
count, flags the document as likely scanned/image-only and needing OCR
(scripts/run_ocr.py) instead of failing silently.

Output layout mirrors input layout:
    data/raw/<area>/<law_slug>/original.pdf
      -> data/processed/<area>/<law_slug>/text.txt
      -> data/processed/<area>/<law_slug>/quality.json

quality.json schema: {char_count, page_count, chars_per_page, likely_scanned,
extraction_method}.

# TODO: needs real source documents in data/raw/ first -- there is no PDF
# checked into this repo yet (see README: "4 flagship laws registered ...
# not yet article-level text"). The extraction logic below is real and will
# run correctly the moment scripts/ingest_documents.py has populated
# data/raw/ with an actual gazette/legislation PDF.

Usage:
    python scripts/extract_text.py --input-file data/raw/criminal/penal-code/original.pdf
    python scripts/extract_text.py --input-file data/raw/civil/civil-code/original.pdf \\
        --min-chars-per-page 200
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Tuple

DATA_RAW_ROOT = Path("data/raw")
DATA_PROCESSED_ROOT = Path("data/processed")

# Heuristic threshold: a genuine legal-text page (Arabic, gazette-format)
# reliably has several hundred characters of body text. Well below this
# on average across the document strongly suggests a scanned/image-only
# PDF where direct extraction is only picking up stray layer artifacts
# (headers, page numbers) rather than the article text itself.
DEFAULT_MIN_CHARS_PER_PAGE = 150


def extract_with_pypdf(pdf_path: Path) -> Tuple[str, int]:
    """Try direct text extraction with pypdf. Returns (text, page_count)."""
    from pypdf import PdfReader

    reader = PdfReader(str(pdf_path))
    page_count = len(reader.pages)
    text_parts = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(text_parts), page_count


def extract_with_pdfplumber(pdf_path: Path) -> Tuple[str, int]:
    """Fallback direct extraction with pdfplumber (handles some layouts
    pypdf misses, e.g. certain column layouts)."""
    import pdfplumber

    with pdfplumber.open(str(pdf_path)) as pdf:
        page_count = len(pdf.pages)
        text_parts = [page.extract_text() or "" for page in pdf.pages]
    return "\n\n".join(text_parts), page_count


def extract_text_from_pdf(
    pdf_path: Path, min_chars_per_page: int = DEFAULT_MIN_CHARS_PER_PAGE
) -> dict:
    """
    Extract text from `pdf_path`, trying pypdf first and pdfplumber as a
    fallback if pypdf yields nothing. Returns a dict:
        {text, page_count, char_count, chars_per_page, likely_scanned,
         extraction_method}
    Does not write anything to disk -- see main()/process_document() for that.
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    text = ""
    page_count = 0
    method = "none"

    try:
        text, page_count = extract_with_pypdf(pdf_path)
        method = "pypdf"
    except Exception as exc:  # noqa: BLE001
        print(f"pypdf extraction failed ({exc}); trying pdfplumber...", file=sys.stderr)

    if not text.strip():
        try:
            text, page_count = extract_with_pdfplumber(pdf_path)
            method = "pdfplumber"
        except Exception as exc:  # noqa: BLE001
            print(f"pdfplumber extraction also failed ({exc}).", file=sys.stderr)
            method = "failed"

    char_count = len(text.strip())
    chars_per_page = (char_count / page_count) if page_count else 0.0
    # Zero-page or zero-char documents are trivially "likely scanned" (there
    # was nothing to extract at all).
    likely_scanned = page_count == 0 or chars_per_page < min_chars_per_page

    return {
        "text": text,
        "page_count": page_count,
        "char_count": char_count,
        "chars_per_page": round(chars_per_page, 1),
        "likely_scanned": likely_scanned,
        "extraction_method": method,
    }


def processed_path_for(raw_path: Path, raw_root: Path, processed_root: Path) -> Path:
    """Mirror a data/raw/... path into the equivalent data/processed/... directory."""
    try:
        relative = raw_path.relative_to(raw_root)
    except ValueError:
        # Input wasn't under data/raw/ -- still mirror by filename-derived dir.
        relative = Path(raw_path.stem)
    # Drop the filename (e.g. original.pdf), keep the <area>/<law_slug> dirs.
    relative_dir = relative.parent if relative.parent != Path(".") else Path(raw_path.stem)
    return processed_root / relative_dir


def process_document(
    pdf_path: Path,
    raw_root: Path = DATA_RAW_ROOT,
    processed_root: Path = DATA_PROCESSED_ROOT,
    min_chars_per_page: int = DEFAULT_MIN_CHARS_PER_PAGE,
) -> Path:
    """Extract text from pdf_path and write text.txt + quality.json into the
    mirrored data/processed/ directory. Returns that directory."""
    result = extract_text_from_pdf(pdf_path, min_chars_per_page=min_chars_per_page)

    out_dir = processed_path_for(pdf_path, raw_root, processed_root)
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "text.txt").write_text(result["text"], encoding="utf-8")

    quality = {k: v for k, v in result.items() if k != "text"}
    (out_dir / "quality.json").write_text(
        json.dumps(quality, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"Extracted {result['char_count']} chars from {result['page_count']} page(s) "
          f"via {result['extraction_method']} -> {out_dir}")
    if result["likely_scanned"]:
        print(
            "FLAGGED as likely_scanned=True -- text yield is low relative to page count. "
            "Run scripts/run_ocr.py on this document instead of trusting this extraction.",
            file=sys.stderr,
        )

    return out_dir


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Extract text from a PDF in data/raw/, writing text.txt + quality.json "
            "into the mirrored data/processed/ directory. Flags likely-scanned PDFs "
            "for the OCR fallback (scripts/run_ocr.py) instead of silently returning "
            "near-empty text."
        )
    )
    parser.add_argument("--input-file", required=True, type=Path, help="Path to the source PDF.")
    parser.add_argument("--raw-root", type=Path, default=DATA_RAW_ROOT)
    parser.add_argument("--processed-root", type=Path, default=DATA_PROCESSED_ROOT)
    parser.add_argument(
        "--min-chars-per-page",
        type=int,
        default=DEFAULT_MIN_CHARS_PER_PAGE,
        help=f"Below this average chars/page, flag likely_scanned=True (default: "
        f"{DEFAULT_MIN_CHARS_PER_PAGE}).",
    )
    return parser


def main(argv: Optional[list] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if not args.input_file.exists():
        print(
            f"ERROR: {args.input_file} does not exist.\n"
            f"# TODO: needs real source documents in data/raw/ first -- run "
            f"scripts/ingest_documents.py to populate data/raw/ before extracting.",
            file=sys.stderr,
        )
        return 1

    try:
        process_document(
            args.input_file,
            raw_root=args.raw_root,
            processed_root=args.processed_root,
            min_chars_per_page=args.min_chars_per_page,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: text extraction failed: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
