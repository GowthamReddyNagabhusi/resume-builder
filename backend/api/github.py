"""
backend/api/github.py — GitHub import and project management endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.github_parser import fetch_github
from backend.database import models as db
from backend.core.settings import get_settings

router = APIRouter(prefix="/api/github", tags=["GitHub"])

def _load_config() -> dict:
    return get_settings()


class ToggleRequest(BaseModel):
    show: bool


@router.get("/import/{username}")
async def import_github(username: str):
    """Fetch and save all GitHub repos for a user."""
    try:
        config = _load_config()
        data = fetch_github(username)
        if not data:
            raise HTTPException(status_code=404, detail=f"GitHub user '{username}' not found")
        projects = db.get_projects(limit=100, only_resume=False)
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
async def list_projects(all: bool = False):
    """List stored GitHub projects."""
    try:
        projects = db.get_projects(limit=100, only_resume=not all)
        return {"projects": projects, "count": len(projects)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/projects/{project_id}")
async def toggle_project(project_id: int, req: ToggleRequest):
    """Toggle whether a project appears on the resume."""
    try:
        db.toggle_project_resume(project_id, req.show)
        return {"success": True, "project_id": project_id, "show_on_resume": req.show}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
