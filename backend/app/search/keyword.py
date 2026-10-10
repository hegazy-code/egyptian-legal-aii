"""
Keyword search over the legal corpus.

Uses simple SQL LIKE matching, which works identically on SQLite and
Postgres. TODO: once on Postgres, swap this for a proper full-text search
(tsvector/websearch_to_tsquery) for better ranking; the function signatures
here are written so that swap is a drop-in change inside this module only.
"""
from typing import List

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.judgments import Judgment
from app.models.legal import Article
from app.schemas.legal import SearchResultItem
from app.utils.arabic import simple_normalize


def keyword_search_articles(db: Session, query: str, limit: int = 10) -> List[SearchResultItem]:
    normalized = simple_normalize(query)
    if not normalized:
        return []
    like_pattern = f"%{normalized}%"
    rows = (
        db.query(Article)
        .filter(or_(Article.text.ilike(like_pattern), Article.article_number.ilike(like_pattern)))
        .limit(limit)
        .all()
    )
    results = []
    for a in rows:
        snippet = (a.text or "")[:240]
        results.append(
            SearchResultItem(
                result_type="article",
                id=a.id,
                title=f"المادة {a.article_number}",
                snippet=snippet,
                score=1.0,
            )
        )
    return results


def keyword_search_judgments(db: Session, query: str, limit: int = 10) -> List[SearchResultItem]:
    normalized = simple_normalize(query)
    if not normalized:
        return []
    like_pattern = f"%{normalized}%"
    rows = (
        db.query(Judgment)
        .filter(or_(Judgment.summary.ilike(like_pattern), Judgment.full_text.ilike(like_pattern)))
        .limit(limit)
        .all()
    )
    results = []
    for j in rows:
        snippet = (j.summary or j.full_text or "")[:240]
        results.append(
            SearchResultItem(
                result_type="judgment",
                id=j.id,
                title=f"حكم رقم {j.case_number or ''} لسنة {j.year or ''}",
                snippet=snippet,
                score=1.0,
            )
        )
    return results
