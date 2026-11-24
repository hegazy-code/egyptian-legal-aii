"""Regression checks for safe catalog imports (run with pytest)."""
import pytest

from scripts.import_library_inventory import validate


def test_rejects_duplicate_drive_ids():
    with pytest.raises(ValueError, match="Duplicate file ID"):
        validate([{"id": "same", "title": "A"}, {"id": "same", "title": "B"}])


def test_rejects_missing_identity():
    with pytest.raises(ValueError, match="id and title required"):
        validate([{"title": "Missing ID"}])


def test_rejects_unknown_category():
    with pytest.raises(ValueError, match="invalid category"):
        validate([{"id": "1", "title": "Test", "category": "official_verified"}])


def test_valid_inventory_keeps_source_identity():
    rows = validate([{"id": "drive-1", "title": "قانون", "category": "legislation"}])
    assert rows[0][0] == "drive-1"
    assert rows[0][2] == "legislation"
