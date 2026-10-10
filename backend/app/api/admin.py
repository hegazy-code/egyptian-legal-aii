"""
Admin-only endpoints: POST /admin/sources, POST /admin/documents,
PATCH /admin/documents/{id}, POST /admin/reindex, GET /admin/evaluations.
"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin_user
from app.database import get_db
from app.models.legal import Document, Source
from app.models.system import AuditLog, EvaluationResult
from app.models.users import User
from app.repositories.legal_repository import LegalRepository
from app.schemas.documents import AdminDocumentCreate, AdminDocumentRead, AdminDocumentUpdate
from app.schemas.legal import SourceCreate, SourceRead

router = APIRouter(prefix="/admin", tags=["admin"])


class ReindexResponse(BaseModel):
    status: str
    detail: str


class EvaluationResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    message_id: Optional[str] = None
    evaluator: str
    score: Optional[float] = None
    criteria: Optional[str] = None
    created_at: datetime


def _log_admin_action(db: Session, admin: User, action: str, entity_type: str, entity_id: str):
    db.add(AuditLog(user_id=admin.id, action=action, entity_type=entity_type, entity_id=entity_id))
    db.commit()


@router.post("/sources", response_model=SourceRead, status_code=status.HTTP_201_CREATED)
def create_source(
    payload: SourceCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    repo = LegalRepository(db)
    source = repo.create_source(Source(**payload.model_dump()))
    _log_admin_action(db, admin, "create_source", "source", source.id)
    return source


@router.post("/documents", response_model=AdminDocumentRead, status_code=status.HTTP_201_CREATED)
def create_document(
    payload: AdminDocumentCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    doc = Document(**payload.model_dump())
    db.add(doc)
    db.commit()
    db.refresh(doc)
    _log_admin_action(db, admin, "create_document", "document", doc.id)
    return doc


@router.patch("/documents/{document_id}", response_model=AdminDocumentRead)
def update_document(
    document_id: str,
    payload: AdminDocumentUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(doc, field, value)
    db.commit()
    db.refresh(doc)
    _log_admin_action(db, admin, "update_document", "document", doc.id)
    return doc


@router.post("/reindex", response_model=ReindexResponse)
def reindex(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    """
    TODO: real implementation should (re)compute embeddings for every
    article/judgment via app.search.vector once that's wired up, and
    rebuild any full-text search indexes. Currently a stub that just
    records the request via an audit log entry so the endpoint is wired
    end-to-end and callable, without pretending to do real indexing work.
    """
    _log_admin_action(db, admin, "reindex_requested", "system", "-")
    return ReindexResponse(
        status="not_implemented",
        detail="Reindexing is a TODO stub -- requires real embeddings/vector search (see app/search/vector.py).",
    )


@router.get("/evaluations", response_model=List[EvaluationResultRead])
def list_evaluations(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    return (
        db.query(EvaluationResult)
        .order_by(EvaluationResult.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
