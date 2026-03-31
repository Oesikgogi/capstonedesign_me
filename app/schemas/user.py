from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserMeResponse(BaseModel):
    id: int
    email: EmailStr
    total_score: int
    boo_stage: str
    created_at: datetime
