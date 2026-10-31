from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class ChatRequest(BaseModel):
    question: str
    conversationId: Optional[str] = None


class SourceCitation(BaseModel):
    id: str = ""
    lawName: str = ""
    articleNumber: Optional[str] = None
    kind: Optional[str] = "other"
    status: str = "current"
    excerpt: Optional[str] = None
    sourceUrl: Optional[str] = None
    basis: Optional[str] = None


class LegalAnswerOut(BaseModel):
    understandingOfQuestion: str = ""
    legalDomain: str = "غير محدد"
    relevantLegalTexts: List[SourceCitation] = []
    explanation: str = ""
    preliminaryApplication: str = ""
    missingInformation: List[str] = []
    possibleProcedures: List[str] = []
    answerSources: List[SourceCitation] = []
    disclaimer: str = (
        "هذه الإجابة لأغراض تعليمية وإرشادية فقط ولا تُغني عن استشارة محامٍ مختص "
        "مرخّص له بمزاولة المهنة."
    )


class CitationOut(BaseModel):
    source_type: str
    citation_text: Optional[str] = None
    article_id: Optional[str] = None
    judgment_id: Optional[str] = None
    relevance_score: Optional[float] = None


class ChatResponse(BaseModel):
    conversationId: Optional[str] = None
    answer: LegalAnswerOut


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    role: str
    content: str
    created_at: datetime


class ConversationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: Optional[str] = None
    status: str
    created_at: datetime
    messages: List[MessageRead] = []


class ConversationListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: Optional[str] = None
    status: str
    created_at: datetime
