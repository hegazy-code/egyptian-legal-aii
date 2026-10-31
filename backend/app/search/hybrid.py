"""
Merge exact-reference, keyword, and vector search into one ranked result list.
Exact article references always win and are placed first.
Now accepts an optional `legal_area` parameter to pre-filter results by law category.
"""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.legal import Article, Law
from app.schemas.legal import SearchResultItem
from app.search.exact_reference import extract_article_references
from app.search.keyword import keyword_search_articles, keyword_search_judgments
from app.search.vector import vector_search

_SNIPPET_SIZE = 500  # characters, keep consistent with keyword.py


def hybrid_search(
    db: Session,
    query: str,
    limit: int = 10,
    legal_area: Optional[str] = None,
) -> List[SearchResultItem]:
    """
    Hybrid search merging:
      1. Exact article-number references (score=10.0, highest priority)
      2. Keyword search (articles + judgments, scored by match density)
      3. Vector/semantic search (cosine similarity, if embeddings are available)

    When `legal_area` is provided (e.g. "قانون جنائي"), results are filtered to
    laws whose category matches -- reducing irrelevant cross-domain noise.
    """
    results: List[SearchResultItem] = []
    seen_ids = set()

    # Build a set of law_ids matching the legal_area for filtering.
    area_law_ids: Optional[set] = None
    if legal_area and legal_area.strip() and legal_area.strip() != "غير محدد":
        area_term = legal_area.strip()
        matching_laws = (
            db.query(Law.id)
            .filter(Law.category.ilike(f"%{area_term}%"))
            .all()
        )
        if matching_laws:
            area_law_ids = {row[0] for row in matching_laws}
            # If the filter matches no laws at all, don't restrict (avoids empty results).

    # 1. Exact article-number references take priority.
    for ref in extract_article_references(query):
        q = db.query(Article).filter(Article.article_number == ref.article_number)
        if area_law_ids:
            q = q.filter(Article.law_id.in_(area_law_ids))
        rows = q.limit(5).all()
        for a in rows:
            if a.id in seen_ids:
                continue
            seen_ids.add(a.id)
            results.append(
                SearchResultItem(
                    result_type="article",
                    id=a.id,
                    title=f"المادة {a.article_number}",
                    snippet=(a.text or "")[:_SNIPPET_SIZE],
                    score=10.0,
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

    # 3. Vector search (cosine similarity from JSONL embeddings if available).
    for item in vector_search(db, query, limit=limit):
        if item.id not in seen_ids:
            seen_ids.add(item.id)
            results.append(item)

    results.sort(key=lambda r: r.score, reverse=True)
    return results[:limit]
