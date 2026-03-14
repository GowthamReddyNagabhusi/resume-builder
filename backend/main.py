"""backend/main.py - CareerForge FastAPI Server."""

import asyncio
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from backend.api import (
    ai,
    auth,
    career,
    dynamic_resume,
    github,
    jobs,
    platforms,
    profile,
    resume,
    stats,
    templates,
)
from backend.core.exceptions import (
    generic_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from backend.core.logger import get_logger
from backend.core.rate_limit import limiter
from backend.core.settings import get_settings
from backend.database import models as db

log = get_logger(__name__)
START_TIME = datetime.now(timezone.utc)


def _parse_csv_env(name: str) -> list[str]:
    raw = os.getenv(name, "")
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


async def _session_cleanup_loop() -> None:
    while True:
        try:
            db.cleanup_expired_sessions()
        except Exception as exc:
            log.error("Session cleanup failed: %s", exc)
        await asyncio.sleep(24 * 60 * 60)


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_settings()
    db.init_db()
    db.cleanup_expired_sessions()

    try:
        from alembic import command
        from alembic.config import Config

        if os.path.exists("alembic.ini"):
            alembic_cfg = Config("alembic.ini")
            command.upgrade(alembic_cfg, "head")
            log.info("Alembic migrations applied")
    except Exception as exc:
        log.warning("Alembic migration skipped: %s", exc)

    cleanup_task = asyncio.create_task(_session_cleanup_loop())

    sentry_dsn = os.getenv("SENTRY_DSN", "")
    if sentry_dsn:
        try:
            import sentry_sdk

            sentry_sdk.init(dsn=sentry_dsn, traces_sample_rate=0.1)
            log.info("Sentry monitoring enabled")
        except Exception as exc:
            log.warning("Sentry init failed: %s", exc)

    log.info("CareerForge backend ready at http://localhost:8000")
    yield
    cleanup_task.cancel()
    log.info("CareerForge shutting down")

app = FastAPI(
    title="CareerForge",
    description="AI-powered career automation: resumes, job tracking, GitHub import",
    version="3.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

if os.getenv("PROMETHEUS_ENABLED", "false").lower() == "true":
    try:
        from prometheus_fastapi_instrumentator import Instrumentator

        Instrumentator().instrument(app).expose(app, endpoint="/metrics")
        log.info("Prometheus metrics enabled")
    except Exception as exc:
        log.warning("Prometheus instrumentation failed: %s", exc)

# CORS: allow local dev, private-network clients, and env-configured origins.
cors_allow_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://0.0.0.0:3000",
]
cors_allow_origins.extend(_parse_csv_env("CORS_ALLOW_ORIGINS"))
cors_allow_origin_regex = os.getenv(
    "CORS_ALLOW_ORIGIN_REGEX",
    r"^https?://(localhost|127\.0\.0\.1|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|172\.(1[6-9]|2\d|3[0-1])\.\d+\.\d+)(:\d+)?$",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_allow_origins,
    allow_origin_regex=cors_allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "img-src 'self' data: https:; connect-src 'self' https://api.groq.com"
    )
    return response

# Mount routers
app.include_router(auth.router)
app.include_router(career.router)
app.include_router(resume.router)
app.include_router(ai.router)
app.include_router(github.router)
app.include_router(jobs.router)
app.include_router(stats.router)
app.include_router(profile.router)
app.include_router(templates.router)
app.include_router(dynamic_resume.router)
app.include_router(platforms.router)


@app.get("/")
async def root():
    return {
        "app": "CareerForge",
        "version": "3.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "auth":   "/api/auth",
            "profile": "/api/profile",
            "templates": "/api/templates",
            "dynamic_resume": "/api/dynamic-resume",
            "stats":  "/api/stats",
            "resume": "/api/resume",
            "github": "/api/github",
            "jobs":   "/api/jobs",
            "ai":     "/api/ai"
        }
    }


@app.get("/health")
async def health():
    db_status = "ok"
    try:
        with db.get_db() as conn:
            conn.execute("SELECT 1")
    except Exception:
        db_status = "error"

    uptime_seconds = int((datetime.now(timezone.utc) - START_TIME).total_seconds())
    return {"status": "ok" if db_status == "ok" else "degraded", "db": db_status, "version": "3.0.0", "uptime_seconds": uptime_seconds}
