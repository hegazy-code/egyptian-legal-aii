from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class CitationOut(BaseModel):
    source_type: str
    citation_text: Optional[str] = None
    article_id: Optional[str] = None
    judgment_id: Optional[str] = None
    relevance_score: Optional[float] = None


class ChatResponse(BaseModel):
    conversation_id: str
    message_id: str
    answer: str
    citations: List[CitationOut] = []


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
