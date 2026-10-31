"""
TODO STUB: OCR for scanned/image-only legal documents.

Intended behavior once implemented:
- Accept an image or a PDF page rendered to an image.
- Run an Arabic-capable OCR engine (e.g. Tesseract with the `ara` language
  pack, or a cloud OCR API) over the image.
- Return recognized text plus a confidence score so low-confidence pages
  can be flagged for manual review in the admin panel
  (see app/api/admin.py -- PATCH /admin/documents/{id}).

Not implemented yet: requires bundling/deploying an OCR engine and real
scanned source documents to validate against, neither of which exist in
this scaffold. Returns a clearly-labeled placeholder result.
"""
from typing import Optional, TypedDict


class OcrResult(TypedDict):
    text: Optional[str]
    confidence: Optional[float]
    status: str  # "ok" | "not_implemented" | "failed"


def ocr_image(image_path: str) -> OcrResult:
    """STUB: always returns not_implemented until a real OCR engine is wired up."""
    return OcrResult(text=None, confidence=None, status="not_implemented")
