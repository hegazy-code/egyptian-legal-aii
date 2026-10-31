"""Thin DB access layer for judgments/courts."""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.judgments import Court, Judgment


class JudgmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, judgment_id: str) -> Optional[Judgment]:
        return self.db.query(Judgment).filter(Judgment.id == judgment_id).first()

    def list(self, skip: int = 0, limit: int = 20) -> List[Judgment]:
        return self.db.query(Judgment).order_by(Judgment.created_at.desc()).offset(skip).limit(limit).all()

    def list_by_court(self, court_id: str, skip: int = 0, limit: int = 20) -> List[Judgment]:
        return (
            self.db.query(Judgment)
            .filter(Judgment.court_id == court_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_court(self, court_id: str) -> Optional[Court]:
        return self.db.query(Court).filter(Court.id == court_id).first()
