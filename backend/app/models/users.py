"""
User-facing models: users, conversations, messages, cases, documents_uploaded.
"""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(20), default="user")  # user/admin
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    conversations: Mapped[List["Conversation"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    cases: Mapped[List["Case"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    documents_uploaded: Mapped[List["DocumentUploaded"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"


class Conversation(BaseModel):
    __tablename__ = "conversations"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active")

    user: Mapped["User"] = relationship(back_populates="conversations")
    messages: Mapped[List["Message"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at"
    )

    def __repr__(self) -> str:
        return f"<Conversation id={self.id} user_id={self.user_id}>"


class Message(BaseModel):
    __tablename__ = "messages"

    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # user/assistant/system
    content: Mapped[str] = mapped_column(Text, nullable=False)

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")

    def __repr__(self) -> str:
        return f"<Message id={self.id} role={self.role} conversation_id={self.conversation_id}>"


class Case(BaseModel):
    """A user's personal legal matter/file (not a court case record)."""

    __tablename__ = "cases"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    case_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="open")  # open/closed/archived

    user: Mapped["User"] = relationship(back_populates="cases")
    documents_uploaded: Mapped[List["DocumentUploaded"]] = relationship(back_populates="case")

    def __repr__(self) -> str:
        return f"<Case id={self.id} title={self.title!r} status={self.status}>"


class DocumentUploaded(BaseModel):
    """A file a user uploaded (evidence, contract, etc.) -- OCR/analysis is a TODO stub."""

    __tablename__ = "documents_uploaded"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    case_id: Mapped[Optional[str]] = mapped_column(ForeignKey("cases.id"), nullable=True)
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ocr_status: Mapped[str] = mapped_column(String(30), default="pending")  # pending/processing/done/failed/not_applicable
    extracted_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship(back_populates="documents_uploaded")
    case: Mapped[Optional["Case"]] = relationship(back_populates="documents_uploaded")

    def __repr__(self) -> str:
        return f"<DocumentUploaded id={self.id} filename={self.filename!r} status={self.ocr_status}>"
