# CareerForge

> AI-powered developer career platform — profile-first onboarding, dynamic resume generation, job tracking, and AI writing with **FastAPI + Next.js + Groq**.

![Dashboard](https://img.shields.io/badge/Status-v2.0.0--stable-brightgreen) ![Python](https://img.shields.io/badge/Python-3.13-blue) ![Next.js](https://img.shields.io/badge/Next.js-16-black) ![License](https://img.shields.io/badge/License-MIT-purple)

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
Frontend:  Next.js 16  (pages router, modern professional UI)
Backend:   FastAPI     (Python 3.13, async, Swagger UI at /docs)
Database:  SQLite      (career.db — projects, resumes, jobs, stats)
AI:        Groq Cloud  (llama-3.1-8b-instant — free tier, fast)
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

### 3. Configure (Secure)
Do not put secrets in `config.yaml`.

Create `.env` from `.env.example`:
```bash
copy .env.example .env
```

Set these values in `.env`:
```env
GROQ_API_KEY=your_real_groq_key
JWT_SECRET=use_a_long_random_secret
JWT_ALGORITHM=HS256
JWT_EXP_MINUTES=120
```

Profile defaults can still be configured in `config.yaml`.

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
careerforge/
├── backend/
│   ├── main.py                   # FastAPI entry point
│   ├── database/models.py        # SQLite schema & queries
│   ├── services/
│   │   ├── ai_engine.py          # Groq AI wrapper
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
  └─► Groq Cloud — llama-3.1-8b-instant, free tier
```

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

## New Career Platform APIs

The platform now supports a multi-user career profile workflow:

- `POST /api/auth/signup`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/auth/logout`
- `POST /api/profile/setup` (career setup wizard)
- `GET /api/profile/me`
- `POST /api/templates/upload`
- `GET /api/templates`
- `POST /api/dynamic-resume/generate`
- `GET /api/dynamic-resume/history`
- `GET /api/dynamic-resume/download/{id}`
- `POST /api/platforms/sync`
- `POST /api/ai/improve-bullet`

---

## License

MIT — free to use, modify, and distribute.
