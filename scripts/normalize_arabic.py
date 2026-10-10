#!/usr/bin/env python3
"""
Arabic text normalization for the offline ingestion pipeline.

This is REAL, fully working code -- no missing-data blocker. It never
mutates or discards the original text: every function returns a *new*
string, and the CLI entry point always keeps `original_text` untouched
alongside a separately-produced `normalized_text` field. That is a hard
rule from docs/legal-source-policy.md's data-quality section: normalization
is a derived, reviewable transform, not a destructive edit of the source.

Normalization steps (each individually toggleable, see build_normalizer()):
  1. Alef normalization      -- أ إ آ ٱ  ->  ا
  2. Alef maksura            -- ى  ->  ي   (configurable; OFF changes meaning
                                 in some words, so this is opt-in per call)
  3. Ta marbuta              -- ة  ->  ه   (configurable; legal text usually
                                 wants ة preserved, so this defaults to OFF)
  4. Diacritics / tashkeel   -- optional, OFF by default. Legal text
     diacritics can be load-bearing (e.g. disambiguating a verb form in a
     penal article), so stripping them is opt-in, never automatic.
  5. Arabic-Indic digit normalization (٠-٩ -> 0-9) -- always safe, always on.
  6. Whitespace collapsing   -- always on.

Usage:
    python scripts/normalize_arabic.py --text "النص هنا"
    python scripts/normalize_arabic.py --input-file data/processed/.../text.txt \\
        --output-file data/processed/.../normalized.json
    python scripts/normalize_arabic.py --input-file in.txt --strip-diacritics \\
        --unify-alef-maksura --unify-ta-marbuta

Doctest-style examples (run `python -m doctest scripts/normalize_arabic.py -v`
or just run this file directly -- the __main__ block below re-runs the same
assertions as a smoke test):

    >>> normalize_alef("أحمد إبراهيم آدم ٱلرحمن")
    'احمد ابراهيم ادم الرحمن'
    >>> normalize_alef_maksura("ذهب إلى المدرسة")
    'ذهب إلي المدرسة'
    >>> normalize_ta_marbuta("المحكمة الجزئية")
    'المحكمه الجزئيه'
    >>> strip_diacritics("الْقَانُونُ الْمَدَنِيّ")
    'القانون المدني'
    >>> normalize_digits("المادة ١٤١ لسنة ٢٠٢٤")
    'المادة 141 لسنة 2024'
    >>> collapse_whitespace("مادة    1  \\n\\n  نص المادة")
    'مادة 1 نص المادة'
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

# --- Individual, composable normalization steps -----------------------------

_DIACRITICS_RE = re.compile(
    r"[ً-ٟؐ-ؚۖ-ۜ۟-۪ۨ-ٰۭ]"
)
_ARABIC_INDIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
_ALEF_VARIANTS = ("أ", "إ", "آ", "ٱ")
_WHITESPACE_RE = re.compile(r"\s+")
_TATWEEL = "ـ"  # ـ kashida/elongation character, always safe to strip


def normalize_alef(text: str) -> str:
    """Collapse alef variants (أ إ آ ٱ) to bare alef (ا)."""
    if not text:
        return text
    for ch in _ALEF_VARIANTS:
        text = text.replace(ch, "ا")
    return text


def normalize_alef_maksura(text: str) -> str:
    """Convert alef maksura (ى) to ya (ي). Opt-in: changes some word shapes."""
    if not text:
        return text
    return text.replace("ى", "ي")


def normalize_ta_marbuta(text: str) -> str:
    """Convert ta marbuta (ة) to ha (ه). Opt-in: usually NOT wanted for legal
    text, where ة vs ه can matter, but offered for lenient-matching use cases
    (e.g. building a search index variant)."""
    if not text:
        return text
    return text.replace("ة", "ه")


def strip_diacritics(text: str) -> str:
    """Remove tashkeel (fatha, kasra, damma, sukun, shadda, tanwin, etc).
    Opt-in and OFF by default -- see module docstring."""
    if not text:
        return text
    return _DIACRITICS_RE.sub("", text)


def strip_tatweel(text: str) -> str:
    """Remove the kashida/tatweel elongation character. Always safe."""
    if not text:
        return text
    return text.replace(_TATWEEL, "")


def normalize_digits(text: str) -> str:
    """Convert Arabic-Indic digits (٠-٩) to ASCII digits (0-9)."""
    if not text:
        return text
    return text.translate(_ARABIC_INDIC_DIGITS)


def collapse_whitespace(text: str) -> str:
    """Collapse runs of whitespace (including newlines) into single spaces
    and trim the ends. Always applied last."""
    if not text:
        return text
    return _WHITESPACE_RE.sub(" ", text).strip()


@dataclass
class NormalizationOptions:
    strip_diacritics: bool = False
    unify_alef_maksura: bool = False
    unify_ta_marbuta: bool = False


def normalize_text(text: str, options: Optional[NormalizationOptions] = None) -> str:
    """
    Apply the full normalization pipeline to `text` and return a NEW string.
    `text` itself is never mutated -- callers are expected to keep the
    original alongside this result (see normalize_document() below for the
    original_text/normalized_text contract).
    """
    options = options or NormalizationOptions()
    result = text or ""
    result = normalize_alef(result)
    if options.unify_alef_maksura:
        result = normalize_alef_maksura(result)
    if options.unify_ta_marbuta:
        result = normalize_ta_marbuta(result)
    if options.strip_diacritics:
        result = strip_diacritics(result)
    result = strip_tatweel(result)
    result = normalize_digits(result)
    result = collapse_whitespace(result)
    return result


def normalize_document(original_text: str, options: Optional[NormalizationOptions] = None) -> dict:
    """
    Produce the {original_text, normalized_text, options} record that every
    downstream pipeline stage (split_articles.py etc.) should consume. This
    is the enforcement point for the "never destroy the original" rule --
    original_text is a straight passthrough, never touched.
    """
    return {
        "original_text": original_text,
        "normalized_text": normalize_text(original_text, options),
        "options": asdict(options or NormalizationOptions()),
    }


# --- CLI ----------------------------------------------------------------


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Normalize Arabic legal text (alef/digit/whitespace normalization, "
            "optional diacritic stripping). Never overwrites the original text -- "
            "always emits normalized_text as a separate field/file."
        )
    )
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--text", help="Normalize a literal string given on the command line.")
    src.add_argument("--input-file", type=Path, help="Path to a UTF-8 text file to normalize.")

    parser.add_argument(
        "--output-file",
        type=Path,
        help="Write the {original_text, normalized_text, options} JSON record here. "
        "If omitted, prints normalized_text to stdout.",
    )
    parser.add_argument(
        "--strip-diacritics",
        action="store_true",
        help="Strip tashkeel/diacritics. OFF by default -- legal text diacritics "
        "can be meaningful (see module docstring).",
    )
    parser.add_argument(
        "--unify-alef-maksura",
        action="store_true",
        help="Convert ى to ي. OFF by default (changes some word shapes).",
    )
    parser.add_argument(
        "--unify-ta-marbuta",
        action="store_true",
        help="Convert ة to ه. OFF by default (usually undesired for legal text).",
    )
    return parser


def main(argv: Optional[list] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.input_file is not None:
        if not args.input_file.exists():
            parser.error(f"--input-file does not exist: {args.input_file}")
        original_text = args.input_file.read_text(encoding="utf-8")
    else:
        original_text = args.text

    options = NormalizationOptions(
        strip_diacritics=args.strip_diacritics,
        unify_alef_maksura=args.unify_alef_maksura,
        unify_ta_marbuta=args.unify_ta_marbuta,
    )
    record = normalize_document(original_text, options)

    if args.output_file:
        args.output_file.parent.mkdir(parents=True, exist_ok=True)
        args.output_file.write_text(
            json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"Wrote normalized record to {args.output_file}")
    else:
        print(record["normalized_text"])

    return 0


def _run_smoke_test() -> None:
    """Inline smoke test (also exercised by doctest in the module docstring)."""
    assert normalize_alef("أحمد إبراهيم آدم ٱلرحمن") == "احمد ابراهيم ادم الرحمن"
    assert normalize_alef_maksura("ذهب إلى المدرسة") == "ذهب إلي المدرسة"
    assert normalize_ta_marbuta("المحكمة الجزئية") == "المحكمه الجزئيه"
    assert strip_diacritics("الْقَانُونُ الْمَدَنِيّ") == "القانون المدني"
    assert normalize_digits("المادة ١٤١ لسنة ٢٠٢٤") == "المادة 141 لسنة 2024"
    assert collapse_whitespace("مادة    1  \n\n  نص المادة") == "مادة 1 نص المادة"

    doc = normalize_document("  المادّة   الأولى:  يُعَاقَبُ   ...  ")
    assert doc["original_text"] == "  المادّة   الأولى:  يُعَاقَبُ   ...  "
    assert doc["normalized_text"] != doc["original_text"]
    print("normalize_arabic.py: all smoke-test assertions passed.")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No args at all -- run the smoke test rather than argparse's usage
        # error, since this script's core logic needs no external input.
        _run_smoke_test()
        sys.exit(0)
    sys.exit(main())
