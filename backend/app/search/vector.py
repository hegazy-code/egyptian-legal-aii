"""
Semantic/vector search using cosine similarity.

Implementation loads embeddings from data/embeddings/articles.jsonl (generated
by scripts/create_embeddings.py) into memory on first call, then embeds the
query via Gemini text-embedding-004 and ranks by cosine similarity.

Falls back to an empty result set when:
  - The JSONL file doesn't exist yet (no embeddings generated)
  - The Gemini API key isn't configured
  - Any unexpected error occurs

This keeps the hybrid search callers safe regardless of state.

TODO: once on Postgres + pgvector, replace the in-memory approach with:
    db.execute("SELECT id FROM embeddings ORDER BY embedding <-> :q LIMIT :k", ...)
"""
import json
import logging
import math
from pathlib import Path
from typing import List, Optional

from sqlalchemy.orm import Session

from app.schemas.legal import SearchResultItem

logger = logging.getLogger(__name__)

_EMBEDDINGS_JSONL = Path("data/embeddings/articles.jsonl")
_SIMILARITY_THRESHOLD = 0.50   # minimum cosine similarity to include a result
_SCORE_SCALE = 5.0             # multiply cosine [0,1] to sit below exact-ref score of 10

# Module-level cache so we only read the file once per process.
_CACHE: Optional[List[dict]] = None


def _load_embeddings() -> List[dict]:
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    if not _EMBEDDINGS_JSONL.exists():
        logger.debug("vector_search: %s not found -- returning empty results", _EMBEDDINGS_JSONL)
        _CACHE = []
        return _CACHE
    data: List[dict] = []
    try:
        with open(_EMBEDDINGS_JSONL, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    obj = json.loads(line)
                    if obj.get("embedding"):
                        data.append(obj)
        logger.info("vector_search: loaded %d embeddings from %s", len(data), _EMBEDDINGS_JSONL)
    except Exception as exc:
        logger.warning("vector_search: failed to load embeddings: %s", exc)
        data = []
    _CACHE = data
    return _CACHE


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def _embed_query(query: str) -> Optional[List[float]]:
    """Embed a query string with Gemini text-embedding-004, task type RETRIEVAL_QUERY."""
    try:
        from app.config import settings
        if not settings.GEMINI_API_KEY:
            return None
        from google import genai
        from google.genai import types as genai_types

        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        result = client.models.embed_content(
            model="text-embedding-004",
            contents=query,
            config=genai_types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
        )
        return list(result.embeddings[0].values)
    except Exception as exc:
        logger.warning("vector_search: could not embed query: %s", exc)
        return None


def vector_search(db: Session, query: str, limit: int = 10) -> List[SearchResultItem]:
    """
    Returns up to `limit` results ranked by semantic similarity.
    Returns an empty list if embeddings aren't available or the API call fails.
    """
    embeddings = _load_embeddings()
    if not embeddings:
        return []

    query_vec = _embed_query(query)
    if query_vec is None:
        return []

    scored: List[tuple] = []
    for item in embeddings:
        emb = item.get("embedding", [])
        if not emb:
            continue
        sim = _cosine_similarity(query_vec, emb)
        if sim >= _SIMILARITY_THRESHOLD:
            scored.append((sim, item))

    scored.sort(key=lambda x: x[0], reverse=True)

    results: List[SearchResultItem] = []
    for sim, item in scored[:limit]:
        results.append(
            SearchResultItem(
                result_type="article",
                id=item.get("article_id", ""),
                title=f"المادة {item.get('article_number', '')}",
                snippet=(item.get("text_preview") or "")[:500],
                score=float(sim) * _SCORE_SCALE,
            )
        )
    return results
