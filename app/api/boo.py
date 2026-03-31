from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.core.score import get_next_stage
from app.models.user import User
from app.schemas.boo import BooStateResponse

router = APIRouter(prefix="/boo", tags=["boo"])


@router.get("/state", response_model=BooStateResponse)
def boo_state(user: User = Depends(get_current_user)) -> BooStateResponse:
    next_stage, next_threshold = get_next_stage(user.total_score)
    return BooStateResponse(
        boo_stage=user.boo_stage,
        total_score=user.total_score,
        next_stage=next_stage,
        next_threshold=next_threshold,
    )
