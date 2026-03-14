"""
backend/api/ai.py — AI generation endpoints (Groq)
"""

import json
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from backend.services.ai_engine import (
    generate, generate_cover_letter,
    suggest_resume_improvements, check_ai_status
)
from backend.core.rate_limit import limiter
from backend.core.settings import get_settings
from backend.core.deps import get_current_user
from fastapi import Depends
from backend.database import models as db

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


class ResumeScoreRequest(BaseModel):
    resume_text: str
    job_description: str


@router.get("/status")
async def ai_status():
    """Check AI provider availability."""
    config = _load_config()
    return check_ai_status(config)


@router.post("/generate")
@limiter.limit("30/minute")
async def ai_generate(request: Request, req: GenerateRequest):
    _ = request
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
@limiter.limit("30/minute")
async def ai_cover_letter(request: Request, req: CoverLetterRequest):
    _ = request
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
@limiter.limit("30/minute")
async def ai_improve(request: Request, req: ImproveRequest):
    _ = request
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
@limiter.limit("30/minute")
async def ai_improve_bullet(request: Request, req: ImproveBulletRequest):
    _ = request
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


@router.post("/score-resume")
@limiter.limit("30/minute")
async def score_resume(request: Request, req: ResumeScoreRequest):
    _ = request
    try:
        config = _load_config()
        prompt = (
            "Score this resume against the job description and return ONLY valid JSON with fields: "
            "score (0-100 int), keyword_matches (string[]), missing_keywords (string[]), "
            "strengths (string[]), weaknesses (string[]), verdict (string).\n\n"
            f"Resume:\n{req.resume_text}\n\n"
            f"Job Description:\n{req.job_description}"
        )
        raw = generate(prompt, config=config, max_tokens=700)
        if not raw:
            raise HTTPException(status_code=502, detail="AI did not return a score")
        clean = raw.strip()
        start = clean.find("{")
        end = clean.rfind("}") + 1
        payload = json.loads(clean[start:end] if start != -1 and end > start else clean)
        score = int(payload.get("score", 0))
        payload["score"] = min(100, max(0, score))
        payload.setdefault("keyword_matches", [])
        payload.setdefault("missing_keywords", [])
        payload.setdefault("strengths", [])
        payload.setdefault("weaknesses", [])
        payload.setdefault("verdict", "")
        return payload
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/role-suggestions")
@limiter.limit("30/minute")
async def role_suggestions(request: Request, user: dict = Depends(get_current_user)):
    _ = request
    try:
        cache_key = f"roles_{user['id']}"
        cached = db.get_ai_cache(cache_key)
        if cached:
            generated_at = cached.get("generated_at")
            if generated_at:
                from datetime import timedelta

                ts = datetime.fromisoformat(str(generated_at).replace("Z", "+00:00"))
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
                if datetime.now(timezone.utc) - ts < timedelta(hours=24):
                    return cached

        bundle = db.get_profile_bundle(user["id"])
        config = _load_config()
        prompt = (
            "You are a career advisor. Return ONLY valid JSON with fields top_roles, skill_gaps, "
            "recommended_certifications. top_roles is max 5 items sorted by match_score desc and each item has "
            "role, match_score(0-100 int), reason. skill_gaps items have skill, priority(high|medium|low), how_to_learn.\n\n"
            f"Profile bundle:\n{json.dumps(bundle)}"
        )
        raw = generate(prompt, config=config, max_tokens=800)
        clean = raw.strip() if raw else "{}"
        start = clean.find("{")
        end = clean.rfind("}") + 1
        data = json.loads(clean[start:end] if start != -1 and end > start else clean)
        roles = sorted(data.get("top_roles", []), key=lambda x: int(x.get("match_score", 0)), reverse=True)[:5]
        out = {
            "top_roles": roles,
            "skill_gaps": data.get("skill_gaps", []),
            "recommended_certifications": data.get("recommended_certifications", []),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        db.set_ai_cache(cache_key, "role_suggestions", out)
        return out
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
