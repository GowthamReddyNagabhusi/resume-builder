"""
backend/api/jobs.py — Job application tracker endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from backend.core.deps import get_current_user
from backend.database import models as db
from fastapi import Depends
from math import ceil

router = APIRouter(prefix="/api/jobs", tags=["Job Tracker"])

VALID_STATUSES = {"applied", "interview", "offer", "rejected"}


class ApplicationCreate(BaseModel):
    company: str
    role: str
    link: str = ""
    notes: str = ""


class ApplicationUpdate(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    link: Optional[str] = None


@router.get("")
async def list_applications(page: int = 1, per_page: int = 20, user: dict = Depends(get_current_user)):
    """Get all job applications."""
    _ = user
    try:
        page = max(page, 1)
        per_page = min(max(per_page, 1), 100)
        offset = (page - 1) * per_page

        apps = db.get_applications(limit=per_page, offset=offset)
        total = db.count_applications()
        pages = max(1, ceil(total / per_page))
        # Group by status for Kanban view
        kanban = {s: [] for s in VALID_STATUSES}
        for app in apps:
            status = app.get("status", "applied")
            if status in kanban:
                kanban[status].append(app)
        return {
            "applications": apps,
            "kanban": kanban,
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": pages,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
async def create_application(req: ApplicationCreate, user: dict = Depends(get_current_user)):
    """Add a new job application."""
    _ = user
    try:
        app_id = db.add_application(
            company=req.company,
            role=req.role,
            link=req.link,
            notes=req.notes
        )
        return {"success": True, "id": app_id, "status": "applied"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{app_id}")
async def update_application(app_id: int, req: ApplicationUpdate, user: dict = Depends(get_current_user)):
    """Update an application (status, notes, etc.)."""
    _ = user
    try:
        updates = req.model_dump(exclude_none=True)
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")
        if "status" in updates and updates["status"] not in VALID_STATUSES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}"
            )
        db.update_application(app_id, **updates)
        return {"success": True, "id": app_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{app_id}")
async def delete_application(app_id: int, user: dict = Depends(get_current_user)):
    """Delete a job application."""
    _ = user
    try:
        db.delete_application(app_id)
        return {"success": True, "id": app_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
