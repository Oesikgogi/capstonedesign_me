from pydantic import BaseModel, Field


class QuizQuestionResponse(BaseModel):
    id: int
    question_text: str
    choices: list[str]


class QuizSubmitRequest(BaseModel):
    question_id: int
    selected_index: int = Field(ge=0)


class QuizSubmitResponse(BaseModel):
    is_correct: bool
    awarded_score: int
    total_score: int
    boo_stage: str
    message: str
