from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
import pytest

from backend.core.security import decode_access_token, hash_password, verify_password


def test_hash_password_not_plaintext():
    plain = "password123"
    hashed = hash_password(plain)
    assert hashed != plain


def test_verify_password_true():
    plain = "password123"
    assert verify_password(plain, hash_password(plain)) is True


def test_verify_password_false():
    assert verify_password("wrong", hash_password("correct")) is False


def test_decode_expired_token_raises():
    secret = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
    token = jwt.encode(
        {
            "sub": "1",
            "email": "a@b.com",
            "jti": "expired-jti",
            "iat": int(datetime.now(timezone.utc).timestamp()) - 120,
            "exp": int((datetime.now(timezone.utc) - timedelta(seconds=5)).timestamp()),
        },
        secret,
        algorithm="HS256",
    )
    with pytest.raises(Exception):
        decode_access_token(token, secret=secret, algorithm="HS256")
