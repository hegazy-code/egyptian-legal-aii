"""
TODO: semantic/vector search stub.

Real implementation needs: (1) an embeddings model call (e.g. Gemini
embeddings) run over the ingested corpus and stored in app.models.system.Embedding,
and (2) a vector index -- pgvector's `<->` distance operator once we're on
Postgres with real data volume. Until then this returns an empty result set
so callers (hybrid search) can safely call it without special-casing.
"""
from typing import List

from sqlalchemy.orm import Session

from app.schemas.legal import SearchResultItem


def vector_search(db: Session, query: str, limit: int = 10) -> List[SearchResultItem]:
    """STUB: always returns no results until embeddings + pgvector are wired up."""
    return []
