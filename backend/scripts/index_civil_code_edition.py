"""Index the Egyptian Tax Authority Civil Code PDF edition for source review."""
import argparse
import hashlib
import re
import sqlite3
import subprocess
import unicodedata
from pathlib import Path

SOURCE = "https://www.eta.gov.eg/sites/default/files/2024-10/law-131-1948.pdf"
ARTICLE = re.compile(r"^ *مادة *(?:\([0-9]+\) *)?(?:[–-] *([0-9]+)|([0-9]+) *[–-])", re.M)


def index(pdf: Path, db: sqlite3.Connection) -> None:
    extracted = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"], check=True, capture_output=True, text=True,
    ).stdout
    pages = extracted.split("\f")
    if not pages[-1].strip():
        pages.pop()
    if len(pages) != 100:
        raise ValueError("Expected the 100-page Egyptian Tax Authority edition")

    db.executescript("""
        CREATE TABLE source (url TEXT NOT NULL, sha256 TEXT NOT NULL, review_status TEXT NOT NULL);
        CREATE TABLE pages (number INTEGER PRIMARY KEY, extracted_text TEXT NOT NULL);
        CREATE TABLE article_candidates (article_number INTEGER NOT NULL, page_number INTEGER NOT NULL,
            UNIQUE (article_number, page_number), FOREIGN KEY (page_number) REFERENCES pages(number));
    """)
    remaining_issuance_articles = 2
    with db:
        db.execute("INSERT INTO source VALUES (?, ?, 'needs_review')",
                   (SOURCE, hashlib.sha256(pdf.read_bytes()).hexdigest()))
        for number, page in enumerate(pages, 1):
            db.execute("INSERT INTO pages VALUES (?, ?)", (number, page))
            normalized = "".join(
                char for char in unicodedata.normalize("NFKC", page)
                if unicodedata.category(char) != "Cf"
            )
            for match in ARTICLE.finditer(normalized):
                if remaining_issuance_articles:
                    remaining_issuance_articles -= 1
                    continue
                article = int(match.group(1) or match.group(2))
                db.execute("INSERT OR IGNORE INTO article_candidates VALUES (?, ?)", (article, number))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Choose a new output database")
    with sqlite3.connect(args.output) as db:
        index(args.pdf, db)


if __name__ == "__main__":
    main()
