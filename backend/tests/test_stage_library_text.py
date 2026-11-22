"""Stage an authorized local text file, preserving review gates and idempotency."""
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from app.models import Base
from app.models.library_catalog import LibraryAsset, LibraryTextChunk
from scripts.stage_library_text import stage
from app.services.library_search import search_verified_library


def test_stage_unverified_dry_run_and_restage_blocked(tmp_path):
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    file = tmp_path / "law.txt"
    file.write_text("نص قانون العمل المصري", encoding="utf-8")
    with Session(engine) as db:
        db.add(LibraryAsset(provider="google_drive", external_file_id="f1",
            title="قانون العمل", category="legislation"))
        db.commit()
        preview = stage(db, "f1", file, apply=False)
        assert preview["chunks"] == 1
        assert not db.scalars(select(LibraryTextChunk)).all()
        stage(db, "f1", file, apply=True)
        chunks = db.scalars(select(LibraryTextChunk)).all()
        assert len(chunks) == 1 and not chunks[0].verified
        assert search_verified_library(db, "قانون العمل") == []
        with pytest.raises(ValueError, match="already exist"):
            stage(db, "f1", file, apply=True)
