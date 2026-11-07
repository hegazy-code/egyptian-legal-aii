"""Immutable-by-application review evidence for judicial decisions.

The table is admin-only and is never exposed to public search. A reviewer
assertion is NOT equivalent to independent authentication of a judgment.
"""
from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel


class JudgmentEvidence(BaseModel):
    __tablename__ = "judgment_evidence"

    judgment_id: Mapped[str] = mapped_column(ForeignKey("judgments.id"), nullable=False, index=True)
    reviewer_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    source_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    independent_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    text_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    source_excerpt: Mapped[str] = mapped_column(Text, nullable=False)
    independent_excerpt: Mapped[str] = mapped_column(Text, nullable=False)
    review_reason: Mapped[str] = mapped_column(Text, nullable=False)
    primary_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    independent_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    primary_fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    independent_fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    verification_outcome: Mapped[str] = mapped_column(String(30), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
