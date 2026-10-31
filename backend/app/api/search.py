"""POST /search, GET /laws, GET /laws/{id}, GET /articles/{id}."""
import time
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.system import SearchLog
from app.repositories.legal_repository import LegalRepository
from app.schemas.legal import ArticleRead, LawDetailRead, LawRead, SearchRequest, SearchResponse
from app.search.hybrid import hybrid_search

router = APIRouter(tags=["search"])


@router.post("/search", response_model=SearchResponse)
def search(payload: SearchRequest, db: Session = Depends(get_db)):
    start = time.perf_counter()
    results = hybrid_search(db, payload.query, limit=payload.limit)
    latency_ms = int((time.perf_counter() - start) * 1000)

    db.add(
        SearchLog(
            query_text=payload.query,
            query_type="hybrid",
            results_count=len(results),
            latency_ms=latency_ms,
        )
    )
    db.commit()

    return SearchResponse(query=payload.query, total=len(results), results=results)


@router.get("/laws", response_model=List[LawRead])
def list_laws(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    repo = LegalRepository(db)
    return repo.list_laws(skip=skip, limit=limit)


@router.get("/laws/{law_id}", response_model=LawDetailRead)
def get_law(law_id: str, db: Session = Depends(get_db)):
    repo = LegalRepository(db)
    law = repo.get_law(law_id)
    if not law:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Law not found")
    return law


@router.get("/articles/{article_id}", response_model=ArticleRead)
def get_article(article_id: str, db: Session = Depends(get_db)):
    repo = LegalRepository(db)
    article = repo.get_article(article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    return article
