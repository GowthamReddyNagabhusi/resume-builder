"""Resume template upload and listing endpoints."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from backend.core.deps import get_current_user
from backend.database import models as db

router = APIRouter(prefix="/api/templates", tags=["Templates"])

UPLOAD_DIR = Path(__file__).resolve().parents[2] / "data" / "templates"
ALLOWED_TYPES = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "application/x-latex": "tex",
    "text/x-tex": "tex",
    "application/json": "json",
    "text/plain": "tex",
}


@router.post("/upload")
async def upload_template(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    content_type = file.content_type or ""
    ext = ALLOWED_TYPES.get(content_type)
    if not ext:
        name_lower = (file.filename or "").lower()
        if name_lower.endswith(".docx"):
            ext = "docx"
        elif name_lower.endswith(".tex"):
            ext = "tex"
        elif name_lower.endswith(".json"):
            ext = "json"
    if not ext:
        raise HTTPException(status_code=400, detail="Unsupported template format. Use DOCX, LaTeX, or JSON.")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = (file.filename or "template").replace(" ", "_")
    disk_name = f"u{user['id']}_{safe_name}"
    target = UPLOAD_DIR / disk_name

    content = await file.read()
    target.write_bytes(content)

    template_id = db.create_template(
        user_id=user["id"],
        template_name=Path(safe_name).stem,
        template_file=str(target),
        template_type=ext,
    )
    return {"success": True, "template_id": template_id}


@router.get("")
async def list_templates(user: dict = Depends(get_current_user)):
    return {"templates": db.list_templates(user["id"])}
