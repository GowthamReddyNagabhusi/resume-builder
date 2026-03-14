"""Resume template upload and listing endpoints."""

from __future__ import annotations

import re
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from backend.core.deps import get_current_user
from backend.core.logger import get_logger
from backend.database import models as db

router = APIRouter(prefix="/api/templates", tags=["Templates"])
log = get_logger(__name__)

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
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large")

    safe_name = Path(file.filename or "template").name
    safe_name = re.sub(r"[^\w.\-]", "_", safe_name)
    ext_name = Path(safe_name).suffix.lower()
    if ext_name not in {".docx", ".tex", ".json"}:
        raise HTTPException(status_code=400, detail="Unsupported format")

    content_type = file.content_type or ""
    ext = ALLOWED_TYPES.get(content_type)
    if not ext:
        name_lower = safe_name.lower()
        if name_lower.endswith(".docx"):
            ext = "docx"
        elif name_lower.endswith(".tex"):
            ext = "tex"
        elif name_lower.endswith(".json"):
            ext = "json"
    if not ext:
        raise HTTPException(status_code=400, detail="Unsupported template format. Use DOCX, LaTeX, or JSON.")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    disk_name = f"u{user['id']}_{safe_name}"
    target = UPLOAD_DIR / disk_name

    target.write_bytes(content)

    template_id = db.create_template(
        user_id=user["id"],
        template_name=Path(safe_name).stem,
        template_file=str(target),
        template_type=ext,
    )
    log.info("Template uploaded: user=%s file=%s size=%s", user["id"], safe_name, len(content))
    return {"success": True, "template_id": template_id}


@router.get("")
async def list_templates(user: dict = Depends(get_current_user)):
    return {"templates": db.list_templates(user["id"])}
