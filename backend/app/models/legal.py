"""
Core legal corpus models: sources, documents, laws, law_versions, articles,
article_versions, amendments, regulations, ministerial_decisions.
"""
from datetime import date
from typing import List, Optional

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Source(BaseModel):
    """Where a piece of legal content came from (gazette, official site, upload...)."""

    __tablename__ = "sources"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, default="official")
    url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    publisher: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    reliability_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    documents: Mapped[List["Document"]] = relationship(back_populates="source")

    def __repr__(self) -> str:
        return f"<Source id={self.id} name={self.name!r}>"


class Document(BaseModel):
    """A raw ingested document (PDF/HTML/etc.) before/after structuring into laws/judgments."""

    __tablename__ = "documents"

    source_id: Mapped[Optional[str]] = mapped_column(ForeignKey("sources.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    document_type: Mapped[str] = mapped_column(String(50), nullable=False, default="law")
    file_path: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    raw_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="ar")
    published_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="pending")  # pending/processed/failed

    source: Mapped[Optional["Source"]] = relationship(back_populates="documents")
    laws: Mapped[List["Law"]] = relationship(back_populates="document")

    def __repr__(self) -> str:
        return f"<Document id={self.id} title={self.title!r} status={self.status}>"


class Law(BaseModel):
    """A named law/statute, e.g. 'قانون العقوبات رقم 58 لسنة 1937'."""

    __tablename__ = "laws"

    document_id: Mapped[Optional[str]] = mapped_column(ForeignKey("documents.id"), nullable=True)
    source_id: Mapped[Optional[str]] = mapped_column(ForeignKey("sources.id"), nullable=True)
    law_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # e.g. civil, criminal
    status: Mapped[str] = mapped_column(String(30), default="active")  # active/repealed/amended
    issued_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    document: Mapped[Optional["Document"]] = relationship(back_populates="laws")
    source: Mapped[Optional["Source"]] = relationship()
    versions: Mapped[List["LawVersion"]] = relationship(back_populates="law", cascade="all, delete-orphan")
    articles: Mapped[List["Article"]] = relationship(back_populates="law", cascade="all, delete-orphan")
    regulations: Mapped[List["Regulation"]] = relationship(back_populates="law")

    def __repr__(self) -> str:
        return f"<Law id={self.id} number={self.law_number} title={self.title!r}>"


class LawVersion(BaseModel):
    """A point-in-time snapshot of a law's full text (tracks amendments over time)."""

    __tablename__ = "law_versions"

    law_id: Mapped[str] = mapped_column(ForeignKey("laws.id"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, default=1)
    effective_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    change_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    full_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    law: Mapped["Law"] = relationship(back_populates="versions")

    def __repr__(self) -> str:
        return f"<LawVersion id={self.id} law_id={self.law_id} v={self.version_number}>"


class Article(BaseModel):
    """A single article ('مادة') within a law -- the primary retrieval/citation unit."""

    __tablename__ = "articles"

    law_id: Mapped[str] = mapped_column(ForeignKey("laws.id"), nullable=False)
    article_number: Mapped[str] = mapped_column(String(50), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    chapter: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    section: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    order_index: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="active")  # active/repealed/amended

    law: Mapped["Law"] = relationship(back_populates="articles")
    versions: Mapped[List["ArticleVersion"]] = relationship(
        back_populates="article", cascade="all, delete-orphan"
    )
    amendments: Mapped[List["Amendment"]] = relationship(back_populates="article")

    def __repr__(self) -> str:
        return f"<Article id={self.id} law_id={self.law_id} number={self.article_number!r}>"


class ArticleVersion(BaseModel):
    """A point-in-time snapshot of a single article's text."""

    __tablename__ = "article_versions"

    article_id: Mapped[str] = mapped_column(ForeignKey("articles.id"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, default=1)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    effective_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    change_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    article: Mapped["Article"] = relationship(back_populates="versions")

    def __repr__(self) -> str:
        return f"<ArticleVersion id={self.id} article_id={self.article_id} v={self.version_number}>"


class Amendment(BaseModel):
    """Records that a law/article was amended by another law, with effective date."""

    __tablename__ = "amendments"

    article_id: Mapped[Optional[str]] = mapped_column(ForeignKey("articles.id"), nullable=True)
    law_id: Mapped[Optional[str]] = mapped_column(ForeignKey("laws.id"), nullable=True)
    amending_law_id: Mapped[Optional[str]] = mapped_column(ForeignKey("laws.id"), nullable=True)
    amendment_type: Mapped[str] = mapped_column(String(30), default="modification")  # modification/repeal/addition
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    effective_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    article: Mapped[Optional["Article"]] = relationship(back_populates="amendments", foreign_keys=[article_id])
    law: Mapped[Optional["Law"]] = relationship(foreign_keys=[law_id])
    amending_law: Mapped[Optional["Law"]] = relationship(foreign_keys=[amending_law_id])

    def __repr__(self) -> str:
        return f"<Amendment id={self.id} type={self.amendment_type}>"


class Regulation(BaseModel):
    """Executive regulation ('اللائحة التنفيذية') attached to a law."""

    __tablename__ = "regulations"

    law_id: Mapped[Optional[str]] = mapped_column(ForeignKey("laws.id"), nullable=True)
    source_id: Mapped[Optional[str]] = mapped_column(ForeignKey("sources.id"), nullable=True)
    regulation_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    issued_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    law: Mapped[Optional["Law"]] = relationship(back_populates="regulations")
    source: Mapped[Optional["Source"]] = relationship()

    def __repr__(self) -> str:
        return f"<Regulation id={self.id} title={self.title!r}>"


class MinisterialDecision(BaseModel):
    """A ministerial decree/decision ('قرار وزاري'), optionally tied to a law."""

    __tablename__ = "ministerial_decisions"

    related_law_id: Mapped[Optional[str]] = mapped_column(ForeignKey("laws.id"), nullable=True)
    source_id: Mapped[Optional[str]] = mapped_column(ForeignKey("sources.id"), nullable=True)
    decision_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    ministry: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    issued_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    related_law: Mapped[Optional["Law"]] = relationship()
    source: Mapped[Optional["Source"]] = relationship()

    def __repr__(self) -> str:
        return f"<MinisterialDecision id={self.id} title={self.title!r}>"
