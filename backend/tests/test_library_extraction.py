"""Tests for lossless page-local text extraction."""
from pathlib import Path
import pytest
from app.services.library_extraction import extract_pages, chunk_pages


def test_chunking_preserves_all_characters_and_page_numbers():
    original = "أ" * 251 + "ب" * 201
    chunks = chunk_pages([(7, original)], max_chars=120)
    assert "".join(item["text"] for item in chunks) == original
    assert all(item["page_start"] == 7 and item["page_end"] == 7 for item in chunks)


def test_utf8_file_extract(tmp_path: Path):
    file = tmp_path / "law.txt"
    file.write_text("نص قانون", encoding="utf-8")
    assert extract_pages(file) == [(1, "نص قانون")]


def test_unsupported_format(tmp_path: Path):
    with pytest.raises(ValueError, match="Unsupported"):
        extract_pages(tmp_path / "old.doc")


def test_pdf_extract_with_page_reference(tmp_path: Path):
    from reportlab.pdfgen import canvas
    file = tmp_path / "sample.pdf"
    c = canvas.Canvas(str(file))
    c.drawString(72, 700, "Legal text page one")
    c.showPage()
    c.drawString(72, 700, "Legal text page two")
    c.save()
    pages = extract_pages(file)
    assert len(pages) == 2
    assert "page one" in pages[0][1]
    assert "page two" in pages[1][1]
