"""
backend/database/models.py — SQLite layer for CareerForge
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

    c.execute("PRAGMA foreign_keys = ON")

    # Users/auth
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT NOT NULL,
            email         TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at    TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS user_sessions (
            jti          TEXT PRIMARY KEY,
            user_id      INTEGER NOT NULL,
            expires_at   TEXT NOT NULL,
            revoked      INTEGER DEFAULT 0,
            created_at   TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id             INTEGER UNIQUE NOT NULL,
            full_name           TEXT,
            email               TEXT,
            phone               TEXT,
            location            TEXT,
            linkedin            TEXT,
            portfolio           TEXT,
            github_profile      TEXT,
            setup_completed     INTEGER DEFAULT 0,
            created_at          TEXT NOT NULL,
            updated_at          TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS education (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL,
            university   TEXT,
            degree       TEXT,
            branch       TEXT,
            cgpa         TEXT,
            start_year   INTEGER,
            end_year     INTEGER,
            created_at   TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS coding_platforms (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id        INTEGER NOT NULL,
            platform_name  TEXT NOT NULL,
            username       TEXT,
            profile_link   TEXT,
            fetched_data   TEXT,
            last_synced_at TEXT,
            created_at     TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS github_data (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id       INTEGER UNIQUE NOT NULL,
            profile_link  TEXT,
            repositories  INTEGER DEFAULT 0,
            stars         INTEGER DEFAULT 0,
            languages     TEXT,
            projects      TEXT,
            contributions INTEGER DEFAULT 0,
            raw_data      TEXT,
            fetched_at    TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS profile_projects (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id       INTEGER NOT NULL,
            source        TEXT DEFAULT 'manual',
            title         TEXT NOT NULL,
            description   TEXT,
            tech_stack    TEXT,
            github_link   TEXT,
            live_link     TEXT,
            created_at    TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS internships (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id            INTEGER NOT NULL,
            company            TEXT,
            role               TEXT,
            start_date         TEXT,
            end_date           TEXT,
            description        TEXT,
            technologies_used  TEXT,
            created_at         TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS certifications (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id          INTEGER NOT NULL,
            certificate_name TEXT,
            provider         TEXT,
            certificate_link TEXT,
            issue_date       TEXT,
            created_at       TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS training (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL,
            course_name     TEXT,
            institution     TEXT,
            skills_learned  TEXT,
            duration        TEXT,
            created_at      TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS resume_templates (
            template_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id        INTEGER NOT NULL,
            template_name  TEXT NOT NULL,
            template_file  TEXT NOT NULL,
            template_type  TEXT NOT NULL,
            created_at     TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS resume_configs (
            id                    INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id               INTEGER NOT NULL,
            template_id           INTEGER,
            selected_projects     TEXT,
            selected_skills       TEXT,
            selected_experience   TEXT,
            selected_platforms    TEXT,
            target_role           TEXT,
            created_at            TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY(template_id) REFERENCES resume_templates(template_id) ON DELETE SET NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS generated_resumes (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id       INTEGER NOT NULL,
            config_id     INTEGER,
            template_id   INTEGER,
            file_path     TEXT NOT NULL,
            file_type     TEXT NOT NULL,
            created_at    TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY(config_id) REFERENCES resume_configs(id) ON DELETE SET NULL,
            FOREIGN KEY(template_id) REFERENCES resume_templates(template_id) ON DELETE SET NULL
        )
    """)

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


# ── Auth and users ─────────────────────────────────────────

def create_user(name: str, email: str, password_hash: str) -> int:
    conn = get_conn()
    now = datetime.now().isoformat()
    cur = conn.execute(
        "INSERT INTO users (name, email, password_hash, created_at) VALUES (?,?,?,?)",
        (name.strip(), email.strip().lower(), password_hash, now),
    )
    conn.commit()
    user_id = cur.lastrowid
    conn.close()
    return user_id


def get_user_by_email(email: str):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE email=?", (email.strip().lower(),)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id: int):
    conn = get_conn()
    row = conn.execute("SELECT id, name, email, created_at FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def save_session(jti: str, user_id: int, expires_at: str):
    conn = get_conn()
    conn.execute(
        "INSERT OR REPLACE INTO user_sessions (jti, user_id, expires_at, revoked, created_at) VALUES (?,?,?,?,?)",
        (jti, user_id, expires_at, 0, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def revoke_session(jti: str):
    conn = get_conn()
    conn.execute("UPDATE user_sessions SET revoked=1 WHERE jti=?", (jti,))
    conn.commit()
    conn.close()


def is_session_revoked(jti: str) -> bool:
    conn = get_conn()
    row = conn.execute("SELECT revoked FROM user_sessions WHERE jti=?", (jti,)).fetchone()
    conn.close()
    if not row:
        return True
    return bool(row["revoked"])


# ── Setup wizard/profile storage ───────────────────────────

def upsert_profile(user_id: int, payload: dict):
    conn = get_conn()
    now = datetime.now().isoformat()
    conn.execute(
        """
        INSERT INTO profiles (
            user_id, full_name, email, phone, location, linkedin, portfolio, github_profile,
            setup_completed, created_at, updated_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(user_id) DO UPDATE SET
            full_name=excluded.full_name,
            email=excluded.email,
            phone=excluded.phone,
            location=excluded.location,
            linkedin=excluded.linkedin,
            portfolio=excluded.portfolio,
            github_profile=excluded.github_profile,
            setup_completed=excluded.setup_completed,
            updated_at=excluded.updated_at
        """,
        (
            user_id,
            payload.get("full_name", ""),
            payload.get("email", ""),
            payload.get("phone", ""),
            payload.get("location", ""),
            payload.get("linkedin", ""),
            payload.get("portfolio", ""),
            payload.get("github_profile", ""),
            1 if payload.get("setup_completed") else 0,
            now,
            now,
        ),
    )
    conn.commit()
    conn.close()


def replace_rows(user_id: int, table: str, rows: list[dict]):
    allowed = {
        "education": ["university", "degree", "branch", "cgpa", "start_year", "end_year"],
        "coding_platforms": ["platform_name", "username", "profile_link"],
        "profile_projects": ["source", "title", "description", "tech_stack", "github_link", "live_link"],
        "internships": ["company", "role", "start_date", "end_date", "description", "technologies_used"],
        "certifications": ["certificate_name", "provider", "certificate_link", "issue_date"],
        "training": ["course_name", "institution", "skills_learned", "duration"],
    }
    if table not in allowed:
        raise ValueError("Invalid table")

    conn = get_conn()
    conn.execute(f"DELETE FROM {table} WHERE user_id=?", (user_id,))
    now = datetime.now().isoformat()
    cols = allowed[table]
    placeholders = ",".join(["?"] * (len(cols) + 2))
    col_sql = ", ".join(["user_id"] + cols + ["created_at"])
    for row in rows or []:
        values = [user_id] + [row.get(c) for c in cols] + [now]
        conn.execute(f"INSERT INTO {table} ({col_sql}) VALUES ({placeholders})", values)
    conn.commit()
    conn.close()


def get_profile_bundle(user_id: int) -> dict:
    conn = get_conn()
    profile = conn.execute("SELECT * FROM profiles WHERE user_id=?", (user_id,)).fetchone()
    edu = conn.execute("SELECT * FROM education WHERE user_id=? ORDER BY id DESC", (user_id,)).fetchall()
    platforms = conn.execute("SELECT * FROM coding_platforms WHERE user_id=? ORDER BY id DESC", (user_id,)).fetchall()
    projects = conn.execute("SELECT * FROM profile_projects WHERE user_id=? ORDER BY id DESC", (user_id,)).fetchall()
    internships = conn.execute("SELECT * FROM internships WHERE user_id=? ORDER BY id DESC", (user_id,)).fetchall()
    certs = conn.execute("SELECT * FROM certifications WHERE user_id=? ORDER BY id DESC", (user_id,)).fetchall()
    training = conn.execute("SELECT * FROM training WHERE user_id=? ORDER BY id DESC", (user_id,)).fetchall()
    github = conn.execute("SELECT * FROM github_data WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return {
        "profile": dict(profile) if profile else None,
        "education": [dict(r) for r in edu],
        "coding_platforms": [dict(r) for r in platforms],
        "projects": [dict(r) for r in projects],
        "internships": [dict(r) for r in internships],
        "certifications": [dict(r) for r in certs],
        "training": [dict(r) for r in training],
        "github_data": dict(github) if github else None,
    }


def upsert_github_data(user_id: int, payload: dict):
    conn = get_conn()
    conn.execute(
        """
        INSERT INTO github_data (
            user_id, profile_link, repositories, stars, languages, projects, contributions, raw_data, fetched_at
        ) VALUES (?,?,?,?,?,?,?,?,?)
        ON CONFLICT(user_id) DO UPDATE SET
            profile_link=excluded.profile_link,
            repositories=excluded.repositories,
            stars=excluded.stars,
            languages=excluded.languages,
            projects=excluded.projects,
            contributions=excluded.contributions,
            raw_data=excluded.raw_data,
            fetched_at=excluded.fetched_at
        """,
        (
            user_id,
            payload.get("profile_link", ""),
            payload.get("repositories", 0),
            payload.get("stars", 0),
            json.dumps(payload.get("languages", [])),
            json.dumps(payload.get("projects", [])),
            payload.get("contributions", 0),
            json.dumps(payload),
            datetime.now().isoformat(),
        ),
    )
    conn.commit()
    conn.close()


def mark_setup_completed(user_id: int):
    conn = get_conn()
    conn.execute("UPDATE profiles SET setup_completed=1, updated_at=? WHERE user_id=?", (datetime.now().isoformat(), user_id))
    conn.commit()
    conn.close()


# ── Templates and dynamic resumes ──────────────────────────

def create_template(user_id: int, template_name: str, template_file: str, template_type: str) -> int:
    conn = get_conn()
    cur = conn.execute(
        "INSERT INTO resume_templates (user_id, template_name, template_file, template_type, created_at) VALUES (?,?,?,?,?)",
        (user_id, template_name, template_file, template_type, datetime.now().isoformat()),
    )
    conn.commit()
    template_id = cur.lastrowid
    conn.close()
    return template_id


def list_templates(user_id: int) -> list[dict]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT template_id, template_name, template_file, template_type, created_at FROM resume_templates WHERE user_id=? ORDER BY created_at DESC",
        (user_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_resume_config(user_id: int, payload: dict) -> int:
    conn = get_conn()
    cur = conn.execute(
        """
        INSERT INTO resume_configs (
            user_id, template_id, selected_projects, selected_skills,
            selected_experience, selected_platforms, target_role, created_at
        ) VALUES (?,?,?,?,?,?,?,?)
        """,
        (
            user_id,
            payload.get("template_id"),
            json.dumps(payload.get("selected_projects", [])),
            json.dumps(payload.get("selected_skills", [])),
            json.dumps(payload.get("selected_experience", [])),
            json.dumps(payload.get("selected_platforms", [])),
            payload.get("target_role", ""),
            datetime.now().isoformat(),
        ),
    )
    conn.commit()
    config_id = cur.lastrowid
    conn.close()
    return config_id


def log_generated_resume(user_id: int, config_id: int | None, template_id: int | None, file_path: str, file_type: str) -> int:
    conn = get_conn()
    cur = conn.execute(
        "INSERT INTO generated_resumes (user_id, config_id, template_id, file_path, file_type, created_at) VALUES (?,?,?,?,?,?)",
        (user_id, config_id, template_id, file_path, file_type, datetime.now().isoformat()),
    )
    conn.commit()
    rid = cur.lastrowid
    conn.close()
    return rid


def list_generated_resumes(user_id: int) -> list[dict]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT id, config_id, template_id, file_path, file_type, created_at FROM generated_resumes WHERE user_id=? ORDER BY created_at DESC",
        (user_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_generated_resume(user_id: int, resume_id: int):
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM generated_resumes WHERE user_id=? AND id=?",
        (user_id, resume_id),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def list_user_ids() -> list[int]:
    conn = get_conn()
    rows = conn.execute("SELECT id FROM users ORDER BY id ASC").fetchall()
    conn.close()
    return [int(r["id"]) for r in rows]
