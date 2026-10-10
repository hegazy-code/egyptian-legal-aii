"""
TODO STUB (partial): normalization of raw ingested Arabic legal text before
it's split into articles / indexed for search.

The lightweight helpers actually used today by search live in
app/utils/arabic.py (diacritics stripping, digit/alef normalization) and are
real, working code -- reused here.

What's still a stub / needs real corpus data to build properly:
- OCR-artifact cleanup (broken ligatures, stray line breaks mid-word from
  justified PDF columns, reversed Arabic-Indic numerals from bad OCR).
- Canonicalizing law/article header formatting variants across different
  sources (gazette PDFs vs. scraped HTML) into one consistent shape before
  app.ingestion.split_articles runs.
"""
from app.utils.arabic import simple_normalize


def normalize_ingested_text(raw_text: str) -> str:
    """
    Currently just applies the basic normalization pipeline used by search.
    TODO: extend with OCR-artifact cleanup and source-specific header
    canonicalization once real ingested documents are available to test
    against.
    """
    return simple_normalize(raw_text)
