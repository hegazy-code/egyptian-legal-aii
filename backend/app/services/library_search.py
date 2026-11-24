"""Retrieve reviewed library excerpts and their source pages for Ask."""
import re

from sqlalchemy import and_, case, func, or_
from sqlalchemy.orm import Session

from app.models.library_catalog import LibraryAsset, LibraryTextChunk
from app.utils.arabic import simple_normalize

_STOP_WORDS = {
    "الذي", "التي", "مصر", "قانون", "القانون", "المادة", "مادة", "لسنة",
    "لسنه", "كيف", "متى", "ماذا", "يمكن", "بخصوص",
}
_PRIMARY_CATEGORIES = ("legislation", "judgment", "appeal", "reconsideration")


def search_verified_library(db: Session, query: str, limit: int = 10) -> list[dict]:
    query = simple_normalize(query[:2000])
    if re.search(r"شقة|شقه|مسكن|ايجار", query) and re.search(r"يطرد|طرد|اخلاء|يخليني|فسخ|ينهي", query):
        query = "ايجار اخلاء " + query
    tokens = list(dict.fromkeys(
        word for word in re.findall(r"[^\W_]+", query)
        if (len(word) >= 3 or word.isdecimal()) and word not in _STOP_WORDS
    ))[:12]
    if not tokens:
        return []

    title = LibraryAsset.title
    body = LibraryTextChunk.text
    for old, new in zip("أإآ٠١٢٣٤٥٦٧٨٩", "ااا0123456789"):
        title = func.replace(title, old, new)
        body = func.replace(body, old, new)

    title_matches = [title.ilike(f"%{token}%") for token in tokens]
    text_matches = [body.ilike(f"%{token}%") for token in tokens]
    matched = sum(case((or_(t, b), 1), else_=0) for t, b in zip(title_matches, text_matches))
    title_rank = sum(case((match, 1), else_=0) for match in title_matches)
    reviewed = (
        db.query(LibraryTextChunk, LibraryAsset)
        .join(LibraryAsset, LibraryTextChunk.asset_id == LibraryAsset.id)
        .filter(
            LibraryAsset.category.in_(_PRIMARY_CATEGORIES),
            LibraryAsset.review_status == "verified",
            LibraryAsset.rights_status == "cleared",
            LibraryTextChunk.verified.is_(True),
            or_(
                LibraryTextChunk.page_start >= 1,
                and_(
                    LibraryAsset.provider == "official",
                    LibraryTextChunk.extraction_method == "reviewed_summary",
                ),
            ),
            LibraryAsset.source_url.like("https://_%"),

        )
    )
    reference = re.search(r"(?:المادة|مادة)\s*([0-9]+)\b", query)
    matches = []
    if reference and re.search(r"المدني|مدني|131\s+لسنة\s+1948", query):
        identity = f"egypt-civil-131-1948-article-{reference.group(1)}"
        matches = reviewed.filter(
            LibraryAsset.provider == "official",
            LibraryAsset.external_file_id == identity,
        ).order_by(LibraryTextChunk.chunk_index).all()
    if not matches:
        matches = (
            reviewed.filter(matched >= min(2, len(tokens)))
            .order_by(matched.desc(), title_rank.desc(), LibraryAsset.title,
                      LibraryTextChunk.chunk_index, LibraryAsset.id)
            .limit(max(1, min(limit, 25)))
            .all()
        )

    return [
        {
            "id": chunk.id,
            "title": asset.title,
            "source_url": asset.source_url,
            "category": asset.category,
            "page_start": chunk.page_start,
            "page_end": chunk.page_end,
            "text": chunk.text,
            "article_number": asset.external_file_id.rsplit("-", 1)[-1]
                if asset.provider == "official"
                and asset.external_file_id.startswith("egypt-civil-131-1948-article-")
                else None,
        }
        for chunk, asset in matches
    ]
