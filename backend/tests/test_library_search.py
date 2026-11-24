"""Integration tests: importer idempotency and reviewed-only search."""
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.models import Base
from app.models.library_catalog import LibraryAsset, LibraryTextChunk
from app.services.library_search import search_verified_library


def test_verified_search_excludes_unreviewed_and_uncleared():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        for file_id, reviewed, rights, chunk_reviewed in [
            ("approved", "verified", "cleared", True),
            ("unreviewed", "unverified", "cleared", True),
            ("restricted", "verified", "unknown", True),
            ("chunk_unreviewed", "verified", "cleared", False),
        ]:
            asset = LibraryAsset(
                provider="google_drive", external_file_id=file_id,
                title=file_id, category="legislation", source_url="https://example.com/test.pdf",
                review_status=reviewed, rights_status=rights,
            )
            db.add(asset)
            db.flush()
            db.add(LibraryTextChunk(
                asset_id=asset.id, chunk_index=0,
                page_start=3, text="نص قانون العمل اختبار",
                verified=chunk_reviewed,
            ))
        db.commit()
        results = search_verified_library(db, "ما نصّ قانون العمل في مصر؟")
        assert len(results) == 1
        assert results[0]["title"] == "approved"
        assert results[0]["page_start"] == 3
        assert search_verified_library(db, "%") == []


def test_catalog_identity_constraint_is_enforced():
    from sqlalchemy.exc import IntegrityError
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        db.add(LibraryAsset(provider="google_drive", external_file_id="same", title="First"))
        db.commit()
        db.add(LibraryAsset(provider="google_drive", external_file_id="same", title="Second"))
        try:
            db.commit()
            assert False, "Expected duplicate identity to be rejected"
        except IntegrityError:
            db.rollback()
