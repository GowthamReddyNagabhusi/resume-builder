"""SQLite data layer for CareerForge."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.core.logger import get_logger

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "career.db"
log = get_logger(__name__)


def get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_db():
    conn = get_conn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with get_db() as conn:
        c = conn.cursor()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email_verified INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
            """
        )
        # Backward-compatible migration for existing databases created before email_verified was introduced.
        user_cols = {row[1] for row in c.execute("PRAGMA table_info(users)").fetchall()}
        if "email_verified" not in user_cols:
            c.execute("ALTER TABLE users ADD COLUMN email_verified INTEGER DEFAULT 0")
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS user_sessions (
                jti TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                expires_at TEXT NOT NULL,
                revoked INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                full_name TEXT,
                email TEXT,
                phone TEXT,
                location TEXT,
                linkedin TEXT,
                portfolio TEXT,
                github_profile TEXT,
                setup_completed INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS education (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                university TEXT,
                degree TEXT,
                branch TEXT,
                cgpa TEXT,
                start_year INTEGER,
                end_year INTEGER,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS coding_platforms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                platform_name TEXT NOT NULL,
                username TEXT,
                profile_link TEXT,
                fetched_data TEXT,
                last_synced_at TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS github_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                profile_link TEXT,
                repositories INTEGER DEFAULT 0,
                stars INTEGER DEFAULT 0,
                languages TEXT,
                projects TEXT,
                contributions INTEGER DEFAULT 0,
                raw_data TEXT,
                fetched_at TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS profile_projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                source TEXT DEFAULT 'manual',
                title TEXT NOT NULL,
                description TEXT,
                tech_stack TEXT,
                github_link TEXT,
                live_link TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS internships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                company TEXT,
                role TEXT,
                start_date TEXT,
                end_date TEXT,
                description TEXT,
                technologies_used TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS certifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                certificate_name TEXT,
                provider TEXT,
                certificate_link TEXT,
                issue_date TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS training (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                course_name TEXT,
                institution TEXT,
                skills_learned TEXT,
                duration TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS resume_templates (
                template_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                template_name TEXT NOT NULL,
                template_file TEXT NOT NULL,
                template_type TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS resume_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                template_id INTEGER,
                selected_projects TEXT,
                selected_skills TEXT,
                selected_experience TEXT,
                selected_platforms TEXT,
                target_role TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY(template_id) REFERENCES resume_templates(template_id) ON DELETE SET NULL
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS generated_resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                config_id INTEGER,
                template_id INTEGER,
                file_path TEXT NOT NULL,
                file_type TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY(config_id) REFERENCES resume_configs(id) ON DELETE SET NULL,
                FOREIGN KEY(template_id) REFERENCES resume_templates(template_id) ON DELETE SET NULL
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS stats_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                data TEXT NOT NULL,
                fetched_at TEXT NOT NULL
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                language TEXT,
                stars INTEGER DEFAULT 0,
                url TEXT,
                topics TEXT,
                show_on_resume INTEGER DEFAULT 1,
                updated_at TEXT
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                job_role TEXT,
                file_path TEXT,
                ai_content TEXT,
                generated_at TEXT
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                role TEXT NOT NULL,
                status TEXT DEFAULT 'applied',
                notes TEXT,
                link TEXT,
                applied_at TEXT,
                updated_at TEXT
            )
            """
        )
        c.execute("CREATE TABLE IF NOT EXISTS manual_skills (id INTEGER PRIMARY KEY AUTOINCREMENT, skill TEXT UNIQUE NOT NULL, added_at TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS manual_certs (id INTEGER PRIMARY KEY AUTOINCREMENT, cert TEXT NOT NULL, added_at TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS manual_experience (id INTEGER PRIMARY KEY AUTOINCREMENT, entry TEXT NOT NULL, added_at TEXT)")
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS ai_cache (
                cache_key TEXT PRIMARY KEY,
                section TEXT,
                content TEXT,
                generated_at TEXT
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS email_verifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                expires_at TEXT NOT NULL,
                used INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS password_resets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                expires_at TEXT NOT NULL,
                used INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )

        c.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_sessions_jti ON user_sessions(jti)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user ON user_sessions(user_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_sessions_expires ON user_sessions(expires_at)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_profiles_user ON profiles(user_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_generated_user ON generated_resumes(user_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_snapshots ON stats_snapshots(source, fetched_at)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_applications ON applications(status)")
    log.info("Database indexes verified")


# stats

def save_snapshot(source: str, data: dict[str, Any]) -> None:
    with get_db() as conn:
        conn.execute(
            "INSERT INTO stats_snapshots (source, data, fetched_at) VALUES (?,?,?)",
            (source, json.dumps(data), datetime.now(timezone.utc).isoformat()),
        )


def get_latest_snapshot(source: str) -> dict[str, Any]:
    with get_db() as conn:
        row = conn.execute(
            "SELECT data FROM stats_snapshots WHERE source=? ORDER BY fetched_at DESC LIMIT 1",
            (source,),
        ).fetchone()
    return json.loads(row["data"]) if row else {}


# projects

def upsert_project(name: str, description: str, language: str, stars: int, url: str, topics: str = "") -> None:
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO projects (name, description, language, stars, url, topics, updated_at)
            VALUES (?,?,?,?,?,?,?)
            ON CONFLICT(name) DO UPDATE SET
                description=excluded.description,
                language=excluded.language,
                stars=excluded.stars,
                url=excluded.url,
                topics=excluded.topics,
                updated_at=excluded.updated_at
            """,
            (name, description, language, stars, url, topics, datetime.now(timezone.utc).isoformat()),
        )


def get_projects(limit: int = 10, only_resume: bool = True, offset: int = 0) -> list[dict[str, Any]]:
    q = "SELECT * FROM projects"
    args: list[Any] = []
    if only_resume:
        q += " WHERE show_on_resume=1"
    q += " ORDER BY stars DESC LIMIT ? OFFSET ?"
    args.extend([limit, offset])
    with get_db() as conn:
        rows = conn.execute(q, tuple(args)).fetchall()
    return [dict(r) for r in rows]


def count_projects(only_resume: bool = True) -> int:
    q = "SELECT COUNT(*) AS c FROM projects"
    if only_resume:
        q += " WHERE show_on_resume=1"
    with get_db() as conn:
        row = conn.execute(q).fetchone()
    return int(row["c"] if row else 0)


def toggle_project_resume(project_id: int, show: bool) -> None:
    with get_db() as conn:
        conn.execute("UPDATE projects SET show_on_resume=? WHERE id=?", (1 if show else 0, project_id))


# jobs

def add_application(company: str, role: str, link: str = "", notes: str = "") -> int:
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO applications (company, role, status, notes, link, applied_at, updated_at) VALUES (?,?,?,?,?,?,?)",
            (company, role, "applied", notes, link, now, now),
        )
        return int(cur.lastrowid)


def get_applications(limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
    q = "SELECT * FROM applications ORDER BY applied_at DESC"
    args: list[Any] = []
    if limit is not None:
        q += " LIMIT ? OFFSET ?"
        args.extend([limit, offset])
    with get_db() as conn:
        rows = conn.execute(q, tuple(args)).fetchall()
    return [dict(r) for r in rows]


def count_applications() -> int:
    with get_db() as conn:
        row = conn.execute("SELECT COUNT(*) AS c FROM applications").fetchone()
    return int(row["c"] if row else 0)


def update_application(app_id: int, **kwargs) -> None:
    if not kwargs:
        return
    kwargs["updated_at"] = datetime.now(timezone.utc).isoformat()
    set_clause = ", ".join(f"{k}=?" for k in kwargs)
    values = list(kwargs.values()) + [app_id]
    with get_db() as conn:
        conn.execute(f"UPDATE applications SET {set_clause} WHERE id=?", values)


def delete_application(app_id: int) -> None:
    with get_db() as conn:
        conn.execute("DELETE FROM applications WHERE id=?", (app_id,))


# resumes

def log_resume(title: str, job_role: str = "", file_path: str = "", ai_content: str = "") -> int:
    if not file_path and title:
        file_path = title
        title = Path(file_path).stem
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO resumes (title, job_role, file_path, ai_content, generated_at) VALUES (?,?,?,?,?)",
            (title, job_role, file_path, ai_content, datetime.now(timezone.utc).isoformat()),
        )
        return int(cur.lastrowid)


def get_resumes(limit: int = 20, offset: int = 0) -> list[dict[str, Any]]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, title, job_role, file_path, generated_at FROM resumes ORDER BY generated_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()
    return [dict(r) for r in rows]


def count_resumes() -> int:
    with get_db() as conn:
        row = conn.execute("SELECT COUNT(*) AS c FROM resumes").fetchone()
    return int(row["c"] if row else 0)


# manual data

def add_skill(skill: str) -> bool:
    try:
        with get_db() as conn:
            conn.execute("INSERT INTO manual_skills (skill, added_at) VALUES (?,?)", (skill.strip(), datetime.now(timezone.utc).isoformat()))
        return True
    except sqlite3.IntegrityError:
        return False


def get_manual_skills() -> list[str]:
    with get_db() as conn:
        rows = conn.execute("SELECT skill FROM manual_skills").fetchall()
    return [r["skill"] for r in rows]


def add_cert(cert: str) -> None:
    with get_db() as conn:
        conn.execute("INSERT INTO manual_certs (cert, added_at) VALUES (?,?)", (cert.strip(), datetime.now(timezone.utc).isoformat()))


def get_certs() -> list[str]:
    with get_db() as conn:
        rows = conn.execute("SELECT cert FROM manual_certs ORDER BY added_at DESC").fetchall()
    return [r["cert"] for r in rows]


def add_experience(entry: str) -> None:
    with get_db() as conn:
        conn.execute("INSERT INTO manual_experience (entry, added_at) VALUES (?,?)", (entry.strip(), datetime.now(timezone.utc).isoformat()))


def get_experience() -> list[str]:
    with get_db() as conn:
        rows = conn.execute("SELECT entry FROM manual_experience ORDER BY added_at DESC").fetchall()
    return [r["entry"] for r in rows]


# auth

def create_user(name: str, email: str, password_hash: str) -> int:
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO users (name, email, password_hash, created_at) VALUES (?,?,?,?)",
            (name.strip(), email.strip().lower(), password_hash, now),
        )
        return int(cur.lastrowid)


def get_user_by_email(email: str) -> dict[str, Any] | None:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE email=?", (email.strip().lower(),)).fetchone()
    return dict(row) if row else None


def get_user_by_id(user_id: int) -> dict[str, Any] | None:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    if not row:
        return None
    user = dict(row)
    return {
        "id": user.get("id"),
        "name": user.get("name"),
        "email": user.get("email"),
        "created_at": user.get("created_at"),
        "email_verified": int(user.get("email_verified", 0) or 0),
    }


def verify_user_email(user_id: int) -> None:
    with get_db() as conn:
        conn.execute("UPDATE users SET email_verified=1 WHERE id=?", (user_id,))


def save_session(jti: str, user_id: int, expires_at: str) -> None:
    with get_db() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO user_sessions (jti, user_id, expires_at, revoked, created_at) VALUES (?,?,?,?,?)",
            (jti, user_id, expires_at, 0, datetime.now(timezone.utc).isoformat()),
        )


def revoke_session(jti: str) -> None:
    with get_db() as conn:
        conn.execute("UPDATE user_sessions SET revoked=1 WHERE jti=?", (jti,))


def revoke_all_sessions_for_user(user_id: int) -> None:
    with get_db() as conn:
        conn.execute("UPDATE user_sessions SET revoked=1 WHERE user_id=?", (user_id,))


def is_session_revoked(jti: str) -> bool:
    with get_db() as conn:
        row = conn.execute("SELECT revoked, expires_at FROM user_sessions WHERE jti=?", (jti,)).fetchone()
    if not row:
        return True
    if int(row["revoked"]):
        return True
    try:
        exp = datetime.fromisoformat(str(row["expires_at"]).replace("Z", "+00:00"))
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        return exp < datetime.now(timezone.utc)
    except Exception:
        return True


def cleanup_expired_sessions() -> int:
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        cur = conn.execute(
            "DELETE FROM user_sessions WHERE expires_at < ? OR revoked = 1",
            (now,),
        )
        deleted = int(cur.rowcount or 0)
    if deleted:
        log.info("Cleaned up %d expired/revoked sessions", deleted)
    return deleted


# setup wizard

def upsert_profile(user_id: int, payload: dict[str, Any]) -> None:
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
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


def replace_rows(user_id: int, table: str, rows: list[dict[str, Any]]) -> None:
    allowed: dict[str, list[str]] = {
        "education": ["university", "degree", "branch", "cgpa", "start_year", "end_year"],
        "coding_platforms": ["platform_name", "username", "profile_link"],
        "profile_projects": ["source", "title", "description", "tech_stack", "github_link", "live_link"],
        "internships": ["company", "role", "start_date", "end_date", "description", "technologies_used"],
        "certifications": ["certificate_name", "provider", "certificate_link", "issue_date"],
        "training": ["course_name", "institution", "skills_learned", "duration"],
    }
    if table not in allowed:
        raise ValueError("Invalid table")
    cols = allowed[table]
    now = datetime.now(timezone.utc).isoformat()
    placeholders = ",".join(["?"] * (len(cols) + 2))
    col_sql = ", ".join(["user_id"] + cols + ["created_at"])
    with get_db() as conn:
        conn.execute(f"DELETE FROM {table} WHERE user_id=?", (user_id,))
        for row in rows or []:
            vals = [user_id] + [row.get(c) for c in cols] + [now]
            conn.execute(f"INSERT INTO {table} ({col_sql}) VALUES ({placeholders})", vals)


def get_profile_bundle(user_id: int) -> dict[str, Any]:
    with get_db() as conn:
        profile = conn.execute("SELECT * FROM profiles WHERE user_id=?", (user_id,)).fetchone()
        edu = conn.execute("SELECT * FROM education WHERE user_id=? ORDER BY id DESC", (user_id,)).fetchall()
        platforms = conn.execute("SELECT * FROM coding_platforms WHERE user_id=? ORDER BY id DESC", (user_id,)).fetchall()
        projects = conn.execute("SELECT * FROM profile_projects WHERE user_id=? ORDER BY id DESC", (user_id,)).fetchall()
        internships = conn.execute("SELECT * FROM internships WHERE user_id=? ORDER BY id DESC", (user_id,)).fetchall()
        certs = conn.execute("SELECT * FROM certifications WHERE user_id=? ORDER BY id DESC", (user_id,)).fetchall()
        training = conn.execute("SELECT * FROM training WHERE user_id=? ORDER BY id DESC", (user_id,)).fetchall()
        github = conn.execute("SELECT * FROM github_data WHERE user_id=?", (user_id,)).fetchone()
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


def upsert_github_data(user_id: int, payload: dict[str, Any]) -> None:
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO github_data (user_id, profile_link, repositories, stars, languages, projects, contributions, raw_data, fetched_at)
            VALUES (?,?,?,?,?,?,?,?,?)
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
                datetime.now(timezone.utc).isoformat(),
            ),
        )


def mark_setup_completed(user_id: int) -> None:
    with get_db() as conn:
        conn.execute("UPDATE profiles SET setup_completed=1, updated_at=? WHERE user_id=?", (datetime.now(timezone.utc).isoformat(), user_id))


# templates + dynamic resumes

def create_template(user_id: int, template_name: str, template_file: str, template_type: str) -> int:
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO resume_templates (user_id, template_name, template_file, template_type, created_at) VALUES (?,?,?,?,?)",
            (user_id, template_name, template_file, template_type, datetime.now(timezone.utc).isoformat()),
        )
        return int(cur.lastrowid)


def list_templates(user_id: int) -> list[dict[str, Any]]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT template_id, template_name, template_file, template_type, created_at FROM resume_templates WHERE user_id=? ORDER BY created_at DESC",
            (user_id,),
        ).fetchall()
    return [dict(r) for r in rows]


def create_resume_config(user_id: int, payload: dict[str, Any]) -> int:
    with get_db() as conn:
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
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        return int(cur.lastrowid)


def log_generated_resume(user_id: int, config_id: int | None, template_id: int | None, file_path: str, file_type: str) -> int:
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO generated_resumes (user_id, config_id, template_id, file_path, file_type, created_at) VALUES (?,?,?,?,?,?)",
            (user_id, config_id, template_id, file_path, file_type, datetime.now(timezone.utc).isoformat()),
        )
        return int(cur.lastrowid)


def list_generated_resumes(user_id: int, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
    q = "SELECT id, config_id, template_id, file_path, file_type, created_at FROM generated_resumes WHERE user_id=? ORDER BY created_at DESC"
    args: list[Any] = [user_id]
    if limit is not None:
        q += " LIMIT ? OFFSET ?"
        args.extend([limit, offset])
    with get_db() as conn:
        rows = conn.execute(q, tuple(args)).fetchall()
    return [dict(r) for r in rows]


def count_generated_resumes(user_id: int) -> int:
    with get_db() as conn:
        row = conn.execute("SELECT COUNT(*) AS c FROM generated_resumes WHERE user_id=?", (user_id,)).fetchone()
    return int(row["c"] if row else 0)


def get_generated_resume(user_id: int, resume_id: int) -> dict[str, Any] | None:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM generated_resumes WHERE user_id=? AND id=?", (user_id, resume_id)).fetchone()
    return dict(row) if row else None


def list_user_ids() -> list[int]:
    with get_db() as conn:
        rows = conn.execute("SELECT id FROM users ORDER BY id ASC").fetchall()
    return [int(r["id"]) for r in rows]


# ai cache

def get_ai_cache(cache_key: str) -> dict[str, Any] | None:
    with get_db() as conn:
        row = conn.execute("SELECT content FROM ai_cache WHERE cache_key=?", (cache_key,)).fetchone()
    if not row:
        return None
    try:
        return json.loads(row["content"])
    except Exception:
        return None


def set_ai_cache(cache_key: str, section: str, content: dict[str, Any]) -> None:
    with get_db() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO ai_cache (cache_key, section, content, generated_at) VALUES (?,?,?,?)",
            (cache_key, section, json.dumps(content), datetime.now(timezone.utc).isoformat()),
        )


# email verification + password reset

def create_email_verification(user_id: int, token: str, expires_at: str) -> None:
    with get_db() as conn:
        conn.execute(
            "INSERT INTO email_verifications (user_id, token, expires_at, used, created_at) VALUES (?,?,?,?,?)",
            (user_id, token, expires_at, 0, datetime.now(timezone.utc).isoformat()),
        )


def get_email_verification(token: str) -> dict[str, Any] | None:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM email_verifications WHERE token=?", (token,)).fetchone()
    return dict(row) if row else None


def mark_email_verification_used(token: str) -> None:
    with get_db() as conn:
        conn.execute("UPDATE email_verifications SET used=1 WHERE token=?", (token,))


def create_password_reset(user_id: int, token: str, expires_at: str) -> None:
    with get_db() as conn:
        conn.execute(
            "INSERT INTO password_resets (user_id, token, expires_at, used, created_at) VALUES (?,?,?,?,?)",
            (user_id, token, expires_at, 0, datetime.now(timezone.utc).isoformat()),
        )


def get_password_reset(token: str) -> dict[str, Any] | None:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM password_resets WHERE token=?", (token,)).fetchone()
    return dict(row) if row else None


def mark_password_reset_used(token: str) -> None:
    with get_db() as conn:
        conn.execute("UPDATE password_resets SET used=1 WHERE token=?", (token,))


def update_user_password(user_id: int, password_hash: str) -> None:
    with get_db() as conn:
        conn.execute("UPDATE users SET password_hash=? WHERE id=?", (password_hash, user_id))
