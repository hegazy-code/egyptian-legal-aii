"""POST /chat, GET /conversations, GET /conversations/{id}."""
import secrets
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models.users import User
from app.repositories.user_repository import ConversationRepository, UserRepository
from app.security.hashing import hash_password
from app.schemas.chat import ChatRequest, ChatResponse, CitationOut, ConversationListItem, ConversationRead
from app.services.chat_service import ChatService

router = APIRouter(tags=["chat"])

_optional_bearer = HTTPBearer(auto_error=False)
GUEST_EMAIL = "guest@legal-ai.local"


def get_user_or_guest(
    credentials: HTTPAuthorizationCredentials = Depends(_optional_bearer),
    db: Session = Depends(get_db),
) -> User:
    """Logged-in users keep their own history; anonymous visitors share a guest account
    (it has a random password, so nobody can log in as it)."""
    if credentials is not None:
        return get_current_user(credentials=credentials, db=db)
    repo = UserRepository(db)
    guest = repo.get_by_email(GUEST_EMAIL)
    if guest is None:
        guest = repo.create(
            User(email=GUEST_EMAIL, hashed_password=hash_password(secrets.token_urlsafe(32)), full_name="Guest", role="guest")
        )
    return guest


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db), current_user: User = Depends(get_user_or_guest)):
    service = ChatService(db)
    conversation, assistant_message, search_results = service.ask(
        user_id=current_user.id, message=payload.message, conversation_id=payload.conversation_id
    )
    citations = [
        CitationOut(
            source_type=r.result_type,
            citation_text=r.title,
            article_id=r.id if r.result_type == "article" else None,
            judgment_id=r.id if r.result_type == "judgment" else None,
            relevance_score=r.score,
        )
        for r in search_results[:5]
    ]
    return ChatResponse(
        conversation_id=conversation.id,
        message_id=assistant_message.id,
        answer=assistant_message.content,
        citations=citations,
    )


@router.get("/conversations", response_model=List[ConversationListItem])
def list_conversations(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = ConversationRepository(db)
    return repo.list_for_user(current_user.id, skip=skip, limit=limit)


@router.get("/conversations/{conversation_id}", response_model=ConversationRead)
def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = ConversationRepository(db)
    conversation = repo.get(conversation_id)
    if not conversation or conversation.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return conversation
