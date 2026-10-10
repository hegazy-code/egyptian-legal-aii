"""
Detect explicit legal-article references in Arabic text, e.g. "المادة 341"
or "المادة رقم 75 من قانون العقوبات", so exact-lookup can be prioritized
over fuzzy keyword search.
"""
import re
from dataclasses import dataclass
from typing import List, Optional

from app.utils.arabic import normalize_arabic_digits

# Matches: المادة (رقم)? <number> (من <law name>)?
_ARTICLE_REF_RE = re.compile(
    r"(?:المادة|مادة)\s*(?:رقم)?\s*\(?\s*(\d+)\s*\)?"
    r"(?:\s*(?:مكرر|مكررا|مكرراً))?"
    r"(?:\s*من\s+([؀-ۿ\s]{3,60}?))?(?=[.,؛،؟!]|$)"
)


@dataclass
class ArticleReference:
    article_number: str
    law_name: Optional[str] = None
    raw_match: str = ""


def extract_article_references(text: str) -> List[ArticleReference]:
    """Find all 'المادة N (من قانون كذا)' style references in free text."""
    if not text:
        return []
    normalized = normalize_arabic_digits(text)
    refs: List[ArticleReference] = []
    for match in _ARTICLE_REF_RE.finditer(normalized):
        number = match.group(1)
        law_name = match.group(2).strip() if match.group(2) else None
        refs.append(ArticleReference(article_number=number, law_name=law_name, raw_match=match.group(0)))
    return refs


def has_exact_reference(text: str) -> bool:
    return len(extract_article_references(text)) > 0
