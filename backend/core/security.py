"""Security helpers: password hashing and JWT token lifecycle."""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import jwt


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
    return f"pbkdf2_sha256$200000${base64.b64encode(salt).decode()}${base64.b64encode(pwd_hash).decode()}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algo, rounds, salt_b64, hash_b64 = password_hash.split("$", 3)
        if algo != "pbkdf2_sha256":
            return False
        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(hash_b64)
        computed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, int(rounds))
        return hmac.compare_digest(computed, expected)
    except Exception:
        return False


def create_access_token(user_id: int, email: str, secret: str, algorithm: str, exp_minutes: int) -> tuple[str, str, datetime]:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=exp_minutes)
    jti = str(uuid4())
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "email": email,
        "jti": jti,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    return jwt.encode(payload, secret, algorithm=algorithm), jti, exp


def decode_access_token(token: str, secret: str, algorithm: str) -> dict[str, Any]:
    return jwt.decode(token, secret, algorithms=[algorithm])
