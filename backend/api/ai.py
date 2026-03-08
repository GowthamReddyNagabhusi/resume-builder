"""
backend/api/ai.py — AI generation endpoints (Ollama + Groq)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import yaml

from backend.services.ai_engine import (
    generate, generate_cover_letter,
    suggest_resume_improvements, check_ai_status
)

router = APIRouter(prefix="/api/ai", tags=["AI"])

CONFIG_PATH = Path(__file__).parent.parent.parent / "config.yaml"


def _load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


class GenerateRequest(BaseModel):
    prompt: str
    model: str = ""


class CoverLetterRequest(BaseModel):
    job_role: str
    company: str
    job_description: str


class ImproveRequest(BaseModel):
    resume_text: str
    job_description: str


@router.get("/status")
async def ai_status():
    """Check AI provider availability (Groq primary + optional Ollama)."""
    config = _load_config()
    return check_ai_status(config)


@router.post("/generate")
async def ai_generate(req: GenerateRequest):
    """Freeform prompt → AI response."""
    try:
        config = _load_config()
        result = generate(
            req.prompt,
            config=config,
        )
        return {"response": result, "success": bool(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cover-letter")
async def ai_cover_letter(req: CoverLetterRequest):
    """Generate a tailored cover letter."""
    try:
        config = _load_config()
        profile = config.get("profile", {})
        profile["skills"] = config.get("skills", {}).get("languages", [])
        letter = generate_cover_letter(
            job_role=req.job_role,
            company=req.company,
            job_description=req.job_description,
            profile=profile,
            config=config
        )
        return {"cover_letter": letter, "success": bool(letter)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/improve-resume")
async def ai_improve(req: ImproveRequest):
    """Suggest improvements to resume for a specific job."""
    try:
        config = _load_config()
        suggestions = suggest_resume_improvements(
            resume_text=req.resume_text,
            job_description=req.job_description,
            config=config
        )
        return {"suggestions": suggestions, "success": bool(suggestions)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
