from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class DocumentUploadedRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    case_id: Optional[str] = None
    filename: str
    mime_type: Optional[str] = None
    ocr_status: str
    extracted_text: Optional[str] = None
    created_at: datetime


# --- Admin-managed corpus Document (app.models.legal.Document) ---


class AdminDocumentCreate(BaseModel):
    title: str
    document_type: str = "law"
    source_id: Optional[str] = None
    raw_text: Optional[str] = None
    language: str = "ar"
    published_date: Optional[date] = None


class AdminDocumentUpdate(BaseModel):
    title: Optional[str] = None
    document_type: Optional[str] = None
    raw_text: Optional[str] = None
    status: Optional[str] = None
    published_date: Optional[date] = None


class AdminDocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    document_type: str
    status: str
    language: str
    created_at: datetime
