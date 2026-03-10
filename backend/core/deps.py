"""FastAPI dependencies for authenticated routes."""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.core.security import decode_access_token
from backend.core.settings import get_settings
from backend.database import models as db

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    cfg = get_settings()
    secret = cfg.get("app", {}).get("jwt_secret", "")
    algo = cfg.get("app", {}).get("jwt_algorithm", "HS256")

    try:
        payload = decode_access_token(credentials.credentials, secret=secret, algorithm=algo)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    jti = payload.get("jti")
    if not jti or db.is_session_revoked(jti):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session revoked")

    user_id = int(payload.get("sub", 0))
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
