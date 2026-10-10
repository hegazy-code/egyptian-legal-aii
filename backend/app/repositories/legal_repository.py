"""Thin DB access layer for laws/articles/sources."""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.legal import Article, Law, Source


class LegalRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_laws(self, skip: int = 0, limit: int = 20) -> List[Law]:
        return self.db.query(Law).order_by(Law.created_at.desc()).offset(skip).limit(limit).all()

    def get_law(self, law_id: str) -> Optional[Law]:
        return self.db.query(Law).filter(Law.id == law_id).first()

    def get_article(self, article_id: str) -> Optional[Article]:
        return self.db.query(Article).filter(Article.id == article_id).first()

    def get_source(self, source_id: str) -> Optional[Source]:
        return self.db.query(Source).filter(Source.id == source_id).first()

    def create_source(self, source: Source) -> Source:
        self.db.add(source)
        self.db.commit()
        self.db.refresh(source)
        return source
