from datetime import datetime
from zoneinfo import ZoneInfo


def _signup_and_token(client, email: str = "meal@hufs.ac.kr") -> str:
    res = client.post("/auth/signup", json={"email": email, "password": "password123"})
    assert res.status_code == 200
    return res.json()["access_token"]


def test_meal_feed_once_per_slot(client, monkeypatch):
    monkeypatch.setattr(
        "app.api.meals.now_kst",
        lambda: datetime(2026, 3, 31, 12, 0, tzinfo=ZoneInfo("Asia/Seoul")),
    )

    token = _signup_and_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    availability = client.get("/meals/availability", headers=headers)
    assert availability.status_code == 200
    payload = availability.json()
    assert payload["meal_slot"] == "LUNCH"
    assert payload["is_available"] is True
    assert len(payload["items"]) >= 1

    meal_item_id = payload["items"][0]["id"]
    feed1 = client.post("/meals/feed", headers=headers, json={"meal_item_id": meal_item_id})
    assert feed1.status_code == 200
    assert feed1.json()["awarded_score"] == 30

    feed2 = client.post("/meals/feed", headers=headers, json={"meal_item_id": meal_item_id})
    assert feed2.status_code == 409


def test_meal_feed_outside_slot_rejected(client, monkeypatch):
    monkeypatch.setattr(
        "app.api.meals.now_kst",
        lambda: datetime(2026, 3, 31, 15, 0, tzinfo=ZoneInfo("Asia/Seoul")),
    )

    token = _signup_and_token(client, "meal2@hufs.ac.kr")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/meals/feed", headers=headers, json={"meal_item_id": 2})
    assert res.status_code == 400
