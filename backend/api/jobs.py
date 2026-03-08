"""
backend/api/jobs.py — Job application tracker endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from backend.database import models as db

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
async def list_applications():
    """Get all job applications."""
    try:
        apps = db.get_applications()
        # Group by status for Kanban view
        kanban = {s: [] for s in VALID_STATUSES}
        for app in apps:
            status = app.get("status", "applied")
            if status in kanban:
                kanban[status].append(app)
        return {"applications": apps, "kanban": kanban, "total": len(apps)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
async def create_application(req: ApplicationCreate):
    """Add a new job application."""
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
async def update_application(app_id: int, req: ApplicationUpdate):
    """Update an application (status, notes, etc.)."""
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
async def delete_application(app_id: int):
    """Delete a job application."""
    try:
        db.delete_application(app_id)
        return {"success": True, "id": app_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
