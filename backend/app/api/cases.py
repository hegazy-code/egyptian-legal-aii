"""POST/GET /cases, GET /cases/{id}."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models.users import User
from app.schemas.cases import CaseCreate, CaseRead
from app.services.case_service import CaseNotFoundError, CaseService

router = APIRouter(prefix="/cases", tags=["cases"])


@router.post("", response_model=CaseRead, status_code=status.HTTP_201_CREATED)
def create_case(payload: CaseCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = CaseService(db)
    case = service.create_case(current_user.id, payload.title, payload.description, payload.case_type)
    return case


@router.get("", response_model=List[CaseRead])
def list_cases(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CaseService(db)
    return service.list_cases(current_user.id, skip=skip, limit=limit)


@router.get("/{case_id}", response_model=CaseRead)
def get_case(case_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = CaseService(db)
    try:
        return service.get_case(case_id, current_user.id)
    except CaseNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
