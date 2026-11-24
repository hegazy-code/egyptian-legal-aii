"""Stage extracted text for a catalog asset without approving or publishing it.

Usage: python -m scripts.stage_library_text FILE_ID /path/to/file.pdf --dry-run
       python -m scripts.stage_library_text FILE_ID /path/to/file.pdf --apply

Requires an existing catalog record and a local, authorized copy of the file.
Only new, unreviewed assets may be staged. Never changes rights/review status.
"""
import argparse
import hashlib
from pathlib import Path
from sqlalchemy import select
from app.database import SessionLocal
from app.models.library_catalog import LibraryAsset, LibraryTextChunk
from app.services.library_extraction import extract_pages, chunk_pages


def stage(db, external_file_id: str, path: Path, apply: bool = False) -> dict:
    asset = db.scalar(select(LibraryAsset).where(
        LibraryAsset.provider == "google_drive",
        LibraryAsset.external_file_id == external_file_id,
    ))
    if asset is None:
        raise ValueError("File not present in catalog")
    if asset.review_status != "unverified":
        raise ValueError("Reviewed assets cannot be replaced by automated extraction")
    if db.scalar(select(LibraryTextChunk.id).where(LibraryTextChunk.asset_id == asset.id).limit(1)):
        raise ValueError("Chunks already exist; manual review required before replacement")
    if not path.is_file() or path.stat().st_size > 30_000_000:
        raise ValueError("Missing file or file exceeds 30 MB")
    with path.open("rb") as stream:
        data_hash = hashlib.file_digest(stream, "sha256").hexdigest()
    pages = extract_pages(path)
    chunks = chunk_pages(pages)
    if not chunks:
        raise ValueError("No text extracted")
    result = {"pages": len(pages), "chunks": len(chunks), "sha256": data_hash, "review_status": "unverified"}
    if apply:
        try:
            for i, item in enumerate(chunks):
                db.add(LibraryTextChunk(asset_id=asset.id, chunk_index=i,
                    page_start=item["page_start"], page_end=item["page_end"],
                    text=item["text"], extraction_method="offline", verified=False))
            asset.sha256 = data_hash
            asset.extraction_status = "extracted_unverified"
            db.commit()
        except Exception:
            db.rollback()
            raise
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file_id")
    parser.add_argument("file", type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    with SessionLocal() as db:
        print(stage(db, args.file_id, args.file, apply=args.apply))


if __name__ == "__main__":
    main()
