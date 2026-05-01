"""
backend/api/stats.py — Stats snapshots and refresh endpoints
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks

from services.github_parser import update_all_stats
from database import models as db
from core.settings import get_settings

router = APIRouter(prefix="/api/stats", tags=["Stats"])

def _load_config() -> dict:
    return get_settings()


@router.get("")
async def get_stats():
    """Get the latest stats snapshots for all platforms."""
    try:
        gh = db.get_latest_snapshot("github")
        cf = db.get_latest_snapshot("codeforces")
        lc = db.get_latest_snapshot("leetcode")
        return {
            "github":     gh,
            "codeforces": cf,
            "leetcode":   lc,
            "has_data":   bool(gh or cf or lc)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh")
async def refresh_stats(background_tasks: BackgroundTasks):
    """Trigger a background stats refresh from all platforms."""
    try:
        config = _load_config()
        background_tasks.add_task(update_all_stats, config)
        return {"success": True, "message": "Stats refresh started in background"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
