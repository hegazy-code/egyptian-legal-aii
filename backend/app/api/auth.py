"""POST /auth/register, /auth/login, /auth/logout -- real JWT + bcrypt auth."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models.users import User
from app.schemas.auth import Token, UserCreate, UserLogin, UserRead
from app.services.auth_service import AuthError, AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    service = AuthService(db)
    try:
        user = service.register(payload.email, payload.password, payload.full_name)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return user


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    service = AuthService(db)
    try:
        user = service.authenticate(payload.email, payload.password)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    token = service.issue_token(user)
    return Token(access_token=token)


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    # JWTs are stateless here; logout is a client-side token discard.
    # TODO: swap in a server-side token blocklist (e.g. Redis) if immediate
    # server-side revocation is required.
    return {"detail": "Logged out successfully."}
