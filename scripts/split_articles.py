#!/usr/bin/env python3
"""
Split a normalized Egyptian law text into individual articles.

REAL, regex-based implementation -- genuinely runnable today against sample
Arabic text (see the embedded smoke test in `if __name__ == "__main__"`
below, which splits ~3 fake articles correctly). It does not depend on any
missing source data; it only needs *some* normalized law text, which is
exactly what scripts/normalize_arabic.py produces.

Input is expected to already be run through normalize_arabic.py (so digits
are ASCII, alef forms are unified, whitespace is collapsed) -- this script
does not re-normalize.

Output: a JSON list of {"article_number": str, "text": str} objects, in
document order.

Usage:
    python scripts/split_articles.py --input-file data/processed/.../normalized.txt \\
        --output-file data/processed/.../articles.json
    python scripts/split_articles.py --text "مادة 1 ... مادة 2 ..."
    python scripts/split_articles.py   # runs the embedded smoke test
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List, Optional, TypedDict

# --- The article-boundary regex -----------------------------------------
#
# Egyptian law texts mark article boundaries in several observed styles:
#   "مادة 1"            -- bare number after the word
#   "المادة (1)"        -- parenthesized number, definite article
#   "مادة رقم 1"        -- "number" spelled out before the digit
#   "مادة (1) مكرر"     -- "مكرر" (bis/repeated) suffix for inserted articles,
#                          e.g. "مادة 5 مكرر" after an amendment
#   "المادة الأولى"     -- spelled-out ordinal instead of a digit (rare, seen
#                          in some older gazette texts) -- NOT matched by
#                          this regex; see "Known limitations" below.
#
# The regex requires the marker to start at a line boundary (^ with
# re.MULTILINE) to avoid false-positives on the word "مادة" appearing mid-
# sentence (e.g. "طبقاً للمادة السابقة ..." referencing another article).
# Input is expected to already be normalize_arabic.py-processed, so digits
# are ASCII and alef forms are unified -- this regex assumes that.
ARTICLE_MARKER_RE = re.compile(
    r"""
    ^\s*
    (?:ال)?مادة              # "مادة" or "المادة"
    \s*
    (?:رقم\s*)?               # optional "رقم"
    \(?\s*(\d+)\s*\)?          # the article number, optionally parenthesized
    \s*
    (مكرر(?:\s*\d*)?)?        # optional "مكرر" (bis) suffix, itself
                               # optionally numbered ("مكرر 1", "مكرر 2")
    """,
    re.MULTILINE | re.VERBOSE,
)


class Article(TypedDict):
    article_number: str
    text: str


def split_law_into_articles(text: str) -> List[Article]:
    """
    Split `text` (already normalized) into a list of {article_number, text}
    dicts, in document order. Text before the first marker (e.g. a law's
    title/preamble block) is discarded from the article list -- callers who
    need the preamble should slice it out of `text` before calling this.
    """
    matches = list(ARTICLE_MARKER_RE.finditer(text))
    articles: List[Article] = []

    for i, m in enumerate(matches):
        number = m.group(1)
        suffix = (m.group(2) or "").strip()
        article_number = f"{number} {suffix}".strip() if suffix else number

        body_start = m.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[body_start:body_end].strip()

        articles.append(Article(article_number=article_number, text=body))

    return articles


# --- Known limitations (read before trusting output on a new source) ----
#
# This regex will MISS an article when:
#   1. The article number is spelled out as an ordinal word instead of a
#      digit ("المادة الأولى" / "الثانية" / ...) -- seen in some older or
#      hand-transcribed texts. Fix: add an ordinal-word -> number lookup
#      table and a second alternation branch, once a real source using this
#      style is found in data/raw/.
#   2. OCR has corrupted the word "مادة" itself (e.g. "ماده" without ة, or a
#      stray space/line-break inside the word from column-justified PDF
#      text). Fix: run scripts/normalize_arabic.py's OCR-artifact cleanup
#      (not yet built -- see backend/app/ingestion/normalize_arabic.py's
#      TODO) before this step, or widen the regex to tolerate a couple of
#      edit-distance-1 misspellings.
#   3. The source uses a completely different structural word ("فصل" alone
#      without articles, for texts organized by section rather than
#      numbered article -- rare in primary legislation but seen in some
#      executive regulations).
#
# What to do when it misses an article: don't silently accept a shorter
# article list than the source table of contents implies. Compare
# len(split_law_into_articles(...)) against the law's known article count
# (many gazette PDFs state "عدد مواد القانون" or a table of contents up
# front) and flag a mismatch for manual review rather than proceeding.


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Split normalized Egyptian law text into a JSON list of articles."
    )
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--text", help="Split a literal string given on the command line.")
    src.add_argument(
        "--input-file", type=Path, help="Path to a normalized UTF-8 text file to split."
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        help="Write the JSON article list here. If omitted, prints to stdout.",
    )
    parser.add_argument(
        "--expected-count",
        type=int,
        default=None,
        help="If given, warn (non-fatal) when the number of split articles doesn't match.",
    )
    return parser


def main(argv: Optional[list] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.input_file is not None:
        if not args.input_file.exists():
            parser.error(f"--input-file does not exist: {args.input_file}")
        text = args.input_file.read_text(encoding="utf-8")
    else:
        text = args.text

    articles = split_law_into_articles(text)

    if not articles:
        print(
            "WARNING: no article markers found. Check that the input has already "
            "been through scripts/normalize_arabic.py, and see the 'Known "
            "limitations' comment in this script for why a marker style might "
            "be missed.",
            file=sys.stderr,
        )

    if args.expected_count is not None and len(articles) != args.expected_count:
        print(
            f"WARNING: expected {args.expected_count} articles, found {len(articles)}. "
            "Flag for manual review rather than trusting this output as-is.",
            file=sys.stderr,
        )

    output = json.dumps(articles, ensure_ascii=False, indent=2)
    if args.output_file:
        args.output_file.parent.mkdir(parents=True, exist_ok=True)
        args.output_file.write_text(output, encoding="utf-8")
        print(f"Wrote {len(articles)} articles to {args.output_file}")
    else:
        print(output)

    return 0


def _run_smoke_test() -> None:
    """Embedded smoke test: a small fake 3-article law text, styled after
    the marker variants documented above, verified to split correctly."""
    sample_law_text = """
قانون تجريبي رقم 99 لسنة 2026

مادة 1
يُقصد بالمصطلحات التالية في تطبيق أحكام هذا القانون المعاني الموضحة قرين كل منها.

المادة (2)
يُحظر على كل شخص القيام بأي فعل يخالف أحكام هذا القانون.

مادة رقم 3 مكرر
تُطبق العقوبات المنصوص عليها في المادة السابقة على كل من يخالف هذا الحكم.
""".strip()

    result = split_law_into_articles(sample_law_text)
    assert len(result) == 3, f"expected 3 articles, got {len(result)}: {result}"

    assert result[0]["article_number"] == "1"
    assert "يُقصد بالمصطلحات" in result[0]["text"]

    assert result[1]["article_number"] == "2"
    assert "يُحظر على كل شخص" in result[1]["text"]

    assert result[2]["article_number"] == "3 مكرر"
    assert "تُطبق العقوبات" in result[2]["text"]
    # The reference to "المادة السابقة" (the previous article) inside
    # article 3's own body must NOT have been treated as a new boundary.
    assert result[2]["text"].count("تُطبق العقوبات") == 1

    print("split_articles.py: smoke test passed -- split 3/3 fake articles correctly.")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if len(sys.argv) == 1:
        _run_smoke_test()
        sys.exit(0)
    sys.exit(main())
