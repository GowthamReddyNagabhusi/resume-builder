from __future__ import annotations


def test_signup_success(client):
    res = client.post("/api/auth/signup", json={"name": "Alice", "email": "alice@example.com", "password": "password123"})
    assert res.status_code == 200
    assert res.json()["success"] is True


def test_signup_duplicate_email(client):
    body = {"name": "Bob", "email": "bob@example.com", "password": "password123"}
    assert client.post("/api/auth/signup", json=body).status_code == 200
    res = client.post("/api/auth/signup", json=body)
    assert res.status_code == 409


def test_signup_short_password_422(client):
    res = client.post("/api/auth/signup", json={"name": "Tiny", "email": "tiny@example.com", "password": "123"})
    assert res.status_code == 422


def test_login_success(client):
    client.post("/api/auth/signup", json={"name": "Login User", "email": "login@example.com", "password": "password123"})
    res = client.post("/api/auth/login", json={"email": "login@example.com", "password": "password123"})
    assert res.status_code == 200
    assert res.json()["success"] is True


def test_login_wrong_password(client):
    client.post("/api/auth/signup", json={"name": "Wrong Pass", "email": "wrong@example.com", "password": "password123"})
    res = client.post("/api/auth/login", json={"email": "wrong@example.com", "password": "badpass123"})
    assert res.status_code == 401


def test_login_unknown_email(client):
    res = client.post("/api/auth/login", json={"email": "missing@example.com", "password": "password123"})
    assert res.status_code == 401


def test_me_with_and_without_token(client, auth_headers):
    ok = client.get("/api/auth/me", headers=auth_headers)
    assert ok.status_code == 200
    client.cookies.clear()
    no = client.get("/api/auth/me")
    assert no.status_code == 401


def test_logout_invalidates_session(client, auth_headers):
    me1 = client.get("/api/auth/me", headers=auth_headers)
    assert me1.status_code == 200
    out = client.post("/api/auth/logout", headers=auth_headers)
    assert out.status_code == 200
    me2 = client.get("/api/auth/me", headers=auth_headers)
    assert me2.status_code == 401


def test_refresh_returns_new_token(client, auth_headers):
    res = client.post("/api/auth/refresh", headers=auth_headers)
    assert res.status_code == 200
    payload = res.json()
    assert payload["success"] is True
    assert payload.get("access_token")
