from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken


class TokenRepository:
    def create(self, db: Session, user_id: int, token_hash: str, expires_at: datetime) -> RefreshToken:
        token = RefreshToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
        db.add(token)
        db.flush()
        return token

    def get_by_hash(self, db: Session, token_hash: str) -> RefreshToken | None:
        return db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()

    def revoke(self, db: Session, token: RefreshToken) -> None:
        token.revoked_at = datetime.now(timezone.utc)
        db.flush()

    def is_active(self, token: RefreshToken) -> bool:
        if token.revoked_at is not None:
            return False

        expires_at = token.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        return expires_at > datetime.now(timezone.utc)
