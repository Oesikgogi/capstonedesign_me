from sqlalchemy import update
from sqlalchemy.orm import Session

from app.core.score import get_boo_stage
from app.models.user import User


class UserRepository:
    def get_by_email(self, db: Session, email: str) -> User | None:
        return db.query(User).filter(User.email == email).first()

    def get_by_id(self, db: Session, user_id: int) -> User | None:
        return db.get(User, user_id)

    def create(self, db: Session, email: str, password_hash: str) -> User:
        user = User(email=email, password_hash=password_hash)
        db.add(user)
        db.flush()
        return user

    def add_score(self, db: Session, user_id: int, delta: int) -> User:
        db.execute(update(User).where(User.id == user_id).values(total_score=User.total_score + delta))
        db.flush()

        user = db.get(User, user_id)
        if user is None:
            raise ValueError("User not found")

        stage = get_boo_stage(user.total_score)
        if user.boo_stage != stage:
            user.boo_stage = stage
            db.flush()

        return user
