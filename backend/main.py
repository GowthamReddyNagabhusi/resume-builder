"""
backend/main.py — CareerForge FastAPI Server
Run with: uvicorn backend.main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from backend.api import (
    resume,
    ai,
    github,
    jobs,
    stats,
    auth,
    profile,
    templates,
    dynamic_resume,
    platforms,
)
from backend.database import models as db

app = FastAPI(
    title="CareerForge",
    description="AI-powered career automation: resumes, job tracking, GitHub import",
    version="2.0.0"
)

# CORS — allow Next.js frontend on port 3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(resume.router)
app.include_router(ai.router)
app.include_router(github.router)
app.include_router(jobs.router)
app.include_router(stats.router)
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(templates.router)
app.include_router(dynamic_resume.router)
app.include_router(platforms.router)


@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    db.init_db()
    print("[CareerForge] Backend running at http://localhost:8000")
    print("[CareerForge] API Docs: http://localhost:8000/docs")


@app.get("/")
async def root():
    return {
        "app": "CareerForge",
        "version": "2.0.0",
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
    return {"status": "ok"}
