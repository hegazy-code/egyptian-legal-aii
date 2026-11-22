"""Import a Drive inventory JSON into the *catalog only*, never into reviewed answers.

Usage (after migration, with a database backup):
  cd backend
  python -m scripts.import_library_inventory /path/to/inventory.json --dry-run
  python -m scripts.import_library_inventory /path/to/inventory.json --apply

Input: JSON list of {id, title, mime_type, url, parent_id, path, size, category}.
No file text is downloaded or asserted to be verified by this command.
"""
import argparse
import json
from pathlib import Path

from app.database import SessionLocal
from app.models.library_catalog import LibraryAsset

ALLOWED_CATEGORIES = {
    "legislation", "judgment", "appeal", "reconsideration",
    "commentary", "template", "procedure", "academic", "unclassified",
}


def validate(records):
    if not isinstance(records, list):
        raise ValueError("Inventory must be a JSON array")
    result = []
    seen = set()
    for i, item in enumerate(records):
        if not isinstance(item, dict):
            raise ValueError(f"Row {i}: expected object")
        file_id = str(item.get("id") or "").strip()
        title = str(item.get("title") or "").strip()
        category = item.get("category") or "unclassified"
        if not file_id or not title:
            raise ValueError(f"Row {i}: id and title required")
        if category not in ALLOWED_CATEGORIES:
            raise ValueError(f"Row {i}: invalid category {category}")
        if file_id in seen:
            raise ValueError(f"Duplicate file ID in inventory: {file_id}")
        seen.add(file_id)
        result.append((file_id, title, category, item))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("inventory", type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    records = validate(json.loads(args.inventory.read_text(encoding="utf-8")))
    if args.dry_run:
        print(f"Validated {len(records)} unique Drive items; database unchanged")
        return
    with SessionLocal() as db:
        inserted = 0
        existing = 0
        try:
            for file_id, title, category, item in records:
                row = db.query(LibraryAsset).filter_by(
                    provider="google_drive", external_file_id=file_id
                ).one_or_none()
                if row:
                    existing += 1
                    continue  # preserve reviewed content and human edits
                db.add(LibraryAsset(
                    provider="google_drive",
                    external_file_id=file_id,
                    parent_external_id=item.get("parent_id"),
                    original_path=item.get("path"),
                    title=title[:500],
                    source_url=item.get("url"),
                    mime_type=item.get("mime_type"),
                    byte_size=item.get("size"),
                    category=category,
                    extraction_status="pending",
                    review_status="unverified",
                    rights_status="unknown",
                ))
                inserted += 1
            db.commit()
        except Exception:
            db.rollback()
            raise
    print(f"Inserted {inserted}; already present {existing}; no text published")


if __name__ == "__main__":
    main()
