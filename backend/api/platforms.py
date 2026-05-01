"""Endpoints for coding platform data synchronization."""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends

from core.deps import get_current_user
from database import models as db
from services.platform_sync import sync_user_platform_data

router = APIRouter(prefix="/api/platforms", tags=["Platforms"])


@router.post("/sync")
async def sync_platforms(background_tasks: BackgroundTasks, user: dict = Depends(get_current_user)):
    background_tasks.add_task(sync_user_platform_data, user["id"])
    return {"success": True, "message": "Platform sync queued"}


@router.get("/data")
async def platform_data(user: dict = Depends(get_current_user)):
    bundle = db.get_profile_bundle(user["id"])
    return {"coding_platforms": bundle.get("coding_platforms", []), "github_data": bundle.get("github_data")}
