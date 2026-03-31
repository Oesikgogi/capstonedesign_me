from pydantic import BaseModel


class BooStateResponse(BaseModel):
    boo_stage: str
    total_score: int
    next_stage: str | None
    next_threshold: int | None
