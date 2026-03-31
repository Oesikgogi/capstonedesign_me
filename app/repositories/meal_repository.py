from datetime import date

from sqlalchemy.orm import Session

from app.models.meal import MealFeedLog, MealItem


class MealRepository:
    def list_by_slot(self, db: Session, meal_slot: str) -> list[MealItem]:
        return (
            db.query(MealItem)
            .filter(MealItem.meal_slot == meal_slot)
            .order_by(MealItem.id.asc())
            .all()
        )

    def get_item(self, db: Session, meal_item_id: int) -> MealItem | None:
        return db.get(MealItem, meal_item_id)

    def already_fed(self, db: Session, user_id: int, feed_date: date, meal_slot: str) -> bool:
        return (
            db.query(MealFeedLog)
            .filter(
                MealFeedLog.user_id == user_id,
                MealFeedLog.feed_date == feed_date,
                MealFeedLog.meal_slot == meal_slot,
            )
            .first()
            is not None
        )

    def create_feed_log(
        self,
        db: Session,
        user_id: int,
        meal_item_id: int,
        meal_slot: str,
        feed_date: date,
        awarded_score: int,
    ) -> MealFeedLog:
        log = MealFeedLog(
            user_id=user_id,
            meal_item_id=meal_item_id,
            meal_slot=meal_slot,
            feed_date=feed_date,
            awarded_score=awarded_score,
        )
        db.add(log)
        db.flush()
        return log
