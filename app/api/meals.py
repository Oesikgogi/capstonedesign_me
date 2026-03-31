from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.time_utils import get_meal_slot, now_kst
from app.models.user import User
from app.repositories.meal_repository import MealRepository
from app.repositories.user_repository import UserRepository
from app.schemas.meal import (
    MealAvailabilityResponse,
    MealFeedRequest,
    MealFeedResponse,
    MealItemResponse,
)

router = APIRouter(prefix="/meals", tags=["meals"])
meal_repo = MealRepository()
user_repo = UserRepository()


@router.get("/availability", response_model=MealAvailabilityResponse)
def meal_availability(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MealAvailabilityResponse:
    current = now_kst()
    meal_slot = get_meal_slot(current)

    if meal_slot is None:
        return MealAvailabilityResponse(
            meal_slot=None,
            is_available=False,
            already_fed=False,
            items=[],
            message="Meal feeding is only available during meal time slots",
        )

    feed_date = current.date()
    already_fed = meal_repo.already_fed(db, user.id, feed_date, meal_slot)
    items = meal_repo.list_by_slot(db, meal_slot)

    return MealAvailabilityResponse(
        meal_slot=meal_slot,
        is_available=(not already_fed) and len(items) > 0,
        already_fed=already_fed,
        items=[MealItemResponse(id=i.id, name=i.name, meal_slot=i.meal_slot, score=i.score) for i in items],
        message="Available" if not already_fed else "Already fed in this slot",
    )


@router.post("/feed", response_model=MealFeedResponse)
def feed_meal(
    payload: MealFeedRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MealFeedResponse:
    current = now_kst()
    meal_slot = get_meal_slot(current)
    if meal_slot is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not in meal time slot")

    feed_date = current.date()
    if meal_repo.already_fed(db, user.id, feed_date, meal_slot):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already fed during this slot")

    item = meal_repo.get_item(db, payload.meal_item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal item not found")
    if item.meal_slot != meal_slot:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Meal item not available in current slot")

    try:
        meal_repo.create_feed_log(
            db,
            user_id=user.id,
            meal_item_id=item.id,
            meal_slot=meal_slot,
            feed_date=feed_date,
            awarded_score=item.score,
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already fed during this slot")

    updated_user = user_repo.add_score(db, user.id, item.score)
    db.commit()

    return MealFeedResponse(
        awarded_score=item.score,
        total_score=updated_user.total_score,
        boo_stage=updated_user.boo_stage,
        message="Meal fed successfully",
    )
