"""Legal source configuration safety: do not activate sources without rights."""
import json
from pathlib import Path

REGISTRY = Path(__file__).resolve().parents[1] / "data" / "judgment_source_registry.json"


def test_cassation_automated_extraction_is_disabled():
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    cassation = next(s for s in registry["sources"] if s["id"] == "cassation")
    assert cassation["index_url"] == "https://cc.gov.eg/judgments_search/"
    assert cassation["terms_url"] == "https://cc.gov.eg/terms"
    assert cassation["enabled"] is False
    assert cassation["automated_retrieval_permitted"] is False
    assert cassation["commercial_republication_permitted"] is False
    assert registry["publication_enabled"] is False


def test_no_unlicensed_source_is_automatically_enabled():
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    assert all(not s["enabled"] for s in registry["sources"] if s["rights_review_required"])
