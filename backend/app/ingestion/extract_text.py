"""
TODO STUB: text extraction from raw ingested documents (PDF/HTML/DOCX).

Intended behavior once implemented:
- Detect file type (PDF, DOCX, HTML, plain text) from the Document's file_path.
- For PDFs: use a library such as pdfplumber/PyMuPDF to extract selectable
  text page-by-page; fall back to app.ingestion.ocr for scanned/image-only
  pages.
- For HTML (e.g. official gazette web pages): strip markup with something
  like BeautifulSoup, preserving paragraph/article boundaries.
- Return the extracted plain text plus basic metadata (page count, whether
  OCR was needed) so it can be stored on Document.raw_text and queued for
  app.ingestion.split_articles.

Not implemented yet because there is no real ingested source corpus to test
against. Returns a clearly-labeled NotImplemented-style placeholder so
callers can integrate against this interface now.
"""
from typing import Optional, TypedDict


class ExtractedText(TypedDict):
    text: Optional[str]
    method: str  # "native" | "ocr" | "unsupported"
    status: str  # "ok" | "not_implemented" | "failed"


def extract_text_from_file(file_path: str) -> ExtractedText:
    """STUB: always returns not_implemented until a real extractor is wired up."""
    return ExtractedText(
        text=None,
        method="unsupported",
        status="not_implemented",
    )
