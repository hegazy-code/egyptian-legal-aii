"""
Declarative base and common mixins shared by all ORM models.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_uuid() -> str:
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    """Shared declarative base for all models (imported by Alembic env.py)."""
    pass


class IDMixin:
    """UUID primary key stored as a string (portable across SQLite/Postgres)."""

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=new_uuid, index=True
    )


class TimestampMixin:
    """created_at / updated_at columns maintained automatically."""

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )


class BaseModel(IDMixin, TimestampMixin, Base):
    """Convenience combined base: id + created_at + updated_at."""
    __abstract__ = True
