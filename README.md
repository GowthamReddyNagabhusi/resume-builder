# CareerForge — AI-Powered Resume Builder & Career Platform

<div align="center">

**Build ATS-optimized, role-specific resumes in seconds — not hours.**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.135-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-000000?logo=next.js&logoColor=white)](https://nextjs.org)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](https://reactjs.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

[Live Demo](#live-deployment) · [Quick Start](#-quick-start) · [API Docs](#-api-reference) · [Architecture](#-architecture)

</div>

---

## 📌 About

**CareerForge** is a full-stack career platform that transforms how professionals create resumes. Instead of manually writing and reformatting for every application, users enter their career data once — education, experience, skills, projects, certifications — and CareerForge's AI pipeline generates tailored, ATS-optimized resumes for any target role.

### Key Capabilities

| Feature | Description |
|---------|-------------|
| 🤖 **AI Resume Generation** | Paste a job description → get a tailored resume with optimized bullet points, keyword matching, and ATS formatting |
| 📊 **Career Data Management** | Full CRUD for education, experience, skills, projects, certifications, and achievements |
| 🔗 **GitHub Integration** | Import repositories, contributions, and profile data directly into your career profile |
| 📈 **Career Roadmaps** | AI-powered career progression paths with skill gap analysis |
| 🎨 **Template System** | Multiple resume templates with customizable layouts |
| 📋 **Job Tracker** | Track applications, statuses, and notes across your job search |
| 📄 **Export Options** | Generate resumes in PDF and DOCX formats |

---

## 🏗 Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                         Client                               │
│                    Next.js 14 / React 18                      │
│          Tailwind CSS · Zustand · React Hook Form             │
└──────────────────────┬───────────────────────────────────────┘
                       │ HTTPS / REST
┌──────────────────────▼───────────────────────────────────────┐
│                    FastAPI Backend                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────┐  │
│  │   Auth   │ │  Career  │ │  Resume  │ │  Integrations  │  │
│  │  (JWT)   │ │   CRUD   │ │ Generate │ │  GitHub/APIs   │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └───────┬────────┘  │
│       │             │            │                │           │
│  ┌────▼─────────────▼────────────▼────────────────▼────────┐ │
│  │              Service Layer                              │ │
│  │  ai_engine · resume_builder · github_parser             │ │
│  │  dynamic_resume_builder · platform_sync                 │ │
│  └────────────────────┬───────────────────────────────────┘ │
│                       │                                      │
│  ┌────────────────────▼───────────────────────────────────┐ │
│  │  Core: security · settings · rate_limit · exceptions   │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────┬───────────────────────────────────────┘
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
   ┌───────────┐ ┌──────────┐ ┌──────────────┐
   │ SQLite /  │ │  Redis   │ │ AI Providers │
   │PostgreSQL │ │  Cache   │ │ OpenAI/      │
   │           │ │          │ │ Anthropic/   │
   │           │ │          │ │ Google/Groq  │
   └───────────┘ └──────────┘ └──────────────┘
```

### Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | Next.js 14, React 18, Tailwind CSS, Zustand, React Hook Form, Axios, jsPDF, html2canvas |
| **Backend** | Python 3.10+, FastAPI, SQLAlchemy, Alembic, Pydantic, SlowAPI |
| **AI** | OpenAI, Anthropic, Google GenAI — modular provider pattern with mock fallback |
| **Database** | SQLite (dev) / PostgreSQL (prod) |
| **Cache** | Redis |
| **Auth** | JWT with refresh tokens, bcrypt password hashing |
| **Infra** | Docker, Docker Compose, GitHub Actions CI, Vercel (frontend + serverless backend) |
| **Docs** | Swagger UI / ReDoc (auto-generated from FastAPI) |

> For a deep-dive into the system design, data model, and AI pipeline, see [`ARCHITECTURE_DESIGN.md`](./ARCHITECTURE_DESIGN.md).

---

## ⚡ Quick Start

### Prerequisites

- **Python 3.10+**
- **Node.js 18+** and npm
- **Docker & Docker Compose** *(optional, for containerized setup)*

### Option 1 — Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/GowthamReddyNagabhusi/resume-builder.git
cd resume-builder

# Copy environment config
cp .env.example .env

# Start all services (PostgreSQL, Redis, Backend, Frontend, PgAdmin)
docker-compose up --build -d
```

### Option 2 — Manual Setup

```bash
# Clone
git clone https://github.com/GowthamReddyNagabhusi/resume-builder.git
cd resume-builder

# Environment
cp .env.example .env
# Edit .env — at minimum set JWT_SECRET or SECRET_KEY

# Backend (Terminal 1)
cd backend
pip install -r requirements.txt
cd ..
python -m uvicorn backend.main:app --reload --port 8000

# Frontend (Terminal 2)
cd frontend
npm install
npm run dev
```

### Option 3 — Windows Batch Scripts

```bash
./start_backend.bat     # Terminal 1
./start_frontend.bat    # Terminal 2
```

### Access Points

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| PgAdmin | http://localhost:5050 *(Docker only)* |

---

## 🔑 Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# ── Required ──────────────────────────────────────
SECRET_KEY=<generate: python -c "import secrets; print(secrets.token_hex(32))">

# ── Database ──────────────────────────────────────
DATABASE_URL=postgresql://resume_user:resume_password@localhost:5432/resume_builder
# Falls back to SQLite (data/career.db) if not set

# ── AI Providers (at least one for AI features) ───
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
# Set AI_PROVIDER=mock to use the mock provider without real API keys

# ── Optional ──────────────────────────────────────
REDIS_URL=redis://localhost:6379/0
CORS_ORIGINS=http://localhost:3000
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...
SENTRY_DSN=...
PROMETHEUS_ENABLED=false
```

See [`.env.example`](./.env.example) for the full list.

---

## 📡 API Reference

All endpoints are documented via Swagger UI at `/docs`. Below is a summary:

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/signup` | Register a new user |
| `POST` | `/api/auth/login` | Login and receive JWT tokens |
| `POST` | `/api/auth/refresh` | Refresh an expired access token |
| `GET` | `/api/auth/me` | Get the authenticated user's profile |

### Career Data (CRUD for each type)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET/POST` | `/api/career/education` | List or add education entries |
| `GET/POST` | `/api/career/experience` | List or add work experience |
| `GET/POST` | `/api/career/skills` | List or add skills |
| `GET/POST` | `/api/career/projects` | List or add projects |
| `GET/POST` | `/api/career/certifications` | List or add certifications |
| `GET/POST` | `/api/career/achievements` | List or add achievements |
| `PUT/DELETE` | `/api/career/{type}/{id}` | Update or delete a specific entry |

### Resume

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/resume/generate` | Generate an AI-tailored resume |
| `GET` | `/api/resume/list` | List saved resumes |
| `POST` | `/api/dynamic-resume/generate` | Dynamic resume generation |

### Other

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/ai/generate` | AI content generation |
| `GET` | `/api/github/user` | Import GitHub profile data |
| `GET/POST` | `/api/jobs` | Job application tracker |
| `GET` | `/api/stats` | User statistics dashboard |
| `GET` | `/api/profile` | User profile management |
| `GET` | `/api/templates` | Resume template listing |
| `GET` | `/health` | Health check with DB status and uptime |

<details>
<summary><strong>Example: Generate a Resume</strong></summary>

```bash
# 1. Sign up
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "SecurePass123", "name": "Jane Doe"}'

# 2. Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "SecurePass123"}' | jq -r '.access_token')

# 3. Generate resume
curl -X POST http://localhost:8000/api/resume/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "job_role": "Senior Software Engineer",
    "job_description": "We are looking for an experienced Python developer with cloud and API design skills..."
  }'
```

</details>

---

## 📁 Project Structure

```
resume-builder/
├── backend/                    # Python FastAPI backend
│   ├── api/                    # Route handlers
│   │   ├── auth.py             #   Authentication & JWT
│   │   ├── career.py           #   Career data CRUD
│   │   ├── resume.py           #   Resume generation
│   │   ├── dynamic_resume.py   #   Dynamic resume builder
│   │   ├── ai.py               #   AI content endpoints
│   │   ├── github.py           #   GitHub integration
│   │   ├── jobs.py             #   Job application tracker
│   │   ├── profile.py          #   User profile
│   │   ├── stats.py            #   Statistics
│   │   ├── templates.py        #   Resume templates
│   │   └── platforms.py        #   Platform integrations
│   ├── services/               # Business logic
│   │   ├── ai_engine.py        #   Multi-provider AI orchestration
│   │   ├── resume_builder.py   #   Resume compilation pipeline
│   │   ├── dynamic_resume_builder.py
│   │   ├── github_parser.py    #   GitHub API data parser
│   │   └── platform_sync.py    #   External platform sync
│   ├── core/                   # Infrastructure
│   │   ├── security.py         #   JWT, password hashing
│   │   ├── settings.py         #   App configuration
│   │   ├── deps.py             #   Dependency injection
│   │   ├── rate_limit.py       #   Rate limiting
│   │   ├── logger.py           #   Structured logging
│   │   └── exceptions.py       #   Error handlers
│   ├── database/               # Data layer
│   │   └── models.py           #   SQLAlchemy ORM models
│   ├── main.py                 # FastAPI app entry point
│   └── requirements.txt        # Python dependencies
├── frontend/                   # Next.js frontend
│   ├── src/
│   │   ├── pages/              # Page routes
│   │   │   ├── index.js        #   Landing page
│   │   │   ├── dashboard.js    #   User dashboard
│   │   │   ├── auth/           #   Login & signup
│   │   │   ├── career/         #   Career data management
│   │   │   └── resume/         #   Resume generation & listing
│   │   ├── components/         # Reusable UI components
│   │   │   ├── common/         #   Shared components
│   │   │   ├── forms/          #   Form components
│   │   │   ├── layout/         #   Layout wrappers
│   │   │   └── resume/         #   Resume-specific components
│   │   ├── lib/                # Utilities & API client
│   │   ├── hooks/              # Custom React hooks
│   │   └── styles/             # CSS stylesheets
│   ├── package.json
│   └── tailwind.config.js
├── tests/                      # Backend test suite
│   ├── test_auth.py
│   ├── test_resume.py
│   ├── test_jobs.py
│   └── test_security.py
├── infra/docker/               # Docker configurations
├── docs/                       # Extended documentation
│   ├── API.md                  #   Full API reference
│   ├── DEPLOYMENT.md           #   Deployment guide
│   ├── QUICKSTART.md           #   Quick start guide
│   ├── SECURITY.md             #   Security practices
│   ├── CONTRIBUTING.md         #   Contribution guidelines
│   └── AI_PIPELINE.md          #   AI pipeline details
├── alembic/                    # Database migrations
├── scripts/                    # Setup scripts (bash & bat)
├── data/                       # SQLite database (dev)
├── docker-compose.yml          # Multi-service dev environment
├── ARCHITECTURE_DESIGN.md      # System design document
├── CHANGELOG.md                # Version history
└── .github/workflows/          # CI/CD pipeline
```

---

## 🧪 Testing

```bash
# Backend tests
pytest tests/

# With coverage
pytest --cov=backend tests/

# Frontend tests
cd frontend && npm test

# Watch mode
cd frontend && npm run test:watch
```

---

## 🚀 Deployment

### Vercel (Current)

The project is configured for Vercel deployment with serverless functions:
- **Frontend**: Deployed as a Next.js app
- **Backend**: Deployed as serverless Python functions via `vercel.json`

### Docker (Self-hosted)

```bash
docker-compose up -d
```

Services: PostgreSQL, Redis, Backend, Frontend, PgAdmin — all connected via `resume_builder_network`.

### Cloud (AWS / Azure / Kubernetes)

See [`docs/DEPLOYMENT.md`](./docs/DEPLOYMENT.md) for production deployment guides covering ECS, App Service, and K8s.

---

## 🔒 Security

- **Authentication**: JWT access + refresh tokens
- **Password Hashing**: bcrypt via passlib
- **Rate Limiting**: Per-user and per-IP via SlowAPI
- **Input Validation**: Pydantic models for all request bodies
- **CORS**: Configurable allowed origins with regex support
- **Security Headers**: X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, CSP, Referrer-Policy
- **SQL Injection Protection**: SQLAlchemy ORM parameterized queries
- **XSS Prevention**: React auto-escaping + Content Security Policy
- **Session Cleanup**: Automatic expired session purging

See [`docs/SECURITY.md`](./docs/SECURITY.md) for the full security policy.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m "feat: add new feature"`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

See [`docs/CONTRIBUTING.md`](./docs/CONTRIBUTING.md) for detailed guidelines, code style, and PR templates.

---

## 🗺 Roadmap

- [x] Core resume generation with AI
- [x] Career data CRUD (education, experience, skills, projects, certifications, achievements)
- [x] JWT authentication with refresh tokens
- [x] GitHub profile integration
- [x] Job application tracker
- [x] Docker Compose dev environment
- [x] Vercel serverless deployment
- [ ] PDF / DOCX export
- [ ] Cover letter generation
- [ ] Interview coaching AI
- [ ] Job board integration & auto-matching
- [ ] Resume analytics dashboard
- [ ] Team collaboration features
- [ ] Mobile app (React Native)
- [ ] Kubernetes production manifests

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](./LICENSE) file for details.

---

<div align="center">
  <strong>Built by <a href="https://github.com/GowthamReddyNagabhusi">Gowtham Reddy Nagabhusi</a></strong>
</div>
