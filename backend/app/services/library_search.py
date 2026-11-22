"""Conservative legal-library search for reviewed source excerpts.

This deliberately does not replace the existing answer engine. It only returns
human-reviewed, rights-cleared chunks, each with its originating file and page.
"""
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.models.library_catalog import LibraryAsset, LibraryTextChunk


def search_verified_library(db: Session, query: str, limit: int = 10) -> list[dict]:
    term = query.strip()
    if len(term) < 2 or len(term) > 200:
        return []
    limit = max(1, min(int(limit), 25))
    # Escape SQL LIKE metacharacters so user input remains a literal search term.
    escaped = term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    matches = (
        db.query(LibraryTextChunk, LibraryAsset)
        .join(LibraryAsset, LibraryTextChunk.asset_id == LibraryAsset.id)
        .filter(
            LibraryAsset.review_status == "verified",
            LibraryAsset.rights_status == "cleared",
            LibraryTextChunk.verified.is_(True),
            LibraryTextChunk.text.ilike(f"%{escaped}%", escape="\\"),
        )
        .order_by(LibraryAsset.title, LibraryTextChunk.chunk_index)
        .limit(limit)
        .all()
    )
    return [
        {
            "asset_id": asset.id,
            "title": asset.title,
            "source_url": asset.source_url,
            "category": asset.category,
            "page_start": chunk.page_start,
            "page_end": chunk.page_end,
            "text": chunk.text,
            "authority": "secondary" if asset.category in {"commentary", "academic"} else "source",
        }
        for chunk, asset in matches
    ]
