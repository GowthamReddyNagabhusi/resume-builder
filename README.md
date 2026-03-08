# Antigravity Career Agent

> AI-powered career automation — resume builder, job tracker, GitHub import, cover letters. Built as a local-first Web SaaS using **FastAPI + Next.js + Groq AI**.

![Dashboard](https://img.shields.io/badge/Status-v1.0-brightgreen) ![Python](https://img.shields.io/badge/Python-3.13-blue) ![Next.js](https://img.shields.io/badge/Next.js-16-black) ![License](https://img.shields.io/badge/License-MIT-purple)

---

## What It Does

| Feature | Description |
|---|---|
| **Smart Resume Builder** | Picks your 2–3 best GitHub projects by stars, description quality, and recency. Generates FAANG-level bullet points via Groq AI. Exports as DOCX. |
| **Job Tracker** | Kanban board — track applications across Applied → Interview → Offer / Rejected |
| **GitHub Import** | Fetches all your repos. Toggle which ones appear on your resume. |
| **AI Writer** | Cover letter generator, resume improver, and freeform AI chat — all powered by Groq |
| **Live Stats Dashboard** | Auto-syncs your GitHub repos, Codeforces rating, and LeetCode solve count |

---

## Tech Stack

```
Frontend:  Next.js 16  (pages router, vanilla CSS, dark glassmorphism UI)
Backend:   FastAPI     (Python 3.13, async, Swagger UI at /docs)
Database:  SQLite      (career.db — projects, resumes, jobs, stats)
AI:        Groq Cloud  (llama-3.1-8b-instant — free tier, fast)
           Ollama WSL  (optional local fallback — llama3 / mistral)
Resume:    python-docx (DOCX output, A4 format, styled)
```

---

## Quick Start

### 1. Prerequisites
- Python 3.10+
- Node.js 18+
- A free [Groq API key](https://console.groq.com/keys)

### 2. Install Backend
```bash
pip install fastapi uvicorn[standard] python-docx pyyaml requests
```

### 3. Configure
Edit `config.yaml` — add your Groq key:
```yaml
groq:
  api_key: "gsk_your_key_here"

profile:
  github_username: "YourGitHubUsername"
  codeforces_handle: "your_cf_handle"
  leetcode_username: "your_lc_username"
```

### 4. Install Frontend
```bash
cd frontend
npm install
```

### 5. Run

**Terminal 1 — Backend:**
```bash
start_backend.bat          # Windows
# or: py -3 -m uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
start_frontend.bat         # Windows
# or: cd frontend && npm run dev
```

- **Dashboard:** http://localhost:3000
- **API Docs (Swagger):** http://localhost:8000/docs

---

## Project Structure

```
antigravity/
├── backend/
│   ├── main.py                   # FastAPI entry point
│   ├── database/models.py        # SQLite schema & queries
│   ├── services/
│   │   ├── ai_engine.py          # Groq AI wrapper (+ Ollama fallback)
│   │   ├── github_parser.py      # GitHub / Codeforces / LeetCode APIs
│   │   └── resume_builder.py     # Smart project picker + DOCX builder
│   └── api/
│       ├── resume.py             # POST /generate, GET /download
│       ├── ai.py                 # /generate, /cover-letter, /improve-resume
│       ├── github.py             # /import, /projects
│       ├── jobs.py               # Job tracker CRUD
│       └── stats.py              # Stats snapshots
├── frontend/
│   ├── pages/                    # index, resume, github, jobs, ai
│   ├── components/Layout.js      # Sidebar navigation
│   ├── lib/api.js                # API client
│   └── styles/globals.css        # Dark glassmorphism design system
├── scheduler.py                  # Background stats refresh daemon
├── config.yaml                   # User profile + API keys
├── start_backend.bat
└── start_frontend.bat
```

---

## AI — How It Works

```
Request
  │
  ├─► Groq Cloud (primary)   — llama-3.1-8b-instant, free 30 RPM
  └─► Ollama WSL (fallback)  — llama3/mistral, runs locally
```

No key? Run `ollama serve` in WSL and it works without Groq too.

---

## Smart Project Picker

The resume builder doesn't just dump all your repos. It scores each project:

| Signal | Weight |
|---|---|
| GitHub Stars | 30 pts |
| Description quality | 25 pts |
| Last updated (recency) | 20 pts |
| Has real language | 15 pts |
| Good project name | 10 pts |

Then picks **2–3 best projects** with language diversity (max 2 same language).

---

## Roadmap

- [ ] PostgreSQL migration
- [ ] Auth (Supabase)
- [ ] PDF export
- [ ] Docker deploy
- [ ] Portfolio website auto-generator

---

## License

MIT — free to use, modify, and distribute.
