"""
database.py — SQLite layer for career-agent
All persistent data lives here.
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "career.db"


def get_conn():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()

    # Stats snapshots
    c.execute("""
        CREATE TABLE IF NOT EXISTS stats_snapshots (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            source      TEXT NOT NULL,          -- 'github' | 'codeforces' | 'leetcode'
            data        TEXT NOT NULL,          -- JSON blob
            fetched_at  TEXT NOT NULL
        )
    """)

    # Projects pulled from GitHub
    c.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT UNIQUE NOT NULL,
            description TEXT,
            language    TEXT,
            stars       INTEGER DEFAULT 0,
            url         TEXT,
            show_on_resume INTEGER DEFAULT 1,
            updated_at  TEXT
        )
    """)

    # Manual additions via Telegram
    c.execute("""
        CREATE TABLE IF NOT EXISTS manual_skills (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            skill TEXT UNIQUE NOT NULL,
            added_at TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS manual_certs (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            cert  TEXT NOT NULL,
            added_at TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS manual_experience (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            entry    TEXT NOT NULL,
            added_at TEXT
        )
    """)

    # Resume generation log
    c.execute("""
        CREATE TABLE IF NOT EXISTS resume_log (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            path       TEXT,
            generated_at TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("[DB] Initialized.")


# ── Stats ──────────────────────────────────────────────────

def save_snapshot(source: str, data: dict):
    conn = get_conn()
    conn.execute(
        "INSERT INTO stats_snapshots (source, data, fetched_at) VALUES (?,?,?)",
        (source, json.dumps(data), datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def get_latest_snapshot(source: str):
    conn = get_conn()
    row = conn.execute(
        "SELECT data FROM stats_snapshots WHERE source=? ORDER BY fetched_at DESC LIMIT 1",
        (source,)
    ).fetchone()
    conn.close()
    return json.loads(row["data"]) if row else {}


# ── Projects ───────────────────────────────────────────────

def upsert_project(name, description, language, stars, url):
    conn = get_conn()
    conn.execute("""
        INSERT INTO projects (name, description, language, stars, url, updated_at)
        VALUES (?,?,?,?,?,?)
        ON CONFLICT(name) DO UPDATE SET
            description=excluded.description,
            language=excluded.language,
            stars=excluded.stars,
            url=excluded.url,
            updated_at=excluded.updated_at
    """, (name, description, language, stars, url, datetime.now().isoformat()))
    conn.commit()
    conn.close()


def get_projects(limit=6):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM projects WHERE show_on_resume=1 ORDER BY stars DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Manual additions ───────────────────────────────────────

def add_skill(skill: str):
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO manual_skills (skill, added_at) VALUES (?,?)",
            (skill.strip(), datetime.now().isoformat())
        )
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
    conn.execute(
        "INSERT INTO manual_certs (cert, added_at) VALUES (?,?)",
        (cert.strip(), datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def get_certs():
    conn = get_conn()
    rows = conn.execute("SELECT cert FROM manual_certs ORDER BY added_at DESC").fetchall()
    conn.close()
    return [r["cert"] for r in rows]


def add_experience(entry: str):
    conn = get_conn()
    conn.execute(
        "INSERT INTO manual_experience (entry, added_at) VALUES (?,?)",
        (entry.strip(), datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def get_experience():
    conn = get_conn()
    rows = conn.execute("SELECT entry FROM manual_experience ORDER BY added_at DESC").fetchall()
    conn.close()
    return [r["entry"] for r in rows]


# ── Resume log ─────────────────────────────────────────────

def log_resume(path: str):
    conn = get_conn()
    conn.execute(
        "INSERT INTO resume_log (path, generated_at) VALUES (?,?)",
        (path, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
