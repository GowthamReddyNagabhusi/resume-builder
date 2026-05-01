"""Career Data CRUD API — education, experience, skills, projects, certifications, achievements, platforms."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from core.deps import get_current_user
from core.logger import get_logger
from database import models as db

router = APIRouter(prefix="/api/career", tags=["Career Data"])
log = get_logger(__name__)


# ── Pydantic models ─────────────────────────────────────────────

class EducationCreate(BaseModel):
    institution: str
    degree: str
    field_of_study: str = ""
    start_year: int | None = None
    end_year: int | None = None
    start_month: str = ""
    end_month: str = ""
    is_current: bool = False
    grade_type: str = "CGPA"
    gpa: str = ""
    description: str = ""


class ExperienceCreate(BaseModel):
    company: str
    position: str
    location: str = ""
    start_date: str = ""
    end_date: str = ""
    description: str = ""
    technologies_used: str = ""


class SkillCreate(BaseModel):
    name: str
    proficiency: str = ""
    category: str = ""


class ProjectCreate(BaseModel):
    name: str
    description: str = ""
    technologies: str = ""
    url: str = ""
    start_date: str = ""
    end_date: str = ""


class CertificationCreate(BaseModel):
    name: str
    issuing_organization: str = ""
    issue_date: str = ""
    expiry_date: str = ""
    credential_id: str = ""
    credential_url: str = ""


class AchievementCreate(BaseModel):
    title: str
    description: str = ""
    organization: str = ""
    date: str = ""
    link: str = ""


class PlatformLinkCreate(BaseModel):
    platform: str
    username: str = ""
    profile_url: str = ""


# ── Summary ──────────────────────────────────────────────────────

@router.get("/summary")
async def career_summary(user: dict = Depends(get_current_user)):
    """Get counts of all career data categories for this user."""
    uid = user["id"]
    bundle = db.get_profile_bundle(uid)
    skills = db.get_manual_skills(user_id=uid)
    achievements = db.get_achievements(uid)
    platforms = db.get_platform_links(uid)
    return {
        "education_count": len(bundle.get("education", [])),
        "experience_count": len(bundle.get("internships", [])),
        "skills_count": len(skills),
        "projects_count": len(bundle.get("projects", [])),
        "certifications_count": len(bundle.get("certifications", [])),
        "achievements_count": len(achievements),
        "platforms_count": len(platforms),
    }


# ── Education ────────────────────────────────────────────────────

@router.get("/education")
async def list_education(user: dict = Depends(get_current_user)):
    uid = user["id"]
    with db.get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM education WHERE user_id=? ORDER BY id DESC", (uid,)
        ).fetchall()
    return [dict(r) for r in rows]


@router.post("/education")
async def create_education(req: EducationCreate, user: dict = Depends(get_current_user)):
    uid = user["id"]
    now = datetime.now(timezone.utc).isoformat()
    with db.get_db() as conn:
        cur = conn.execute(
            """INSERT INTO education (user_id, university, degree, branch, cgpa, start_year, end_year, start_month, end_month, is_current, grade_type, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (uid, req.institution, req.degree, req.field_of_study, req.gpa,
             req.start_year, req.end_year, req.start_month, req.end_month,
             1 if req.is_current else 0, req.grade_type, now),
        )
        return {"id": cur.lastrowid, "success": True}


@router.delete("/education/{item_id}")
async def delete_education(item_id: int, user: dict = Depends(get_current_user)):
    uid = user["id"]
    with db.get_db() as conn:
        conn.execute("DELETE FROM education WHERE id=? AND user_id=?", (item_id, uid))
    return {"success": True}


# ── Experience ───────────────────────────────────────────────────

@router.get("/experience")
async def list_experience(user: dict = Depends(get_current_user)):
    uid = user["id"]
    with db.get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM internships WHERE user_id=? ORDER BY id DESC", (uid,)
        ).fetchall()
    return [dict(r) for r in rows]


@router.post("/experience")
async def create_experience(req: ExperienceCreate, user: dict = Depends(get_current_user)):
    uid = user["id"]
    now = datetime.now(timezone.utc).isoformat()
    with db.get_db() as conn:
        cur = conn.execute(
            """INSERT INTO internships (user_id, company, role, start_date, end_date, description, technologies_used, created_at)
               VALUES (?,?,?,?,?,?,?,?)""",
            (uid, req.company, req.position, req.start_date, req.end_date,
             req.description, req.technologies_used, now),
        )
        return {"id": cur.lastrowid, "success": True}


@router.delete("/experience/{item_id}")
async def delete_experience(item_id: int, user: dict = Depends(get_current_user)):
    uid = user["id"]
    with db.get_db() as conn:
        conn.execute("DELETE FROM internships WHERE id=? AND user_id=?", (item_id, uid))
    return {"success": True}


# ── Skills ───────────────────────────────────────────────────────

@router.get("/skills")
async def list_skills(user: dict = Depends(get_current_user)):
    uid = user["id"]
    with db.get_db() as conn:
        rows = conn.execute(
            "SELECT id, skill AS name, added_at FROM manual_skills WHERE user_id=? ORDER BY id DESC",
            (uid,),
        ).fetchall()
    return [dict(r) for r in rows]


@router.post("/skills")
async def create_skill(req: SkillCreate, user: dict = Depends(get_current_user)):
    uid = user["id"]
    now = datetime.now(timezone.utc).isoformat()
    try:
        with db.get_db() as conn:
            cur = conn.execute(
                "INSERT INTO manual_skills (user_id, skill, added_at) VALUES (?,?,?)",
                (uid, req.name.strip(), now),
            )
            return {"id": cur.lastrowid, "name": req.name.strip(), "success": True}
    except Exception:
        raise HTTPException(status_code=409, detail="Skill already exists")


@router.delete("/skills/{item_id}")
async def delete_skill(item_id: int, user: dict = Depends(get_current_user)):
    uid = user["id"]
    db.delete_skill(item_id, user_id=uid)
    return {"success": True}


# ── Projects ─────────────────────────────────────────────────────

@router.get("/projects")
async def list_projects(user: dict = Depends(get_current_user)):
    uid = user["id"]
    with db.get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM profile_projects WHERE user_id=? ORDER BY id DESC", (uid,)
        ).fetchall()
    return [dict(r) for r in rows]


@router.post("/projects")
async def create_project(req: ProjectCreate, user: dict = Depends(get_current_user)):
    uid = user["id"]
    now = datetime.now(timezone.utc).isoformat()
    with db.get_db() as conn:
        cur = conn.execute(
            """INSERT INTO profile_projects (user_id, source, title, description, tech_stack, github_link, live_link, created_at)
               VALUES (?,?,?,?,?,?,?,?)""",
            (uid, "manual", req.name, req.description, req.technologies,
             req.url, "", now),
        )
        return {"id": cur.lastrowid, "name": req.name, "success": True}


@router.delete("/projects/{item_id}")
async def delete_project(item_id: int, user: dict = Depends(get_current_user)):
    uid = user["id"]
    with db.get_db() as conn:
        conn.execute("DELETE FROM profile_projects WHERE id=? AND user_id=?", (item_id, uid))
    return {"success": True}


# ── Certifications ───────────────────────────────────────────────

@router.get("/certifications")
async def list_certifications(user: dict = Depends(get_current_user)):
    uid = user["id"]
    with db.get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM certifications WHERE user_id=? ORDER BY id DESC", (uid,)
        ).fetchall()
    return [dict(r) for r in rows]


@router.post("/certifications")
async def create_certification(req: CertificationCreate, user: dict = Depends(get_current_user)):
    uid = user["id"]
    now = datetime.now(timezone.utc).isoformat()
    with db.get_db() as conn:
        cur = conn.execute(
            """INSERT INTO certifications (user_id, certificate_name, provider, certificate_link, issue_date, created_at)
               VALUES (?,?,?,?,?,?)""",
            (uid, req.name, req.issuing_organization, req.credential_url,
             req.issue_date, now),
        )
        return {"id": cur.lastrowid, "name": req.name, "success": True}


@router.delete("/certifications/{item_id}")
async def delete_certification(item_id: int, user: dict = Depends(get_current_user)):
    uid = user["id"]
    with db.get_db() as conn:
        conn.execute("DELETE FROM certifications WHERE id=? AND user_id=?", (item_id, uid))
    return {"success": True}


# ── Achievements ─────────────────────────────────────────────────

@router.get("/achievements")
async def list_achievements(user: dict = Depends(get_current_user)):
    uid = user["id"]
    return db.get_achievements(uid)


@router.post("/achievements")
async def create_achievement(req: AchievementCreate, user: dict = Depends(get_current_user)):
    uid = user["id"]
    aid = db.create_achievement(
        user_id=uid,
        title=req.title,
        description=req.description,
        organization=req.organization,
        date=req.date,
        link=req.link,
    )
    return {"id": aid, "title": req.title, "success": True}


@router.delete("/achievements/{item_id}")
async def delete_achievement(item_id: int, user: dict = Depends(get_current_user)):
    uid = user["id"]
    db.delete_achievement(item_id, uid)
    return {"success": True}


# ── Platform Links ───────────────────────────────────────────────

@router.get("/platforms")
async def list_platforms(user: dict = Depends(get_current_user)):
    uid = user["id"]
    return db.get_platform_links(uid)


@router.post("/platforms")
async def create_platform(req: PlatformLinkCreate, user: dict = Depends(get_current_user)):
    uid = user["id"]
    pid = db.create_platform_link(
        user_id=uid,
        platform=req.platform,
        username=req.username,
        profile_url=req.profile_url,
    )
    return {"id": pid, "platform": req.platform, "success": True}


@router.delete("/platforms/{item_id}")
async def delete_platform(item_id: int, user: dict = Depends(get_current_user)):
    uid = user["id"]
    db.delete_platform_link(item_id, uid)
    return {"success": True}
