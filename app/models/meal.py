from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class MealItem(Base):
    __tablename__ = "meal_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    meal_slot: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    score: Mapped[int] = mapped_column(Integer, nullable=False)


class MealFeedLog(Base):
    __tablename__ = "meal_feed_logs"
    __table_args__ = (UniqueConstraint("user_id", "feed_date", "meal_slot", name="uq_meal_feed_user_date_slot"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    meal_item_id: Mapped[int] = mapped_column(ForeignKey("meal_items.id", ondelete="CASCADE"), nullable=False, index=True)
    meal_slot: Mapped[str] = mapped_column(String(32), nullable=False)
    feed_date: Mapped[date] = mapped_column(Date, nullable=False)
    awarded_score: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
