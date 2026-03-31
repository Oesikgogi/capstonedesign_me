from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.repositories.quiz_repository import QuizRepository
from app.repositories.user_repository import UserRepository
from app.schemas.quiz import QuizQuestionResponse, QuizSubmitRequest, QuizSubmitResponse

router = APIRouter(prefix="/quiz", tags=["quiz"])
quiz_repo = QuizRepository()
user_repo = UserRepository()


@router.get("/questions", response_model=list[QuizQuestionResponse])
def list_questions(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[QuizQuestionResponse]:
    questions = quiz_repo.list_questions(db)
    return [
        QuizQuestionResponse(
            id=q.id,
            question_text=q.question_text,
            choices=quiz_repo.parse_choices(q),
        )
        for q in questions
    ]


@router.post("/submit", response_model=QuizSubmitResponse)
def submit_quiz(
    payload: QuizSubmitRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> QuizSubmitResponse:
    question = quiz_repo.get_question(db, payload.question_id)
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    choices = quiz_repo.parse_choices(question)
    if payload.selected_index >= len(choices):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Selected index out of range")

    is_correct = payload.selected_index == question.correct_index
    quiz_repo.record_attempt(
        db,
        user_id=user.id,
        question_id=question.id,
        selected_index=payload.selected_index,
        is_correct=is_correct,
    )

    awarded_score = 0
    message = "Wrong answer"

    if is_correct:
        awarded = quiz_repo.award_once(db, user.id, question.id, question.score)
        if awarded:
            updated_user = user_repo.add_score(db, user.id, question.score)
            awarded_score = question.score
            message = "Correct answer! score awarded"
            db.commit()
            return QuizSubmitResponse(
                is_correct=True,
                awarded_score=awarded_score,
                total_score=updated_user.total_score,
                boo_stage=updated_user.boo_stage,
                message=message,
            )

        message = "Correct, but score already awarded for this question"

    db.commit()
    refreshed_user = user_repo.get_by_id(db, user.id)
    if refreshed_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return QuizSubmitResponse(
        is_correct=is_correct,
        awarded_score=awarded_score,
        total_score=refreshed_user.total_score,
        boo_stage=refreshed_user.boo_stage,
        message=message,
    )
