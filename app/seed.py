import json

from sqlalchemy.orm import Session

from app.core.constants import MEAL_DEFAULT_SCORE, QUIZ_DEFAULT_SCORE
from app.core.time_utils import MEAL_SLOT_BREAKFAST, MEAL_SLOT_DINNER, MEAL_SLOT_LUNCH
from app.models.meal import MealItem
from app.models.quiz import QuizQuestion


QUIZ_SEEDS = [
    {
        "question_text": "한국외대 서울캠퍼스의 상징 동물은 무엇인가요?",
        "choices": ["호랑이", "부엉이", "독수리", "고양이"],
        "correct_index": 1,
        "score": QUIZ_DEFAULT_SCORE,
    },
    {
        "question_text": "한국외대 축제명으로 올바른 것은 무엇인가요?",
        "choices": ["대동제", "HUFS Festival", "외대문화제", "스프링팝"],
        "correct_index": 0,
        "score": QUIZ_DEFAULT_SCORE,
    },
    {
        "question_text": "한국외대의 공식 약어는 무엇인가요?",
        "choices": ["KU", "HUFS", "SNU", "KHU"],
        "correct_index": 1,
        "score": QUIZ_DEFAULT_SCORE,
    },
]

MEAL_SEEDS = [
    {"name": "토스트 세트", "meal_slot": MEAL_SLOT_BREAKFAST, "score": MEAL_DEFAULT_SCORE},
    {"name": "상추불고기비빔밥", "meal_slot": MEAL_SLOT_LUNCH, "score": MEAL_DEFAULT_SCORE},
    {"name": "치킨마요덮밥", "meal_slot": MEAL_SLOT_DINNER, "score": MEAL_DEFAULT_SCORE},
]


def seed_initial_data(db: Session) -> None:
    question_exists = db.query(QuizQuestion).first()
    if question_exists is None:
        for item in QUIZ_SEEDS:
            db.add(
                QuizQuestion(
                    question_text=item["question_text"],
                    choices_json=json.dumps(item["choices"], ensure_ascii=False),
                    correct_index=item["correct_index"],
                    score=item["score"],
                )
            )

    meal_exists = db.query(MealItem).first()
    if meal_exists is None:
        for item in MEAL_SEEDS:
            db.add(MealItem(name=item["name"], meal_slot=item["meal_slot"], score=item["score"]))

    db.commit()
