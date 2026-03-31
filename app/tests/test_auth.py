def test_auth_signup_login_refresh_logout_flow(client):
    signup_res = client.post(
        "/auth/signup",
        json={"email": "test1@hufs.ac.kr", "password": "password123"},
    )
    assert signup_res.status_code == 200
    signup_data = signup_res.json()
    assert "access_token" in signup_data
    assert "refresh_token" in signup_data

    access_token = signup_data["access_token"]
    me_res = client.get("/users/me", headers={"Authorization": f"Bearer {access_token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "test1@hufs.ac.kr"

    login_res = client.post(
        "/auth/login",
        json={"email": "test1@hufs.ac.kr", "password": "password123"},
    )
    assert login_res.status_code == 200

    refresh_res = client.post("/auth/refresh", json={"refresh_token": login_res.json()["refresh_token"]})
    assert refresh_res.status_code == 200
    rotated_refresh = refresh_res.json()["refresh_token"]

    logout_res = client.post("/auth/logout", json={"refresh_token": rotated_refresh})
    assert logout_res.status_code == 200

    refresh_again_res = client.post("/auth/refresh", json={"refresh_token": rotated_refresh})
    assert refresh_again_res.status_code == 401


def test_invalid_access_token_rejected(client):
    res = client.get("/users/me", headers={"Authorization": "Bearer invalid-token"})
    assert res.status_code == 401
