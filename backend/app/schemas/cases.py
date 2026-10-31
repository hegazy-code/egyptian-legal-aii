from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CaseCreate(BaseModel):
    title: str
    description: Optional[str] = None
    case_type: Optional[str] = None


class CaseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    case_type: Optional[str] = None
    status: Optional[str] = None


class CaseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    case_type: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
