from pydantic import BaseModel


class MealItemResponse(BaseModel):
    id: int
    name: str
    meal_slot: str
    score: int


class MealAvailabilityResponse(BaseModel):
    meal_slot: str | None
    is_available: bool
    already_fed: bool
    items: list[MealItemResponse]
    message: str


class MealFeedRequest(BaseModel):
    meal_item_id: int


class MealFeedResponse(BaseModel):
    awarded_score: int
    total_score: int
    boo_stage: str
    message: str
