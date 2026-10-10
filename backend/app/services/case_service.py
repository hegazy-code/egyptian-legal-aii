"""Business logic for user cases (personal legal matters)."""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.users import Case
from app.repositories.user_repository import CaseRepository


class CaseNotFoundError(Exception):
    pass


class CaseService:
    def __init__(self, db: Session):
        self.db = db
        self.cases = CaseRepository(db)

    def create_case(self, user_id: str, title: str, description: Optional[str], case_type: Optional[str]) -> Case:
        case = Case(user_id=user_id, title=title, description=description, case_type=case_type)
        return self.cases.create(case)

    def get_case(self, case_id: str, user_id: str) -> Case:
        case = self.cases.get(case_id)
        if not case or case.user_id != user_id:
            raise CaseNotFoundError(f"Case {case_id} not found.")
        return case

    def list_cases(self, user_id: str, skip: int = 0, limit: int = 20) -> List[Case]:
        return self.cases.list_for_user(user_id, skip=skip, limit=limit)
