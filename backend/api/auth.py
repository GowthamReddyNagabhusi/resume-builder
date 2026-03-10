"""Authentication endpoints: signup, login, me, logout."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field

from backend.core.deps import get_current_user
from backend.core.security import create_access_token, hash_password, verify_password
from backend.core.settings import get_settings
from backend.database import models as db

router = APIRouter(prefix="/api/auth", tags=["Auth"])
bearer_scheme = HTTPBearer(auto_error=False)


class SignUpRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/signup")
async def signup(req: SignUpRequest):
    db.init_db()
    existing = db.get_user_by_email(req.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user_id = db.create_user(req.name, req.email, hash_password(req.password))
    return {"success": True, "user_id": user_id}


@router.post("/login")
async def login(req: LoginRequest):
    db.init_db()
    user = db.get_user_by_email(req.email)
    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    cfg = get_settings()
    app_cfg = cfg.get("app", {})
    token, jti, exp = create_access_token(
        user_id=user["id"],
        email=user["email"],
        secret=app_cfg.get("jwt_secret", ""),
        algorithm=app_cfg.get("jwt_algorithm", "HS256"),
        exp_minutes=int(app_cfg.get("jwt_exp_minutes", 120)),
    )
    db.save_session(jti=jti, user_id=user["id"], expires_at=exp.isoformat())

    profile_bundle = db.get_profile_bundle(user["id"])
    setup_completed = bool((profile_bundle.get("profile") or {}).get("setup_completed"))

    return {
        "success": True,
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "created_at": user["created_at"],
            "setup_completed": setup_completed,
        },
    }


@router.get("/me")
async def me(user: dict = Depends(get_current_user)):
    bundle = db.get_profile_bundle(user["id"])
    setup_completed = bool((bundle.get("profile") or {}).get("setup_completed"))
    return {"user": {**user, "setup_completed": setup_completed}}


@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    cfg = get_settings()
    app_cfg = cfg.get("app", {})
    from backend.core.security import decode_access_token

    try:
        payload = decode_access_token(
            credentials.credentials,
            secret=app_cfg.get("jwt_secret", ""),
            algorithm=app_cfg.get("jwt_algorithm", "HS256"),
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    jti = payload.get("jti")
    if jti:
        db.revoke_session(jti)
    return {"success": True}
