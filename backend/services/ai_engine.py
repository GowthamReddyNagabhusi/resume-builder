"""
backend/services/ai_engine.py
Groq-powered AI engine.
"""

import json
import requests

GROQ_URL  = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"   # free tier, fast


# ── Groq (primary) ─────────────────────────────────────────

def _call_groq(api_key: str, prompt: str, max_tokens: int = 1024) -> str | None:
    if not api_key or api_key.startswith("PASTE"):
        return None
    try:
        r = requests.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": GROQ_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0.7,
            },
            timeout=30,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
    except requests.exceptions.HTTPError as e:
        code = e.response.status_code if e.response else 0
        if code == 429:
            print("[AI] Groq rate limit hit — wait a minute and retry.")
        else:
            print(f"[AI] Groq HTTP {code}: {e}")
    except Exception as e:
        print(f"[AI] Groq error: {e}")
    return None


# ── Main generate ───────────────────────────────────────────

def generate(prompt: str, config: dict = None, max_tokens: int = 1024) -> str:
    """
    Generate text using Groq.
    Returns empty string if the provider is unavailable.
    """
    cfg = config or {}
    groq_key = cfg.get("groq", {}).get("api_key", "")

    # Groq provider
    result = _call_groq(groq_key, prompt, max_tokens)
    if result:
        return result

    print("[AI] Groq unavailable. Check your GROQ_API_KEY configuration.")
    return ""


def check_ai_status(config: dict = None) -> dict:
    """Return Groq provider availability."""
    cfg = config or {}
    groq_key = cfg.get("groq", {}).get("api_key", "")
    groq_ok = bool(groq_key and not groq_key.startswith("PASTE"))

    return {
        "groq": {"available": groq_ok, "model": GROQ_MODEL},
        "primary": "groq" if groq_ok else "none",
    }


# ── Specialised helpers ─────────────────────────────────────

def generate_resume_bullets(project: dict, config: dict = None) -> list[str]:
    """Generate 4 FAANG-style resume bullets for a GitHub project."""
    prompt = f"""You are a professional resume writer for FAANG-level software engineering resumes.

Write exactly 4 bullet points for this GitHub project to include in a resume.

STRICT RULES:
- Start EVERY bullet with a strong action verb (Built, Designed, Implemented, Engineered, Optimized, Automated, Architected, Developed)
- Be specific and technical
- Include measurable outcomes where possible (e.g., handles 10k+ requests, reduced latency by 40%)
- Last bullet MUST be: "Tech: [comma-separated stack]"
- Each bullet is ONE sentence, maximum 20 words
- Return ONLY a JSON array of strings. No explanation, no markdown.

Project: {project.get('name', '')}
Description: {project.get('description', '') or 'Not provided'}
Language: {project.get('language', 'Unknown')}
Stars: {project.get('stars', 0)}

Return only the JSON array like: ["bullet1", "bullet2", "bullet3", "bullet4"]"""

    result = generate(prompt, config=config, max_tokens=512)
    if not result:
        return [
            f"Developed {project.get('name', 'this project')} with focus on performance and clean architecture.",
            f"Tech: {project.get('language', 'N/A')}",
        ]
    try:
        clean = result.strip()
        start = clean.find("[")
        end   = clean.rfind("]") + 1
        if start != -1 and end > start:
            return json.loads(clean[start:end])
        return json.loads(clean)
    except Exception:
        lines = [l.strip().lstrip("-*1234567890. ") for l in result.split("\n") if l.strip()]
        return [l for l in lines if len(l) > 10][:4]


def generate_cover_letter(
    job_role: str, company: str, job_description: str, profile: dict, config: dict = None
) -> str:
    prompt = f"""Write a professional cover letter for:

Applicant: {profile.get('name', 'The Applicant')}
Target Role: {job_role} at {company}
Skills: {', '.join(profile.get('skills', []))}

Job Description:
{job_description[:800]}

RULES:
- 3-4 paragraphs, under 350 words
- Professional but enthusiastic
- Mention 2-3 specific technical skills relevant to the JD
- Do NOT use placeholder text
- No date/address header"""

    return generate(prompt, config=config) or "Cover letter generation failed. Check AI config."


def suggest_resume_improvements(resume_text: str, job_description: str, config: dict = None) -> str:
    prompt = f"""You are a senior technical recruiter reviewing a resume.

JOB DESCRIPTION:
{job_description[:600]}

RESUME:
{resume_text[:1200]}

Give 5 specific, actionable suggestions to improve this resume for the role.
Format as a numbered list. Be direct and technical."""

    return generate(prompt, config=config) or "Improvement suggestions failed. Check AI config."
