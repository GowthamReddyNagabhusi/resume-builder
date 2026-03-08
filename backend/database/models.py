"""
backend/database/models.py — SQLite layer for Antigravity Career Agent
Upgraded schema with users, projects, resumes, applications, stats
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "data" / "career.db"


def get_conn():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()

    # Stats snapshots (GitHub / Codeforces / LeetCode)
    c.execute("""
        CREATE TABLE IF NOT EXISTS stats_snapshots (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            source     TEXT NOT NULL,
            data       TEXT NOT NULL,
            fetched_at TEXT NOT NULL
        )
    """)

    # GitHub projects
    c.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            name           TEXT UNIQUE NOT NULL,
            description    TEXT,
            language       TEXT,
            stars          INTEGER DEFAULT 0,
            url            TEXT,
            topics         TEXT,
            show_on_resume INTEGER DEFAULT 1,
            updated_at     TEXT
        )
    """)

    # Generated resumes
    c.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            title        TEXT,
            job_role     TEXT,
            file_path    TEXT,
            ai_content   TEXT,
            generated_at TEXT
        )
    """)

    # Job application tracker
    c.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            company     TEXT NOT NULL,
            role        TEXT NOT NULL,
            status      TEXT DEFAULT 'applied',
            notes       TEXT,
            link        TEXT,
            applied_at  TEXT,
            updated_at  TEXT
        )
    """)

    # Manual skills
    c.execute("""
        CREATE TABLE IF NOT EXISTS manual_skills (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            skill    TEXT UNIQUE NOT NULL,
            added_at TEXT
        )
    """)

    # Manual certifications
    c.execute("""
        CREATE TABLE IF NOT EXISTS manual_certs (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            cert     TEXT NOT NULL,
            added_at TEXT
        )
    """)

    # Manual experience/training entries
    c.execute("""
        CREATE TABLE IF NOT EXISTS manual_experience (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            entry    TEXT NOT NULL,
            added_at TEXT
        )
    """)

    # AI response cache
    c.execute("""
        CREATE TABLE IF NOT EXISTS ai_cache (
            cache_key    TEXT PRIMARY KEY,
            section      TEXT,
            content      TEXT,
            generated_at TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("[DB] Initialized.")


# ── Stats snapshots ────────────────────────────────────────

def save_snapshot(source: str, data: dict):
    conn = get_conn()
    conn.execute(
        "INSERT INTO stats_snapshots (source, data, fetched_at) VALUES (?,?,?)",
        (source, json.dumps(data), datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def get_latest_snapshot(source: str) -> dict:
    conn = get_conn()
    row = conn.execute(
        "SELECT data FROM stats_snapshots WHERE source=? ORDER BY fetched_at DESC LIMIT 1",
        (source,)
    ).fetchone()
    conn.close()
    return json.loads(row["data"]) if row else {}


# ── Projects ───────────────────────────────────────────────

def upsert_project(name, description, language, stars, url, topics=""):
    conn = get_conn()
    conn.execute("""
        INSERT INTO projects (name, description, language, stars, url, topics, updated_at)
        VALUES (?,?,?,?,?,?,?)
        ON CONFLICT(name) DO UPDATE SET
            description=excluded.description,
            language=excluded.language,
            stars=excluded.stars,
            url=excluded.url,
            topics=excluded.topics,
            updated_at=excluded.updated_at
    """, (name, description, language, stars, url, topics, datetime.now().isoformat()))
    conn.commit()
    conn.close()


def get_projects(limit=10, only_resume=True):
    conn = get_conn()
    if only_resume:
        rows = conn.execute(
            "SELECT * FROM projects WHERE show_on_resume=1 ORDER BY stars DESC LIMIT ?",
            (limit,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM projects ORDER BY stars DESC LIMIT ?", (limit,)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def toggle_project_resume(project_id: int, show: bool):
    conn = get_conn()
    conn.execute(
        "UPDATE projects SET show_on_resume=? WHERE id=?",
        (1 if show else 0, project_id)
    )
    conn.commit()
    conn.close()


# ── Job Applications ───────────────────────────────────────

def add_application(company: str, role: str, link: str = "", notes: str = "") -> int:
    conn = get_conn()
    now = datetime.now().isoformat()
    cur = conn.execute(
        "INSERT INTO applications (company, role, status, notes, link, applied_at, updated_at) VALUES (?,?,?,?,?,?,?)",
        (company, role, "applied", notes, link, now, now)
    )
    conn.commit()
    app_id = cur.lastrowid
    conn.close()
    return app_id


def get_applications():
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM applications ORDER BY applied_at DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_application(app_id: int, **kwargs):
    conn = get_conn()
    kwargs["updated_at"] = datetime.now().isoformat()
    set_clause = ", ".join(f"{k}=?" for k in kwargs)
    values = list(kwargs.values()) + [app_id]
    conn.execute(f"UPDATE applications SET {set_clause} WHERE id=?", values)
    conn.commit()
    conn.close()


def delete_application(app_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM applications WHERE id=?", (app_id,))
    conn.commit()
    conn.close()


# ── Resumes ────────────────────────────────────────────────

def log_resume(title: str, job_role: str, file_path: str, ai_content: str = "") -> int:
    conn = get_conn()
    cur = conn.execute(
        "INSERT INTO resumes (title, job_role, file_path, ai_content, generated_at) VALUES (?,?,?,?,?)",
        (title, job_role, file_path, ai_content, datetime.now().isoformat())
    )
    conn.commit()
    resume_id = cur.lastrowid
    conn.close()
    return resume_id


def get_resumes(limit=20):
    conn = get_conn()
    rows = conn.execute(
        "SELECT id, title, job_role, file_path, generated_at FROM resumes ORDER BY generated_at DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Manual data ────────────────────────────────────────────

def add_skill(skill: str) -> bool:
    conn = get_conn()
    try:
        conn.execute("INSERT INTO manual_skills (skill, added_at) VALUES (?,?)",
                     (skill.strip(), datetime.now().isoformat()))
        conn.commit()
        result = True
    except sqlite3.IntegrityError:
        result = False
    conn.close()
    return result


def get_manual_skills():
    conn = get_conn()
    rows = conn.execute("SELECT skill FROM manual_skills").fetchall()
    conn.close()
    return [r["skill"] for r in rows]


def add_cert(cert: str):
    conn = get_conn()
    conn.execute("INSERT INTO manual_certs (cert, added_at) VALUES (?,?)",
                 (cert.strip(), datetime.now().isoformat()))
    conn.commit()
    conn.close()


def get_certs():
    conn = get_conn()
    rows = conn.execute("SELECT cert FROM manual_certs ORDER BY added_at DESC").fetchall()
    conn.close()
    return [r["cert"] for r in rows]


def add_experience(entry: str):
    conn = get_conn()
    conn.execute("INSERT INTO manual_experience (entry, added_at) VALUES (?,?)",
                 (entry.strip(), datetime.now().isoformat()))
    conn.commit()
    conn.close()


def get_experience():
    conn = get_conn()
    rows = conn.execute("SELECT entry FROM manual_experience ORDER BY added_at DESC").fetchall()
    conn.close()
    return [r["entry"] for r in rows]
