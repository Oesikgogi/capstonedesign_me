import json
from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.quiz import QuizAttempt, QuizQuestion, QuizReward


class QuizRepository:
    def list_questions(self, db: Session) -> list[QuizQuestion]:
        return db.query(QuizQuestion).order_by(QuizQuestion.id.asc()).all()

    def get_question(self, db: Session, question_id: int) -> QuizQuestion | None:
        return db.get(QuizQuestion, question_id)

    def parse_choices(self, question: QuizQuestion) -> list[str]:
        return json.loads(question.choices_json)

    def record_attempt(
        self,
        db: Session,
        user_id: int,
        question_id: int,
        selected_index: int,
        is_correct: bool,
    ) -> QuizAttempt:
        attempt = QuizAttempt(
            user_id=user_id,
            question_id=question_id,
            selected_index=selected_index,
            is_correct=is_correct,
            attempted_at=datetime.now(timezone.utc),
        )
        db.add(attempt)
        db.flush()
        return attempt

    def award_once(self, db: Session, user_id: int, question_id: int, score: int) -> bool:
        reward = QuizReward(user_id=user_id, question_id=question_id, awarded_score=score)
        try:
            with db.begin_nested():
                db.add(reward)
                db.flush()
            return True
        except IntegrityError:
            return False
