"""POST /documents (user upload), GET /documents/{id}. OCR/analysis is a TODO stub."""
import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.ingestion.ocr import ocr_image
from app.models.users import DocumentUploaded, User
from app.schemas.documents import DocumentUploadedRead

router = APIRouter(prefix="/documents", tags=["documents"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "uploads")


@router.post("", response_model=DocumentUploadedRead, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    safe_name = f"{uuid.uuid4()}_{os.path.basename(file.filename or 'upload')}"
    dest_path = os.path.join(UPLOAD_DIR, safe_name)

    contents = await file.read()
    with open(dest_path, "wb") as f:
        f.write(contents)

    is_image = (file.content_type or "").startswith("image/")
    ocr_status = "not_applicable"
    extracted_text = None
    if is_image:
        # TODO: real OCR pipeline. See app/ingestion/ocr.py -- currently a stub.
        result = ocr_image(dest_path)
        ocr_status = result["status"]
        extracted_text = result["text"]

    doc = DocumentUploaded(
        user_id=current_user.id,
        filename=file.filename or safe_name,
        file_path=dest_path,
        mime_type=file.content_type,
        ocr_status=ocr_status,
        extracted_text=extracted_text,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.get("/{document_id}", response_model=DocumentUploadedRead)
def get_document(document_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    doc = db.query(DocumentUploaded).filter(DocumentUploaded.id == document_id).first()
    if not doc or doc.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return doc
