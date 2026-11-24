"""Tests for the read-only Drive inventory audit."""
import json
from pathlib import Path

from scripts.audit_library_inventory import inventory_files


def test_inventory_deduplicates_and_excludes_temporary_files(tmp_path: Path):
    batch = {"folders": [{"items": [
        {"id": "one", "title": "قانون.pdf", "mime_type": "application/pdf"},
        {"id": "folder", "title": "Nested", "is_folder": True},
        {"id": "temp", "title": "~$draft.doc", "mime_type": "application/msword"},
    ]}]}
    nested = {"folders": [{"items": [
        {"id": "one", "title": "قانون.pdf", "mime_type": "application/pdf"},
        {"id": "two", "title": "حكم.pdf", "mime_type": "application/pdf"},
    ]}]}
    (tmp_path / "drive_batch_01.json").write_text(json.dumps(batch), encoding="utf-8")
    (tmp_path / "egypt_laws_nested_01.json").write_text(json.dumps(nested), encoding="utf-8")
    paths, items, duplicates, temporary = inventory_files(tmp_path)
    assert len(paths) == 2
    assert set(items) == {"one", "two"}
    assert duplicates == 1
    assert temporary == 1


def test_inventory_rejects_empty_manifest_directory(tmp_path: Path):
    import pytest
    with pytest.raises(ValueError, match="No inventory manifests"):
        inventory_files(tmp_path)
