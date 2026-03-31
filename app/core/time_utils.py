from datetime import datetime
from zoneinfo import ZoneInfo

from app.core.config import settings


MEAL_SLOT_BREAKFAST = "BREAKFAST"
MEAL_SLOT_LUNCH = "LUNCH"
MEAL_SLOT_DINNER = "DINNER"


def now_kst() -> datetime:
    return datetime.now(ZoneInfo(settings.timezone))


def get_meal_slot(target: datetime | None = None) -> str | None:
    dt = target or now_kst()
    hour = dt.hour

    if settings.breakfast_start_hour <= hour < settings.breakfast_end_hour:
        return MEAL_SLOT_BREAKFAST
    if settings.lunch_start_hour <= hour < settings.lunch_end_hour:
        return MEAL_SLOT_LUNCH
    if settings.dinner_start_hour <= hour < settings.dinner_end_hour:
        return MEAL_SLOT_DINNER
    return None
