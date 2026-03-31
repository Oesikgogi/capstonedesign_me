from app.core.constants import BooStage
from app.repositories.user_repository import UserRepository


def _signup_and_token(client, email: str = "quiz@hufs.ac.kr") -> str:
    res = client.post("/auth/signup", json={"email": email, "password": "password123"})
    assert res.status_code == 200
    return res.json()["access_token"]


def test_quiz_first_correct_awarded_once(client):
    token = _signup_and_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    questions_res = client.get("/quiz/questions", headers=headers)
    assert questions_res.status_code == 200
    questions = questions_res.json()
    assert len(questions) >= 1

    first_question_id = questions[0]["id"]

    submit1 = client.post(
        "/quiz/submit",
        headers=headers,
        json={"question_id": first_question_id, "selected_index": 1},
    )
    assert submit1.status_code == 200
    assert submit1.json()["is_correct"] is True
    assert submit1.json()["awarded_score"] == 50
    assert submit1.json()["total_score"] == 50

    submit2 = client.post(
        "/quiz/submit",
        headers=headers,
        json={"question_id": first_question_id, "selected_index": 1},
    )
    assert submit2.status_code == 200
    assert submit2.json()["is_correct"] is True
    assert submit2.json()["awarded_score"] == 0
    assert submit2.json()["total_score"] == 50


def test_boo_stage_boundaries(test_session_factory):
    session = test_session_factory()
    try:
        signup = {
            "email": "stage@hufs.ac.kr",
            "password_hash": "hashed",
            "total_score": 299,
            "boo_stage": BooStage.BABY,
        }

        from app.models.user import User

        user = User(**signup)
        session.add(user)
        session.commit()

        repo = UserRepository()
        updated = repo.add_score(session, user.id, 1)
        session.commit()
        assert updated.total_score == 300
        assert updated.boo_stage == BooStage.JACKET

        updated.total_score = 799
        updated.boo_stage = BooStage.JACKET
        session.commit()

        updated2 = repo.add_score(session, user.id, 1)
        session.commit()
        assert updated2.total_score == 800
        assert updated2.boo_stage == BooStage.GRADUATE
    finally:
        session.close()
