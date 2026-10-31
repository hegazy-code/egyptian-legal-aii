"""POST /chat, GET /conversations, GET /conversations/{id}."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.users import User
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    CitationOut,
    ConversationListItem,
    ConversationRead,
    LegalAnswerOut,
)
from app.services.chat_service import ChatService

router = APIRouter(tags=["chat"])

# ---------------------------------------------------------------------------
# Guest user support
# A locked system account is created on first use so anonymous /chat requests
# satisfy the Conversation.user_id FK without needing a real login.
# ---------------------------------------------------------------------------
_GUEST_EMAIL = "guest@system.local"


def _get_guest_user_id(db: Session) -> str:
    """Return the ID of the system guest user, creating it on first call."""
    user = db.query(User).filter(User.email == _GUEST_EMAIL).first()
    if user:
        return user.id
    guest = User(
        email=_GUEST_EMAIL,
        hashed_password="!",   # unusable password -- bcrypt never produces "!"
        full_name="مستخدم ضيف",
        role="user",
        is_active=True,
    )
    db.add(guest)
    db.commit()
    db.refresh(guest)
    return guest.id


# ---------------------------------------------------------------------------
# NOTE: JWT auth is intentionally NOT required on POST /chat while the
# frontend auth flow is being built. The conversations endpoints retain auth
# because they expose per-user history.
# Re-add `current_user: User = Depends(get_current_user)` to chat() and pass
# current_user.id to service.ask() once the frontend login is wired up.
# ---------------------------------------------------------------------------


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    guest_id = _get_guest_user_id(db)
    service = ChatService(db)

    conversation, assistant_message, search_results, answer_dict = service.ask(
        user_id=guest_id,
        question=payload.question,
        conversation_id=payload.conversationId,
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
        conversationId=conversation.id,
        messageId=assistant_message.id,
        answer=LegalAnswerOut(**answer_dict),
        citations=citations,
    )


# ---------------------------------------------------------------------------
# Conversation history endpoints (keep auth on these).
# ---------------------------------------------------------------------------
from app.api.deps import get_current_user          # noqa: E402
from app.repositories.user_repository import ConversationRepository  # noqa: E402


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
