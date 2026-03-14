from __future__ import annotations

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("JWT_SECRET", "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("JWT_EXP_MINUTES", "120")
os.environ.setdefault("TESTING", "true")

from backend.main import app  # noqa: E402
from backend.database import models as db  # noqa: E402


@pytest.fixture
def test_db(tmp_path: Path):
    db.DB_PATH = tmp_path / "career_test.db"
    db.init_db()
    yield db.DB_PATH


@pytest.fixture
def client(test_db):
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_headers(client):
    email = "test.user@example.com"
    client.post("/api/auth/signup", json={"name": "Test User", "email": email, "password": "password123"})
    login = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    token = login.json().get("access_token", "")
    return {"Authorization": f"Bearer {token}"}
