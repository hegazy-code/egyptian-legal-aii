"""
Loads the law texts shipped in backend/data/laws/*.json into the database.

Idempotent: a law is (re)loaded only if it isn't already present with the same number of articles.
Safe to run on every start (also works with an ephemeral SQLite database).
Each JSON file: {title, law_number, year, category, source_name, source_url, notes, articles:[{number, chapter, text}]}
"""
import json
import logging
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session

from app.models.legal import Article, Law, Source

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "laws"


def _get_or_create_source(db: Session, seed: dict) -> Source:
    name = seed.get("source_name") or "unknown"
    src = db.query(Source).filter(Source.name == name).first()
    if src is None:
        src = Source(
            name=name,
            source_type="community_dataset",
            url=seed.get("source_url"),
            publisher="HuggingFace dataflare/egypt-legal-corpus",
            reliability_score=2,  # 1-5 scale: unofficial, not verified against the Official Gazette
            notes="Unofficial community dataset; texts may predate later amendments.",
        )
        db.add(src)
        db.flush()
    return src


def load_law_file(db: Session, path: Path) -> Optional[int]:
    seed = json.loads(path.read_text(encoding="utf-8"))
    title = seed["title"]
    articles = seed.get("articles") or []
    law = db.query(Law).filter(Law.title == title, Law.law_number == seed.get("law_number")).first()
    if law is not None:
        existing = db.query(Article).filter(Article.law_id == law.id).count()
        if existing == len(articles):
            return None  # already loaded
        db.delete(law)  # cascades to its articles
        db.flush()
    src = _get_or_create_source(db, seed)
    law = Law(
        source_id=src.id,
        law_number=seed.get("law_number"),
        title=title,
        year=seed.get("year"),
        category=seed.get("category"),
        status="active",
    )
    db.add(law)
    db.flush()
    db.bulk_save_objects(
        [
            Article(
                law_id=law.id,
                article_number=a["number"],
                text=a["text"],
                chapter=(a.get("chapter") or None),
                order_index=i,
            )
            for i, a in enumerate(articles)
        ]
    )
    db.commit()
    return len(articles)


def load_all_laws(db: Session) -> int:
    """Load every law file; returns the number of articles newly inserted."""
    total = 0
    if not DATA_DIR.exists():
        return 0
    for path in sorted(DATA_DIR.glob("*.json")):
        try:
            n = load_law_file(db, path)
            if n:
                logger.info("Loaded %s (%d articles)", path.name, n)
                total += n
        except Exception:  # never block startup on a bad data file
            db.rollback()
            logger.exception("Failed to load law file %s", path.name)
    return total
