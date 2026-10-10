"""
Fetches the Egyptian law texts from the public dataset API (HuggingFace dataflare/egypt-legal-corpus,
MIT licence) and loads them into the database -- no hand-made data files needed.

How it works:
  1. Find which laws from MANIFEST are not in the database yet (the shipped data/laws/*.json load first).
  2. Download the dataset's parquet file (URL discovered through the HuggingFace API, or LAW_DATASET_URL).
  3. For each wanted document (matched by an md5 of its text) split it into articles and store them.
Never raises into the caller: on any failure it logs and returns 0, and the app keeps whatever is loaded.
"""
import hashlib
import logging
import os
import re
import tempfile
from typing import Optional

import httpx
from sqlalchemy.orm import Session

from app.models.legal import Article, Law
from app.seed.law_manifest import MANIFEST
from app.seed.load_laws import _get_or_create_source
from app.seed.splitter import attach_chapters, split_articles, split_keyword

logger = logging.getLogger(__name__)

DATASET = "dataflare/egypt-legal-corpus"
HF_PARQUET_LIST = f"https://huggingface.co/api/datasets/{DATASET}/parquet/default/train"
SOURCE_URL = f"https://huggingface.co/datasets/{DATASET}"
SOURCE_NAME = "dataflare/egypt-legal-corpus (HuggingFace)"
BASE_NOTE = "نص أساسي من مجموعة بيانات مجتمعية غير رسمية؛ قد لا يتضمن التعديلات اللاحقة (خاصة مبالغ الغرامات والرسوم والعقوبات). "


def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip(" .-/")


def parse_articles(text: str, max_n: int = 1500) -> list[dict]:
    """Pick the better of the two splitters (keyword mode vs table mode) and clean the result."""
    kw = [{"number": n, "chapter": "", "text": t} for n, t in split_keyword(text, max_n)]
    tb = attach_chapters(split_articles(text, max_n))
    arts = kw if len(kw) >= len(tb) else tb
    out, seen = [], set()
    for a in arts:
        n = a["number"].strip().lstrip("0") or a["number"]
        t = _clean(a["text"])
        if len(t) < 12 or n in seen:
            continue
        seen.add(n)
        out.append({"number": n, "chapter": _clean(a.get("chapter", "")), "text": t})
    return out


def _missing_entries(db: Session) -> list[tuple]:
    have = {(l.title, l.law_number or "") for l in db.query(Law).all()}
    return [m for m in MANIFEST if (m[2], m[3]) not in have]


def _find_dataset_url() -> Optional[str]:
    override = os.environ.get("LAW_DATASET_URL")
    if override:
        return override
    r = httpx.get(HF_PARQUET_LIST, timeout=30, follow_redirects=True)
    r.raise_for_status()
    urls = r.json()
    return urls[0] if urls else None


def _download(url: str) -> str:
    if os.path.exists(url):  # local file (tests / offline use)
        return url
    fd, path = tempfile.mkstemp(suffix=".parquet")
    os.close(fd)
    with httpx.stream("GET", url, timeout=120, follow_redirects=True) as r:
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_bytes(1 << 20):
                f.write(chunk)
    return path


def sync_from_dataset(db: Session) -> int:
    """Load every manifest law that is not in the DB yet. Returns the number of articles inserted."""
    try:
        wanted = {m[1]: m for m in _missing_entries(db)}
        if not wanted:
            return 0
        import pyarrow.parquet as pq

        url = _find_dataset_url()
        if not url:
            logger.warning("Law dataset URL not found; skipping auto-fetch")
            return 0
        path = _download(url)
        total = 0
        try:
            pf = pq.ParquetFile(path)
            for batch in pf.iter_batches(batch_size=128, columns=["text"]):
                for text in batch.column("text").to_pylist():
                    if not text:
                        continue
                    h = hashlib.md5(text.encode()).hexdigest()
                    entry = next((wanted[k] for k in wanted if h.startswith(k)), None)
                    if entry is None:
                        continue
                    slug, _, title, number, year, category, note = entry
                    arts = parse_articles(text)
                    if not arts:
                        continue
                    if db.query(Law).filter(Law.title == title, Law.law_number == number).first():
                        continue
                    seed = {"source_name": SOURCE_NAME, "source_url": SOURCE_URL}
                    src = _get_or_create_source(db, seed)
                    law = Law(source_id=src.id, law_number=number, title=title, year=year,
                              category=category, status="active")
                    db.add(law)
                    db.flush()
                    db.bulk_save_objects([
                        Article(law_id=law.id, article_number=a["number"], text=a["text"],
                                chapter=a["chapter"] or None, order_index=i)
                        for i, a in enumerate(arts)
                    ])
                    db.commit()
                    logger.info("Fetched %s (%d articles) from dataset API", slug, len(arts))
                    total += len(arts)
        finally:
            if path != url and os.path.exists(path):
                os.remove(path)
        return total
    except Exception:
        db.rollback()
        logger.exception("Law auto-fetch from dataset failed; continuing with loaded data")
        return 0
