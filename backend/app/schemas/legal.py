from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class SourceCreate(BaseModel):
    name: str
    source_type: str = "official"
    url: Optional[str] = None
    publisher: Optional[str] = None
    notes: Optional[str] = None


class SourceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    source_type: str
    url: Optional[str] = None
    publisher: Optional[str] = None
    created_at: datetime


class ArticleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    law_id: str
    article_number: str
    text: str
    chapter: Optional[str] = None
    section: Optional[str] = None
    status: str


class LawRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    law_number: Optional[str] = None
    title: str
    year: Optional[int] = None
    category: Optional[str] = None
    status: str
    issued_date: Optional[date] = None


class LawDetailRead(LawRead):
    articles: List[ArticleRead] = []


class SearchRequest(BaseModel):
    query: str
    limit: int = 10


class SearchResultItem(BaseModel):
    result_type: str  # "article" | "judgment"
    id: str
    title: str
    snippet: str
    score: float = 0.0


class SearchResponse(BaseModel):
    query: str
    total: int
    results: List[SearchResultItem]
