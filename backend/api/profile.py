"""Career setup wizard and profile management endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.core.deps import get_current_user
from backend.database import models as db
from backend.services.github_parser import fetch_github

router = APIRouter(prefix="/api/profile", tags=["Profile"])


class SetupPayload(BaseModel):
    personal_details: dict = Field(default_factory=dict)
    education: list[dict] = Field(default_factory=list)
    coding_platforms: list[dict] = Field(default_factory=list)
    projects: list[dict] = Field(default_factory=list)
    internships: list[dict] = Field(default_factory=list)
    certifications: list[dict] = Field(default_factory=list)
    training: list[dict] = Field(default_factory=list)


@router.get("/me")
async def get_my_profile(user: dict = Depends(get_current_user)):
    return db.get_profile_bundle(user["id"])


@router.post("/setup")
async def save_setup(payload: SetupPayload, user: dict = Depends(get_current_user)):
    try:
        uid = user["id"]
        pd = payload.personal_details or {}
        db.upsert_profile(
            uid,
            {
                "full_name": pd.get("full_name") or user.get("name"),
                "email": pd.get("email") or user.get("email"),
                "phone": pd.get("phone", ""),
                "location": pd.get("location", ""),
                "linkedin": pd.get("linkedin", ""),
                "portfolio": pd.get("portfolio", ""),
                "github_profile": pd.get("github_profile", ""),
                "setup_completed": True,
            },
        )

        db.replace_rows(uid, "education", payload.education)
        db.replace_rows(uid, "coding_platforms", payload.coding_platforms)
        db.replace_rows(uid, "profile_projects", payload.projects)
        db.replace_rows(uid, "internships", payload.internships)
        db.replace_rows(uid, "certifications", payload.certifications)
        db.replace_rows(uid, "training", payload.training)
        db.mark_setup_completed(uid)

        github_profile = pd.get("github_profile", "")
        if github_profile:
            username = github_profile.rstrip("/").split("/")[-1]
            gh = fetch_github(username)
            if gh:
                db.upsert_github_data(
                    uid,
                    {
                        "profile_link": gh.get("profile_url", github_profile),
                        "repositories": gh.get("public_repos", 0),
                        "stars": gh.get("total_stars", 0),
                        "languages": gh.get("top_languages", []),
                        "projects": db.get_projects(limit=10, only_resume=False),
                        "contributions": 0,
                    },
                )

        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
