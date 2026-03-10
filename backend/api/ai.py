"""
backend/api/ai.py — AI generation endpoints (Groq)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.ai_engine import (
    generate, generate_cover_letter,
    suggest_resume_improvements, check_ai_status
)
from backend.core.settings import get_settings

router = APIRouter(prefix="/api/ai", tags=["AI"])

def _load_config() -> dict:
    return get_settings()


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


class ImproveBulletRequest(BaseModel):
    bullet: str
    target_role: str = ""


@router.get("/status")
async def ai_status():
    """Check AI provider availability."""
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


@router.post("/improve-bullet")
async def ai_improve_bullet(req: ImproveBulletRequest):
    """Improve a single resume bullet with stronger, measurable phrasing."""
    try:
        config = _load_config()
        prompt = (
            "Rewrite this resume bullet to be more technical and impact-driven. "
            "Keep it to one sentence under 30 words. "
            "Use strong action verbs and include measurable impact when possible.\n\n"
            f"Target Role: {req.target_role or 'Software Engineer'}\n"
            f"Bullet: {req.bullet}"
        )
        improved = generate(prompt, config=config, max_tokens=120)
        return {"original": req.bullet, "improved": improved or req.bullet, "success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
