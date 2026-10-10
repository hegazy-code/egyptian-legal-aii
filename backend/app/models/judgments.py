"""
Judgments and topic/relationship graph models: judgments, courts, legal_topics,
article_topics, judgment_topics, legal_relationships.
"""
from datetime import date
from typing import List, Optional

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Court(BaseModel):
    """A court, e.g. محكمة النقض (Court of Cassation)."""

    __tablename__ = "courts"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # cassation/appeal/first_instance
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    judgments: Mapped[List["Judgment"]] = relationship(back_populates="court")

    def __repr__(self) -> str:
        return f"<Court id={self.id} name={self.name!r}>"


class Judgment(BaseModel):
    """A court judgment/ruling used as precedent."""

    __tablename__ = "judgments"

    court_id: Mapped[Optional[str]] = mapped_column(ForeignKey("courts.id"), nullable=True)
    source_id: Mapped[Optional[str]] = mapped_column(ForeignKey("sources.id"), nullable=True)
    case_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    chamber: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    judgment_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    full_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="published")

    court: Mapped[Optional["Court"]] = relationship(back_populates="judgments")
    source: Mapped[Optional["Source"]] = relationship()
    topics: Mapped[List["JudgmentTopic"]] = relationship(back_populates="judgment", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Judgment id={self.id} case_number={self.case_number!r} year={self.year}>"


class LegalTopic(BaseModel):
    """A legal subject-matter tag (e.g. 'الإيجار', 'الطلاق'), hierarchical."""

    __tablename__ = "legal_topics"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    name_ar: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    parent_topic_id: Mapped[Optional[str]] = mapped_column(ForeignKey("legal_topics.id"), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    parent: Mapped[Optional["LegalTopic"]] = relationship(remote_side="LegalTopic.id")

    def __repr__(self) -> str:
        return f"<LegalTopic id={self.id} name={self.name!r}>"


class ArticleTopic(BaseModel):
    """Association: article <-> legal topic."""

    __tablename__ = "article_topics"

    article_id: Mapped[str] = mapped_column(ForeignKey("articles.id"), nullable=False)
    topic_id: Mapped[str] = mapped_column(ForeignKey("legal_topics.id"), nullable=False)

    article: Mapped["Article"] = relationship()
    topic: Mapped["LegalTopic"] = relationship()

    def __repr__(self) -> str:
        return f"<ArticleTopic article_id={self.article_id} topic_id={self.topic_id}>"


class JudgmentTopic(BaseModel):
    """Association: judgment <-> legal topic."""

    __tablename__ = "judgment_topics"

    judgment_id: Mapped[str] = mapped_column(ForeignKey("judgments.id"), nullable=False)
    topic_id: Mapped[str] = mapped_column(ForeignKey("legal_topics.id"), nullable=False)

    judgment: Mapped["Judgment"] = relationship(back_populates="topics")
    topic: Mapped["LegalTopic"] = relationship()

    def __repr__(self) -> str:
        return f"<JudgmentTopic judgment_id={self.judgment_id} topic_id={self.topic_id}>"


class LegalRelationship(BaseModel):
    """
    Generic typed edge between two legal entities, e.g. a judgment that
    'interprets' an article, or a law that 'repeals' another law.

    source_type/target_type + *_id are a polymorphic reference (not a real
    FK, since the target table varies) into one of: article, law, judgment,
    regulation, ministerial_decision.
    """

    __tablename__ = "legal_relationships"

    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_id: Mapped[str] = mapped_column(String(36), nullable=False)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_id: Mapped[str] = mapped_column(String(36), nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(50), nullable=False)  # cites/amends/interprets/repeals
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<LegalRelationship {self.source_type}:{self.source_id} "
            f"-{self.relationship_type}-> {self.target_type}:{self.target_id}>"
        )
