"""Business logic for registration/login and JWT issuance."""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.users import User
from app.repositories.user_repository import UserRepository
from app.security.hashing import hash_password, verify_password
from app.security.jwt import create_access_token


class AuthError(Exception):
    """Raised for user-facing auth failures (bad credentials, duplicate email...)."""


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)

    def register(self, email: str, password: str, full_name: Optional[str] = None) -> User:
        existing = self.users.get_by_email(email)
        if existing:
            raise AuthError("Email already registered.")
        user = User(email=email, hashed_password=hash_password(password), full_name=full_name)
        return self.users.create(user)

    def authenticate(self, email: str, password: str) -> User:
        user = self.users.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise AuthError("Invalid email or password.")
        if not user.is_active:
            raise AuthError("This account is disabled.")
        user.last_login_at = datetime.now(timezone.utc)
        self.db.commit()
        return user

    def issue_token(self, user: User) -> str:
        return create_access_token(subject=user.id, role=user.role)
