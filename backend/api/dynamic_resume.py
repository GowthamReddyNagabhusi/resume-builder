"""Dynamic resume generation and history endpoints."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from math import ceil

from core.deps import get_current_user
from database import models as db
from services.dynamic_resume_builder import build_dynamic_resume

router = APIRouter(prefix="/api/dynamic-resume", tags=["Dynamic Resume"])


class ResumeConfigRequest(BaseModel):
    template_id: int | None = None
    selected_projects: list[int] = Field(default_factory=list)
    selected_skills: list[str] = Field(default_factory=list)
    selected_experience: list[int] = Field(default_factory=list)
    selected_platforms: list[int] = Field(default_factory=list)
    target_role: str = ""
    output_type: str = "docx"


@router.post("/generate")
async def generate_dynamic_resume(req: ResumeConfigRequest, user: dict = Depends(get_current_user)):
    try:
        config_id = db.create_resume_config(user["id"], req.model_dump())
        result = build_dynamic_resume(user_id=user["id"], config=req.model_dump(), config_id=config_id)
        resume_id = db.log_generated_resume(
            user_id=user["id"],
            config_id=config_id,
            template_id=req.template_id,
            file_path=result["file_path"],
            file_type=req.output_type,
        )
        return {
            "success": True,
            "resume_id": resume_id,
            "config_id": config_id,
            "download_url": f"/api/dynamic-resume/download/{resume_id}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def history(page: int = 1, per_page: int = 20, user: dict = Depends(get_current_user)):
    page = max(page, 1)
    per_page = min(max(per_page, 1), 100)
    offset = (page - 1) * per_page
    resumes = db.list_generated_resumes(user["id"], limit=per_page, offset=offset)
    total = db.count_generated_resumes(user["id"])
    return {
        "resumes": resumes,
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": max(1, ceil(total / per_page)),
    }


@router.get("/download/{resume_id}")
async def download_resume(resume_id: int, user: dict = Depends(get_current_user)):
    rec = db.get_generated_resume(user["id"], resume_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Resume not found")
    path = Path(rec["file_path"])
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    media_type = "application/pdf" if rec["file_type"] == "pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    return FileResponse(path=str(path), filename=path.name, media_type=media_type)
