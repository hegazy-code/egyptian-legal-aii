"""
Merge exact-reference, keyword, and (stubbed) vector search into one ranked
result list. Exact article references always win and are placed first.
"""
from typing import List

from sqlalchemy.orm import Session

from app.models.legal import Article
from app.schemas.legal import SearchResultItem
from app.search.exact_reference import extract_article_references
from app.search.keyword import keyword_search_articles, keyword_search_judgments
from app.search.vector import vector_search


def hybrid_search(db: Session, query: str, limit: int = 10) -> List[SearchResultItem]:
    results: List[SearchResultItem] = []
    seen_ids = set()

    # 1. Exact article-number references take priority.
    for ref in extract_article_references(query):
        rows = db.query(Article).filter(Article.article_number == ref.article_number).limit(5).all()
        for a in rows:
            if a.id in seen_ids:
                continue
            seen_ids.add(a.id)
            results.append(
                SearchResultItem(
                    result_type="article",
                    id=a.id,
                    title=f"المادة {a.article_number}",
                    snippet=(a.text or "")[:240],
                    score=10.0,  # exact match ranks highest
                )
            )

    # 2. Keyword search (articles + judgments).
    for item in keyword_search_articles(db, query, limit=limit):
        if item.id not in seen_ids:
            seen_ids.add(item.id)
            results.append(item)
    for item in keyword_search_judgments(db, query, limit=limit):
        if item.id not in seen_ids:
            seen_ids.add(item.id)
            results.append(item)

    # 3. Vector search (stub -- currently a no-op, see search/vector.py).
    for item in vector_search(db, query, limit=limit):
        if item.id not in seen_ids:
            seen_ids.add(item.id)
            results.append(item)

    results.sort(key=lambda r: r.score, reverse=True)
    return results[:limit]
