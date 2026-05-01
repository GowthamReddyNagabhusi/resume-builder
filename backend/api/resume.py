"""
backend/api/resume.py — Resume generation and download endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path

from services.resume_builder import build_docx
from core.deps import get_current_user
from database import models as db
from core.settings import get_settings
from math import ceil

router = APIRouter(prefix="/api/resume", tags=["Resume"])

def _load_config() -> dict:
    return get_settings()


class GenerateRequest(BaseModel):
    job_role: str = ""
    job_description: str = ""


@router.post("/generate")
async def generate_resume(req: GenerateRequest, user: dict = Depends(get_current_user)):
    """Generate a tailored DOCX resume using Groq AI."""
    try:
        config = _load_config()
        result = build_docx(config, job_role=req.job_role, job_description=req.job_description, user_id=user["id"])
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return {
            "success": True,
            "resume_id": result["resume_id"],
            "filename": result["filename"],
            "download_url": f"/api/resume/download/{result['resume_id']}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_resumes(page: int = 1, per_page: int = 20, user: dict = Depends(get_current_user)):
    """List all previously generated resumes for the current user."""
    uid = user["id"]
    try:
        page = max(page, 1)
        per_page = min(max(per_page, 1), 100)
        offset = (page - 1) * per_page
        resumes = db.get_resumes(limit=per_page, offset=offset, user_id=uid)
        total = db.count_resumes(user_id=uid)
        return {
            "resumes": resumes,
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": max(1, ceil(total / per_page)),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{resume_id}")
async def download_resume(resume_id: int, user: dict = Depends(get_current_user)):
    """Download a generated resume DOCX file (only if it belongs to the user)."""
    uid = user["id"]
    try:
        resumes = db.get_resumes(limit=100, user_id=uid)
        resume = next((r for r in resumes if r["id"] == resume_id), None)
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        file_path = Path(resume["file_path"])
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Resume file no longer exists")
        return FileResponse(
            path=str(file_path),
            filename=file_path.name,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
