"""
backend/api/github.py — GitHub import and project management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from math import ceil

from services.github_parser import fetch_github
from database import models as db
from core.deps import get_current_user
from core.settings import get_settings

router = APIRouter(prefix="/api/github", tags=["GitHub"])

def _load_config() -> dict:
    return get_settings()


class ToggleRequest(BaseModel):
    show: bool


@router.get("/import/{username}")
async def import_github(username: str, user: dict = Depends(get_current_user)):
    """Fetch and save all GitHub repos for a user."""
    try:
        config = _load_config()
        data = fetch_github(username, user["id"])
        if not data:
            raise HTTPException(status_code=404, detail=f"GitHub user '{username}' not found")
        projects = db.get_projects(limit=100, only_resume=False, user_id=user["id"])
        return {
            "profile": data,
            "projects_saved": len(projects),
            "projects": projects
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects")
async def list_projects(all: bool = False, page: int = 1, per_page: int = 50, user: dict = Depends(get_current_user)):
    """List stored GitHub projects."""
    try:
        page = max(page, 1)
        per_page = min(max(per_page, 1), 100)
        offset = (page - 1) * per_page
        projects = db.get_projects(limit=per_page, only_resume=not all, offset=offset, user_id=user["id"])
        total = db.count_projects(only_resume=not all, user_id=user["id"])
        return {
            "projects": projects,
            "count": len(projects),
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": max(1, ceil(total / per_page)),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/projects/{project_id}")
async def toggle_project(project_id: int, req: ToggleRequest, user: dict = Depends(get_current_user)):
    """Toggle whether a project appears on the resume."""
    try:
        db.toggle_project_resume(project_id, req.show, user_id=user["id"])
        return {"success": True, "project_id": project_id, "show_on_resume": req.show}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
