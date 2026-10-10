"""
System/infrastructure models: embeddings, search_logs, answer_citations,
evaluation_results, audit_logs.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Embedding(BaseModel):
    """
    Vector embedding for a piece of content (article, judgment, document...).

    TODO: this is a stub. `vector` is stored as a JSON-encoded list of floats
    in a Text column so it works on SQLite today. Once the corpus is large
    enough to justify Postgres, swap this column to `pgvector.sqlalchemy.Vector`
    and migrate DATABASE_URL to Postgres -- no other app code needs to change
    since retrieval goes through app/search/vector.py.
    """

    __tablename__ = "embeddings"

    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)  # article/judgment/document
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    model_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    dimension: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    vector: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # TODO: pgvector.Vector later

    def __repr__(self) -> str:
        return f"<Embedding id={self.id} entity_type={self.entity_type} entity_id={self.entity_id}>"


class SearchLog(BaseModel):
    """Logs every search/query for analytics and evaluation."""

    __tablename__ = "search_logs"

    user_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"), nullable=True)
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    query_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # keyword/exact_reference/hybrid
    results_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    user: Mapped[Optional["User"]] = relationship()

    def __repr__(self) -> str:
        return f"<SearchLog id={self.id} query={self.query_text[:30]!r}>"


class AnswerCitation(BaseModel):
    """Links a chat message's answer to the specific source(s) it cited."""

    __tablename__ = "answer_citations"

    message_id: Mapped[str] = mapped_column(ForeignKey("messages.id"), nullable=False)
    article_id: Mapped[Optional[str]] = mapped_column(ForeignKey("articles.id"), nullable=True)
    judgment_id: Mapped[Optional[str]] = mapped_column(ForeignKey("judgments.id"), nullable=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)  # article/judgment/regulation/...
    citation_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    relevance_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    message: Mapped["Message"] = relationship()
    article: Mapped[Optional["Article"]] = relationship()
    judgment: Mapped[Optional["Judgment"]] = relationship()

    def __repr__(self) -> str:
        return f"<AnswerCitation id={self.id} message_id={self.message_id} source_type={self.source_type}>"


class EvaluationResult(BaseModel):
    """Human or automated evaluation of an answer's quality (for the admin dashboard)."""

    __tablename__ = "evaluation_results"

    message_id: Mapped[Optional[str]] = mapped_column(ForeignKey("messages.id"), nullable=True)
    evaluator: Mapped[str] = mapped_column(String(50), default="auto")  # human/auto
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    criteria: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # e.g. "groundedness"
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    message: Mapped[Optional["Message"]] = relationship()

    def __repr__(self) -> str:
        return f"<EvaluationResult id={self.id} score={self.score}>"


class AuditLog(BaseModel):
    """Tracks admin/user actions for accountability (source edits, reindex triggers, etc.)."""

    __tablename__ = "audit_logs"

    user_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    entity_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON-encoded string
    ip_address: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    user: Mapped[Optional["User"]] = relationship()

    def __repr__(self) -> str:
        return f"<AuditLog id={self.id} action={self.action!r}>"
