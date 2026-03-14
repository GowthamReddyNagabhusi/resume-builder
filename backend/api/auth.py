"""Authentication endpoints: signup, login, me, logout, refresh, verification, reset."""

from __future__ import annotations

import os
import secrets
import smtplib
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field

from backend.core.deps import get_current_user
from backend.core.logger import get_logger
from backend.core.rate_limit import limiter
from backend.core.security import create_access_token, decode_access_token, hash_password, verify_password
from backend.core.settings import get_settings
from backend.database import models as db

router = APIRouter(prefix="/api/auth", tags=["Auth"])
bearer_scheme = HTTPBearer(auto_error=False)
log = get_logger(__name__)


class SignUpRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


def _send_email(subject: str, to_email: str, body: str) -> None:
    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_pass = os.getenv("SMTP_PASS", "")
    email_from = os.getenv("EMAIL_FROM", smtp_user or "no-reply@careerforge.local")

    if not smtp_host or not smtp_user or not smtp_pass:
        log.warning("SMTP not configured; email not sent to %s", to_email)
        log.info("Email subject: %s | body: %s", subject, body)
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = email_from
    msg["To"] = to_email
    msg.set_content(body)

    with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)


def _issue_token(user: dict) -> tuple[str, str, datetime]:
    cfg = get_settings().get("app", {})
    return create_access_token(
        user_id=user["id"],
        email=user["email"],
        secret=cfg.get("jwt_secret", ""),
        algorithm=cfg.get("jwt_algorithm", "HS256"),
        exp_minutes=int(cfg.get("jwt_exp_minutes", 120)),
    )


def _set_auth_cookie(response: Response, token: str) -> None:
    exp_seconds = int(get_settings().get("app", {}).get("jwt_exp_minutes", 120)) * 60
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=exp_seconds,
        path="/",
    )


@router.post("/signup")
@limiter.limit("5/minute")
async def signup(request: Request, req: SignUpRequest):
    _ = request
    db.init_db()
    existing = db.get_user_by_email(req.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user_id = db.create_user(req.name, req.email, hash_password(req.password))

    token = secrets.token_hex(32)
    expires_at = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
    db.create_email_verification(user_id, token, expires_at)

    backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
    verify_link = f"{backend_url}/api/auth/verify-email?token={token}"
    _send_email("Verify your CareerForge email", req.email, f"Verify your email: {verify_link}")

    return {"success": True, "user_id": user_id}


@router.post("/register")
@limiter.limit("5/minute")
async def register(request: Request, req: SignUpRequest):
    """Alias for /signup — used by the frontend API client."""
    return await signup(request, req)


@router.get("/verify-email")
async def verify_email(token: str):
    rec = db.get_email_verification(token)
    if not rec:
        raise HTTPException(status_code=400, detail="Invalid verification token")
    if int(rec.get("used", 0)):
        raise HTTPException(status_code=400, detail="Verification token already used")

    exp = datetime.fromisoformat(str(rec["expires_at"]).replace("Z", "+00:00"))
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    if exp < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Verification token expired")

    db.verify_user_email(int(rec["user_id"]))
    db.mark_email_verification_used(token)

    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    return RedirectResponse(url=f"{frontend_url}/login?verified=true", status_code=307)


@router.post("/resend-verification")
@limiter.limit("3/hour")
async def resend_verification(request: Request, user: dict = Depends(get_current_user)):
    _ = request
    token = secrets.token_hex(32)
    expires_at = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
    db.create_email_verification(user["id"], token, expires_at)

    backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
    verify_link = f"{backend_url}/api/auth/verify-email?token={token}"
    _send_email("Verify your CareerForge email", user["email"], f"Verify your email: {verify_link}")
    return {"success": True}


@router.post("/login")
@limiter.limit("10/minute")
async def login(request: Request, req: LoginRequest, response: Response):
    _ = request
    db.init_db()
    user = db.get_user_by_email(req.email)
    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token, jti, exp = _issue_token(user)
    db.save_session(jti=jti, user_id=user["id"], expires_at=exp.isoformat())
    _set_auth_cookie(response, token)

    profile_bundle = db.get_profile_bundle(user["id"])
    setup_completed = bool((profile_bundle.get("profile") or {}).get("setup_completed"))

    return {
        "success": True,
        "access_token": token,
        "token_type": "bearer",
        "expires_at": int(exp.timestamp()),
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "created_at": user["created_at"],
            "email_verified": bool(user.get("email_verified", 0)),
            "setup_completed": setup_completed,
        },
    }


@router.post("/refresh")
async def refresh_token(response: Response, user: dict = Depends(get_current_user)):
    full_user = db.get_user_by_id(user["id"])
    if not full_user:
        raise HTTPException(status_code=401, detail="User not found")

    token, jti, exp = _issue_token(full_user)
    db.save_session(jti=jti, user_id=user["id"], expires_at=exp.isoformat())
    _set_auth_cookie(response, token)
    return {"success": True, "access_token": token, "token_type": "bearer", "expires_at": int(exp.timestamp())}


@router.get("/me")
async def me(user: dict = Depends(get_current_user)):
    bundle = db.get_profile_bundle(user["id"])
    setup_completed = bool((bundle.get("profile") or {}).get("setup_completed"))
    return {**user, "setup_completed": setup_completed}


@router.post("/logout")
async def logout(response: Response, request: Request, credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = ""
    if credentials and credentials.scheme.lower() == "bearer":
        token = credentials.credentials
    if not token:
        token = request.cookies.get("access_token", "")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authentication token")

    cfg = get_settings().get("app", {})
    try:
        payload = decode_access_token(token, secret=cfg.get("jwt_secret", ""), algorithm=cfg.get("jwt_algorithm", "HS256"))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    jti = payload.get("jti")
    if jti:
        db.revoke_session(jti)
    response.delete_cookie(key="access_token", path="/")
    return {"success": True}


@router.post("/forgot-password")
@limiter.limit("3/hour")
async def forgot_password(request: Request, req: ForgotPasswordRequest):
    _ = request
    user = db.get_user_by_email(req.email)
    if user:
        token = secrets.token_hex(32)
        expires_at = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        db.create_password_reset(int(user["id"]), token, expires_at)
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        reset_link = f"{frontend_url}/reset-password?token={token}"
        _send_email("Reset your CareerForge password", req.email, f"Reset your password: {reset_link}")
    return {"success": True, "message": "If the email exists, reset instructions were sent."}


@router.post("/reset-password")
async def reset_password(req: ResetPasswordRequest):
    rec = db.get_password_reset(req.token)
    if not rec:
        raise HTTPException(status_code=400, detail="Invalid reset token")
    if int(rec.get("used", 0)):
        raise HTTPException(status_code=400, detail="Reset token already used")

    exp = datetime.fromisoformat(str(rec["expires_at"]).replace("Z", "+00:00"))
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    if exp < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Reset token expired")

    db.update_user_password(int(rec["user_id"]), hash_password(req.new_password))
    db.mark_password_reset_used(req.token)
    db.revoke_all_sessions_for_user(int(rec["user_id"]))
    return {"success": True, "message": "Password updated. Please log in."}
