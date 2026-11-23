"""Read-only reconciliation of staged Google Drive inventory against the catalog.

Run after applying the additive migration to a *test* database:
    cd backend
    python -m scripts.audit_library_inventory ../data/inventory

Does not download documents, modify records, or expose credentials.
"""
import argparse
import json
from collections import Counter
from pathlib import Path

from sqlalchemy import func
from app.database import SessionLocal
from app.models.library_catalog import LibraryAsset, LibraryTextChunk


def inventory_files(root: Path):
    paths = sorted(root.glob("drive_batch_*.json")) + sorted(root.glob("egypt_laws_nested_*.json"))
    if not paths:
        raise ValueError(f"No inventory manifests in {root}")
    items = {}
    duplicates = 0
    temporary = 0
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        for folder in payload.get("folders", []):
            for item in folder.get("items", []):
                if item.get("is_folder") or item.get("mime_type") == "application/vnd.google-apps.folder":
                    continue
                name = str(item.get("title", ""))
                if name.startswith("~$"):
                    temporary += 1
                    continue
                file_id = item.get("id")
                if not file_id:
                    continue
                if file_id in items:
                    duplicates += 1
                else:
                    items[file_id] = item
    return paths, items, duplicates, temporary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("inventory_dir", type=Path)
    args = parser.parse_args()
    paths, items, duplicates, temporary = inventory_files(args.inventory_dir)
    print(f"Manifests: {len(paths)}; unique source files: {len(items)}; repeated IDs: {duplicates}; temporary files excluded: {temporary}")
    with SessionLocal() as db:
        existing = {
            row.external_file_id: row
            for row in db.query(LibraryAsset).filter(LibraryAsset.provider == "google_drive").all()
        }
        matched = set(items) & set(existing)
        missing = set(items) - set(existing)
        extra = set(existing) - set(items)
        statuses = Counter((existing[k].review_status, existing[k].rights_status) for k in matched)
        chunks = db.query(func.count(LibraryTextChunk.id)).scalar()
        print(f"Present in DB: {len(matched)}; missing from DB: {len(missing)}; DB files outside staged manifests: {len(extra)}")
        print(f"Total text chunks in DB: {chunks}")
        for (review, rights), count in sorted(statuses.items()):
            print(f"  matched review={review} rights={rights}: {count}")
        print("Missing Drive IDs (first 30):")
        for file_id in sorted(missing)[:30]:
            print(f"  {file_id}: {items[file_id].get('title', '')[:100]}")
    print("Read-only audit completed. Inventory is incomplete; missing counts are not a full-library total.")


if __name__ == "__main__":
    main()
