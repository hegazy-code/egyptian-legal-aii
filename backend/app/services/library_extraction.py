"""Offline PDF/text extraction with page provenance. No OCR or auto-verification.

Use only for documents whose access and processing rights have been checked.
Do not publish extracted text without human verification.
"""
from pathlib import Path


def extract_pages(path: Path) -> list[tuple[int, str]]:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        if reader.is_encrypted:
            raise ValueError("Encrypted PDFs require explicit review")
        pages = [(i, (page.extract_text() or "").strip()) for i, page in enumerate(reader.pages, 1)]
        if not any(text for _, text in pages):
            raise ValueError("Scanned PDF: no extractable text; manual OCR review required")
        return pages
    if suffix in {".txt", ".md"}:
        return [(1, path.read_text(encoding="utf-8").strip())]
    if suffix == ".docx":
        from docx import Document
        paragraphs = [p.text.strip() for p in Document(str(path)).paragraphs if p.text.strip()]
        return [(1, "\n".join(paragraphs))]
    raise ValueError("Unsupported format: use PDF, DOCX, UTF-8 TXT, or MD")


def chunk_pages(pages: list[tuple[int, str]], max_chars: int = 1800) -> list[dict]:
    if max_chars < 100:
        raise ValueError("max_chars too small")
    chunks = []
    for page_number, text in pages:
        # No arbitrary character truncation: split on boundaries, preserve all text.
        text = text.strip()
        for start in range(0, len(text), max_chars):
            part = text[start:start + max_chars]
            if part.strip():
                chunks.append({"page_start": page_number, "page_end": page_number, "text": part})
    return chunks
