"""Additive legal-library catalog models; no production migration or import is run here.

Keep raw source text distinct from reviewed, citable legal material.
"""
from datetime import date
from typing import Optional
from sqlalchemy import Date, ForeignKey, Integer, String, Text, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel


class LibraryAsset(BaseModel):
    __tablename__ = "library_assets"
    __table_args__ = (
        UniqueConstraint("provider", "external_file_id", name="uq_library_asset_provider_file"),
        Index("ix_library_asset_category_status", "category", "review_status"),
    )
    provider: Mapped[str] = mapped_column(String(30), nullable=False, default="google_drive")
    external_file_id: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_external_id: Mapped[Optional[str]] = mapped_column(String(255))
    original_path: Mapped[Optional[str]] = mapped_column(Text)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(String(1200))
    mime_type: Mapped[Optional[str]] = mapped_column(String(150))
    byte_size: Mapped[Optional[int]] = mapped_column(Integer)
    sha256: Mapped[Optional[str]] = mapped_column(String(64))
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="unclassified")
    extraction_status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    review_status: Mapped[str] = mapped_column(String(30), nullable=False, default="unverified")
    rights_status: Mapped[str] = mapped_column(String(30), nullable=False, default="unknown")
    source_document_id: Mapped[Optional[str]] = mapped_column(ForeignKey("documents.id"))


class LibraryTextChunk(BaseModel):
    __tablename__ = "library_text_chunks"
    __table_args__ = (UniqueConstraint("asset_id", "chunk_index", name="uq_library_chunk_index"),)
    asset_id: Mapped[str] = mapped_column(ForeignKey("library_assets.id"), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    page_start: Mapped[Optional[int]] = mapped_column(Integer)
    page_end: Mapped[Optional[int]] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    extraction_method: Mapped[Optional[str]] = mapped_column(String(40))
    verified: Mapped[bool] = mapped_column(default=False, nullable=False)


class LegalCommentary(BaseModel):
    __tablename__ = "legal_commentaries"
    asset_id: Mapped[str] = mapped_column(ForeignKey("library_assets.id"), nullable=False)
    article_id: Mapped[Optional[str]] = mapped_column(ForeignKey("articles.id"))
    judgment_id: Mapped[Optional[str]] = mapped_column(ForeignKey("judgments.id"))
    author: Mapped[Optional[str]] = mapped_column(String(255))
    excerpt: Mapped[str] = mapped_column(Text, nullable=False)
    page_reference: Mapped[Optional[str]] = mapped_column(String(100))
    review_status: Mapped[str] = mapped_column(String(30), default="unverified", nullable=False)


class AppealRecord(BaseModel):
    __tablename__ = "appeal_records"
    judgment_id: Mapped[Optional[str]] = mapped_column(ForeignKey("judgments.id"))
    asset_id: Mapped[Optional[str]] = mapped_column(ForeignKey("library_assets.id"))
    procedure_type: Mapped[str] = mapped_column(String(40), nullable=False)  # appeal/cassation/reconsideration
    filing_number: Mapped[Optional[str]] = mapped_column(String(100))
    filing_year: Mapped[Optional[int]] = mapped_column(Integer)
    filing_date: Mapped[Optional[date]] = mapped_column(Date)
    outcome: Mapped[Optional[str]] = mapped_column(String(100))
    grounds: Mapped[Optional[str]] = mapped_column(Text)
    review_status: Mapped[str] = mapped_column(String(30), default="unverified", nullable=False)


class LegalTemplate(BaseModel):
    __tablename__ = "legal_templates"
    asset_id: Mapped[Optional[str]] = mapped_column(ForeignKey("library_assets.id"))
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    template_type: Mapped[str] = mapped_column(String(60), nullable=False)
    jurisdiction: Mapped[str] = mapped_column(String(80), default="EG", nullable=False)
    body: Mapped[Optional[str]] = mapped_column(Text)
    required_fields_json: Mapped[Optional[str]] = mapped_column(Text)
    instructions: Mapped[Optional[str]] = mapped_column(Text)
    review_status: Mapped[str] = mapped_column(String(30), default="unverified", nullable=False)
