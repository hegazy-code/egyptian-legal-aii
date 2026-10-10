"""
Import Base and every model here so Alembic autogenerate (and SQLAlchemy's
mapper configuration in general) can see the full schema.
"""
from app.models.base import Base  # noqa: F401

# legal.py
from app.models.legal import (  # noqa: F401
    Source,
    Document,
    Law,
    LawVersion,
    Article,
    ArticleVersion,
    Amendment,
    Regulation,
    MinisterialDecision,
)

# judgments.py
from app.models.judgments import (  # noqa: F401
    Court,
    Judgment,
    LegalTopic,
    ArticleTopic,
    JudgmentTopic,
    LegalRelationship,
)

# users.py
from app.models.users import (  # noqa: F401
    User,
    Conversation,
    Message,
    Case,
    DocumentUploaded,
)

# system.py
from app.models.system import (  # noqa: F401
    Embedding,
    SearchLog,
    AnswerCitation,
    EvaluationResult,
    AuditLog,
)

__all__ = [
    "Base",
    "Source",
    "Document",
    "Law",
    "LawVersion",
    "Article",
    "ArticleVersion",
    "Amendment",
    "Regulation",
    "MinisterialDecision",
    "Court",
    "Judgment",
    "LegalTopic",
    "ArticleTopic",
    "JudgmentTopic",
    "LegalRelationship",
    "User",
    "Conversation",
    "Message",
    "Case",
    "DocumentUploaded",
    "Embedding",
    "SearchLog",
    "AnswerCitation",
    "EvaluationResult",
    "AuditLog",
]
