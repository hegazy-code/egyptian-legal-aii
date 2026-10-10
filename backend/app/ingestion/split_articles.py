"""
TODO STUB: split a full law's normalized text into individual Article rows.

Intended behavior once implemented:
- Scan the normalized full text (see app.ingestion.normalize_arabic) for
  article boundary markers, typically lines starting with "مادة" or
  "المادة" followed by a number (optionally "مكرر").
- For each boundary, capture the article number and the text up to the next
  boundary (or end of document/chapter).
- Detect chapter/section headers (e.g. "الباب الأول", "الفصل الثاني") to
  populate Article.chapter / Article.section.
- Create one app.models.legal.Article row per detected article, linked to
  the parent Law, preserving order via Article.order_index.

Not implemented yet: needs a real, representative set of ingested law texts
to validate the boundary-detection regexes against (formatting varies
significantly between sources). Returns a clearly-labeled placeholder so
the ingestion pipeline can be wired end-to-end now and this step swapped in
later without touching any other module.
"""
from typing import List, TypedDict


class SplitArticleResult(TypedDict):
    article_number: str
    text: str
    chapter: str


def split_law_into_articles(law_full_text: str) -> List[SplitArticleResult]:
    """STUB: always returns an empty list until real boundary-detection is implemented."""
    return []
