"""Thin DB access layer for users/conversations/messages/cases."""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.users import Case, Conversation, Message, User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user


class ConversationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: str, title: Optional[str] = None) -> Conversation:
        conv = Conversation(user_id=user_id, title=title)
        self.db.add(conv)
        self.db.commit()
        self.db.refresh(conv)
        return conv

    def get(self, conversation_id: str) -> Optional[Conversation]:
        return self.db.query(Conversation).filter(Conversation.id == conversation_id).first()

    def list_for_user(self, user_id: str, skip: int = 0, limit: int = 20) -> List[Conversation]:
        return (
            self.db.query(Conversation)
            .filter(Conversation.user_id == user_id)
            .order_by(Conversation.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def add_message(self, conversation_id: str, role: str, content: str) -> Message:
        msg = Message(conversation_id=conversation_id, role=role, content=content)
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg


class CaseRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, case: Case) -> Case:
        self.db.add(case)
        self.db.commit()
        self.db.refresh(case)
        return case

    def get(self, case_id: str) -> Optional[Case]:
        return self.db.query(Case).filter(Case.id == case_id).first()

    def list_for_user(self, user_id: str, skip: int = 0, limit: int = 20) -> List[Case]:
        return (
            self.db.query(Case)
            .filter(Case.user_id == user_id)
            .order_by(Case.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
