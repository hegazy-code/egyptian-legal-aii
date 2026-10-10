#!/usr/bin/env python3
"""
OCR fallback for scanned/image-only Egyptian legal PDFs.

REAL, working implementation using pytesseract + pdf2image (Tesseract is
free/open-source, so this needs no paid API). It is functionally complete
but UNTESTED against a real scanned Egyptian legal PDF, because none exist
in this repo yet (see scripts/extract_text.py's TODO -- this script is what
extract_text.py's `likely_scanned: true` flag routes to).

System dependencies (not pip-installable -- install via your OS package
manager before running this script):
    apt install tesseract-ocr tesseract-ocr-ara poppler-utils

  - tesseract-ocr        the OCR engine itself
  - tesseract-ocr-ara     the Arabic language pack (required -- default
                           Tesseract install is English-only)
  - poppler-utils         provides `pdftoppm`, which pdf2image shells out to
                           for rendering PDF pages to images

Output layout mirrors data/raw/ into data/ocr/ (parallel to how
extract_text.py mirrors data/raw/ into data/processed/):
    data/raw/<area>/<law_slug>/original.pdf
      -> data/ocr/<area>/<law_slug>/text.txt
      -> data/ocr/<area>/<law_slug>/quality.json

quality.json schema: {page_count, char_count, avg_confidence, per_page_confidence,
low_confidence_pages}. Pages below --min-confidence are listed in
low_confidence_pages for manual review (see docs/legal-source-policy.md's
OCR_REVIEW_REQUIRED status).

Usage:
    python scripts/run_ocr.py --input-file data/raw/criminal/penal-code/original.pdf
    python scripts/run_ocr.py --input-file data/raw/civil/civil-code/original.pdf \\
        --lang ara --dpi 300 --min-confidence 60
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import List, Optional

DATA_RAW_ROOT = Path("data/raw")
DATA_OCR_ROOT = Path("data/ocr")

DEFAULT_LANG = "ara"
DEFAULT_DPI = 300
DEFAULT_MIN_CONFIDENCE = 60.0


def check_system_dependencies() -> Optional[str]:
    """
    Return an error message if a required system binary is missing, else None.
    Checked explicitly (rather than letting pdf2image/pytesseract raise deep
    inside a stack trace) so the failure is a clear, actionable message.
    """
    missing = []
    if shutil.which("pdftoppm") is None:
        missing.append("pdftoppm (from poppler-utils)")
    if shutil.which("tesseract") is None:
        missing.append("tesseract (from tesseract-ocr)")

    if missing:
        return (
            "Missing required system dependenc"
            + ("y" if len(missing) == 1 else "ies")
            + f": {', '.join(missing)}.\n"
            "Install with: apt install tesseract-ocr tesseract-ocr-ara poppler-utils"
        )
    return None


def check_tesseract_language(lang: str) -> Optional[str]:
    """Return an error message if the requested Tesseract language pack isn't
    installed, else None."""
    import pytesseract

    try:
        available = pytesseract.get_languages(config="")
    except Exception as exc:  # noqa: BLE001
        return f"Could not query installed Tesseract languages: {exc}"

    if lang not in available:
        return (
            f"Tesseract language pack '{lang}' is not installed "
            f"(available: {', '.join(available)}). "
            f"Install with: apt install tesseract-ocr-{lang}"
        )
    return None


def ocr_pdf(
    pdf_path: Path,
    lang: str = DEFAULT_LANG,
    dpi: int = DEFAULT_DPI,
    min_confidence: float = DEFAULT_MIN_CONFIDENCE,
) -> dict:
    """
    Render each page of `pdf_path` to an image and OCR it with Tesseract.
    Returns {text, page_count, char_count, avg_confidence, per_page_confidence,
    low_confidence_pages}.

    Requires the tesseract and pdftoppm system binaries plus the requested
    Tesseract language pack to be installed -- see module docstring.
    """
    from pdf2image import convert_from_path
    import pytesseract

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    images = convert_from_path(str(pdf_path), dpi=dpi)

    page_texts: List[str] = []
    per_page_confidence: List[float] = []

    for image in images:
        # image_to_data gives per-word confidence; average the positive
        # (non -1, i.e. actually-recognized) confidences for this page.
        data = pytesseract.image_to_data(
            image, lang=lang, output_type=pytesseract.Output.DICT
        )
        confidences = [float(c) for c in data.get("conf", []) if str(c) not in ("-1", "")]
        page_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        per_page_confidence.append(round(page_confidence, 1))

        page_text = pytesseract.image_to_string(image, lang=lang)
        page_texts.append(page_text)

    full_text = "\n\n".join(page_texts)
    avg_confidence = (
        round(sum(per_page_confidence) / len(per_page_confidence), 1)
        if per_page_confidence
        else 0.0
    )
    low_confidence_pages = [
        i + 1 for i, c in enumerate(per_page_confidence) if c < min_confidence
    ]

    return {
        "text": full_text,
        "page_count": len(images),
        "char_count": len(full_text.strip()),
        "avg_confidence": avg_confidence,
        "per_page_confidence": per_page_confidence,
        "low_confidence_pages": low_confidence_pages,
    }


def processed_path_for(raw_path: Path, raw_root: Path, ocr_root: Path) -> Path:
    """Mirror a data/raw/... path into the equivalent data/ocr/... directory."""
    try:
        relative = raw_path.relative_to(raw_root)
    except ValueError:
        relative = Path(raw_path.stem)
    relative_dir = relative.parent if relative.parent != Path(".") else Path(raw_path.stem)
    return ocr_root / relative_dir


def process_document(
    pdf_path: Path,
    raw_root: Path = DATA_RAW_ROOT,
    ocr_root: Path = DATA_OCR_ROOT,
    lang: str = DEFAULT_LANG,
    dpi: int = DEFAULT_DPI,
    min_confidence: float = DEFAULT_MIN_CONFIDENCE,
) -> Path:
    """Run OCR on pdf_path and write text.txt + quality.json into the
    mirrored data/ocr/ directory. Returns that directory."""
    result = ocr_pdf(pdf_path, lang=lang, dpi=dpi, min_confidence=min_confidence)

    out_dir = processed_path_for(pdf_path, raw_root, ocr_root)
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "text.txt").write_text(result["text"], encoding="utf-8")
    quality = {k: v for k, v in result.items() if k != "text"}
    (out_dir / "quality.json").write_text(
        json.dumps(quality, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(
        f"OCR'd {result['page_count']} page(s), {result['char_count']} chars, "
        f"avg confidence {result['avg_confidence']} -> {out_dir}"
    )
    if result["low_confidence_pages"]:
        print(
            f"LOW CONFIDENCE pages needing manual review "
            f"(OCR_REVIEW_REQUIRED per docs/legal-source-policy.md): "
            f"{result['low_confidence_pages']}",
            file=sys.stderr,
        )

    return out_dir


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "OCR a scanned/image-only PDF with Tesseract (Arabic language pack). "
            "Requires system dependencies -- see module docstring for the apt install line."
        )
    )
    parser.add_argument("--input-file", required=True, type=Path, help="Path to the source PDF.")
    parser.add_argument("--raw-root", type=Path, default=DATA_RAW_ROOT)
    parser.add_argument("--ocr-root", type=Path, default=DATA_OCR_ROOT)
    parser.add_argument(
        "--lang", default=DEFAULT_LANG, help=f"Tesseract language code (default: {DEFAULT_LANG})."
    )
    parser.add_argument(
        "--dpi", type=int, default=DEFAULT_DPI, help=f"Render DPI (default: {DEFAULT_DPI})."
    )
    parser.add_argument(
        "--min-confidence",
        type=float,
        default=DEFAULT_MIN_CONFIDENCE,
        help=f"Pages below this avg word confidence are flagged for manual "
        f"review (default: {DEFAULT_MIN_CONFIDENCE}).",
    )
    return parser


def main(argv: Optional[list] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    dep_error = check_system_dependencies()
    if dep_error:
        print(f"ERROR: {dep_error}", file=sys.stderr)
        return 1

    if not args.input_file.exists():
        print(
            f"ERROR: {args.input_file} does not exist.\n"
            f"# TODO: needs real source documents in data/raw/ first -- run "
            f"scripts/ingest_documents.py to populate data/raw/, then "
            f"scripts/extract_text.py to check whether OCR is even needed.",
            file=sys.stderr,
        )
        return 1

    lang_error = check_tesseract_language(args.lang)
    if lang_error:
        print(f"ERROR: {lang_error}", file=sys.stderr)
        return 1

    try:
        process_document(
            args.input_file,
            raw_root=args.raw_root,
            ocr_root=args.ocr_root,
            lang=args.lang,
            dpi=args.dpi,
            min_confidence=args.min_confidence,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: OCR failed: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
