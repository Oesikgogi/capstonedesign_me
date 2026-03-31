from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    TokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    hash_token,
    verify_password,
)
from app.models.user import User
from app.repositories.token_repository import TokenRepository
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self) -> None:
        self.user_repo = UserRepository()
        self.token_repo = TokenRepository()

    def signup(self, db: Session, email: str, password: str) -> tuple[str, str, User]:
        existing = self.user_repo.get_by_email(db, email)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

        user = self.user_repo.create(db, email=email, password_hash=get_password_hash(password))
        access_token, _ = create_access_token(str(user.id))
        refresh_token, refresh_expires = create_refresh_token(str(user.id))

        self.token_repo.create(
            db,
            user_id=user.id,
            token_hash=hash_token(refresh_token),
            expires_at=refresh_expires,
        )
        return access_token, refresh_token, user

    def login(self, db: Session, email: str, password: str) -> tuple[str, str, User]:
        user = self.user_repo.get_by_email(db, email)
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        access_token, _ = create_access_token(str(user.id))
        refresh_token, refresh_expires = create_refresh_token(str(user.id))
        self.token_repo.create(
            db,
            user_id=user.id,
            token_hash=hash_token(refresh_token),
            expires_at=refresh_expires,
        )
        return access_token, refresh_token, user

    def refresh(self, db: Session, refresh_token: str) -> tuple[str, str, User]:
        try:
            payload = decode_token(refresh_token, expected_type="refresh")
        except TokenError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        token_hash = hash_token(refresh_token)
        token_row = self.token_repo.get_by_hash(db, token_hash)
        if token_row is None or not self.token_repo.is_active(token_row):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is not active")

        sub = payload.get("sub")
        if sub is None or str(token_row.user_id) != str(sub):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token subject mismatch")

        user = self.user_repo.get_by_id(db, token_row.user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        self.token_repo.revoke(db, token_row)

        access_token, _ = create_access_token(str(user.id))
        new_refresh_token, new_refresh_expires = create_refresh_token(str(user.id))
        self.token_repo.create(
            db,
            user_id=user.id,
            token_hash=hash_token(new_refresh_token),
            expires_at=new_refresh_expires,
        )
        return access_token, new_refresh_token, user

    def logout(self, db: Session, refresh_token: str) -> None:
        try:
            decode_token(refresh_token, expected_type="refresh")
        except TokenError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        token_row = self.token_repo.get_by_hash(db, hash_token(refresh_token))
        if token_row is None or not self.token_repo.is_active(token_row):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is not active")

        self.token_repo.revoke(db, token_row)
