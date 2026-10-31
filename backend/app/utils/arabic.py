"""Small Arabic text helpers used across search/ingestion/rag."""
import re

_ARABIC_DIACRITICS = re.compile(r"[ً-ٰٟۖ-ۭ]")
_ARABIC_INDIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def strip_diacritics(text: str) -> str:
    """Remove Arabic diacritical marks (tashkeel) for more robust matching."""
    return _ARABIC_DIACRITICS.sub("", text or "")


def normalize_arabic_digits(text: str) -> str:
    """Convert Arabic-Indic digits (٠-٩) to ASCII digits (0-9)."""
    return (text or "").translate(_ARABIC_INDIC_DIGITS)


def normalize_alef_forms(text: str) -> str:
    """Collapse alef variants (أ إ آ) to bare alef (ا) for lenient matching."""
    if not text:
        return text
    for ch in ("أ", "إ", "آ"):
        text = text.replace(ch, "ا")
    return text


def simple_normalize(text: str) -> str:
    """Light normalization pipeline used by keyword search."""
    text = strip_diacritics(text)
    text = normalize_arabic_digits(text)
    text = normalize_alef_forms(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text
