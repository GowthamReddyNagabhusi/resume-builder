# Resume Builder - AI-Powered Resume Compiler

## Overview

**Resume Builder** is an enterprise-grade, AI-powered platform that compiles resumes automatically. Instead of manually writing resumes for each job application, users provide structured career data once, and the system automatically generates role-specific, ATS-optimized resumes using advanced AI.

### Key Features

- **Career Data Compiler**: Store all career information (education, experience, skills, projects, certifications) in one place
- **AI-Powered Resume Generation**: Automatically generate role-specific resumes tailored to job descriptions
- **External Platform Integration**: Connect GitHub, LeetCode, Codeforces, and other platforms to automatically import career data
- **Template System**: Multiple professionally-designed resume templates
- **ATS Optimization**: AI-powered optimization for Applicant Tracking Systems
- **Multi-User SaaS**: Secure authentication and multi-user support
- **Cloud-Ready**: Designed for scalable deployment to AWS, Azure, or other cloud providers

### Why Resume Builder?

**Problem**: Creating tailored resumes for each job application is time-consuming and repetitive.

**Solution**: Provide structured career data once. The system compiles role-specific, optimized resumes using AI.

**Result**: Spend more time applying to jobs, less time writing resumes.

---

## System Architecture

### Technology Stack

**Backend**:
- **Framework**: FastAPI (Python async framework)
- **Database**: SQLite (local), PostgreSQL-ready for production
- **ORM**: SQLAlchemy ORM with raw SQL support
- **AI Integration**: Groq API (free, fast), OpenAI/Anthropic fallbacks
- **Authentication**: JWT tokens with refresh support
- **Rate Limiting**: Token-bucket based
- **Logging**: Structured JSON logging

**Frontend**:
- **Framework**: Next.js 16+ (React 18)
- **Styling**: Tailwind CSS with @tailwindcss/forms
- **State Management**: React Context API
- **HTTP Client**: Fetch API with custom client
- **Form Handling**: React Hook Form
- **Auth Context**: Custom AuthContext provider

**Infrastructure**:
- **Containerization**: Docker
- **Deployment**: Docker Compose or standalone
- **CI/CD**: GitHub Actions ready
- **Cloud**: AWS/Azure compatible

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                      │
│  Pages: Auth, Dashboard, Career Data, Resume Generation   │
└─────────────────────────────────────────────────────────────┘
                              ↓ (HTTPS/REST)
┌─────────────────────────────────────────────────────────────┐
│                   Backend API (FastAPI)                     │
│  Routes: Auth, Career Data, Resume, Integrations, Admin   │
└─────────────────────────────────────────────────────────────┘
                              ↓
     ┌────────────────────────┼────────────────────────┐
     ↓                        ↓                        ↓
┌──────────┐          ┌──────────────┐         ┌──────────────┐
│PostgreSQL│          │ AI Pipeline  │         │     Redis    │
│Database  │          │  (Multi-LLM) │         │  (Cache)     │
└──────────┘          └──────────────┘         └──────────────┘
                              ↓
              ┌──────────────────────────────┐
              │  External Platform APIs      │
              │ GitHub, LeetCode, etc        │
              └──────────────────────────────┘
```

For detailed architecture, see [ARCHITECTURE_DESIGN.md](./ARCHITECTURE_DESIGN.md).

---

## Quick Start

### Prerequisites

- Python 3.11+ (for local development)
- Node.js 18+ (for frontend)
- Git
- Windows/Mac/Linux

### Local Development (Recommended)

**Quickest Setup**:

```bash
# Clone repository
git clone https://github.com/yourusername/resume-builder.git
cd resume-builder

# Windows: Run startup scripts
./start_backend.bat     # Terminal 1
./start_frontend.bat    # Terminal 2

# Linux/Mac:
python -m uvicorn backend.main:app --reload --port 8000  # Terminal 1
cd frontend && npm run dev                                # Terminal 2
```

**With Docker**:

```bash
docker-compose up -d
```

### Access the Application

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | User interface |
| Backend API | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/docs | Interactive Swagger UI |
| Database | `data/career.db` | SQLite database |

### Environment Setup

```bash
# Create .env file (copy from .env.example)
cp .env.example .env

# Required variables:
# JWT_SECRET - Generate: python -c "import secrets; print(secrets.token_hex(32))"
# GROQ_API_KEY - Get free key at https://console.groq.com
```

---

## API Documentation

The API is fully documented with interactive Swagger UI:

**Swagger UI**: http://localhost:8000/docs
**ReDoc**: http://localhost:8000/redoc

### Main Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/api/auth/signup` | Register new user |
| `POST` | `/api/auth/login` | User login |
| `POST` | `/api/auth/refresh` | Refresh JWT token |
| `GET` | `/api/auth/me` | Get current user |
| `POST` | `/api/resume/generate` | Generate AI resume |
| `GET` | `/api/resume/list` | List saved resumes |
| `GET` | `/api/jobs` | Get job applications |
| `POST` | `/api/jobs` | Add job application |
| `GET` | `/api/ai/generate` | AI content generation |
| `GET` | `/api/github/user` | GitHub profile import |
| `GET` | `/api/stats` | User statistics |

### Example API Calls

**User Signup**:

```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123",
    "name": "John Doe"
  }'
```

**Generate Resume**:

```bash
curl -X POST http://localhost:8000/api/resume/generate \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "job_role": "Senior Software Engineer",
    "job_description": "We seek an experienced Python/Go developer..."
  }'
```

**Get User Profile**:

```bash
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

See [API Documentation](./docs/API.md) for complete endpoint reference.

---

## Development Workflow

### Project Structure

```
resume-builder/
├── backend/                   # FastAPI backend
│   ├── api/                   # API endpoints
│   │   ├── auth.py
│   │   ├── resume.py
│   │   ├── jobs.py
│   │   ├── ai.py
│   │   ├── github.py
│   │   ├── profile.py
│   │   ├── stats.py
│   │   ├── templates.py
│   │   ├── dynamic_resume.py
│   │   └── platforms.py
│   ├── services/              # Business logic
│   │   ├── resume_builder.py
│   │   ├── ai_engine.py
│   │   ├── github_parser.py
│   │   └── platform_sync.py
│   ├── core/                  # Core modules
│   │   ├── security.py        # JWT, encryption
│   │   ├── settings.py        # Configuration
│   │   ├── deps.py            # Dependencies
│   │   ├── logger.py          # Logging
│   │   ├── rate_limit.py      # Rate limiting
│   │   └── exceptions.py      # Error handling
│   ├── database/              # Data layer
│   │   └── models.py          # SQLite models
│   ├── main.py                # Application entry
│   └── requirements.txt
├── frontend/                  # Next.js frontend
│   ├── src/
│   │   ├── pages/             # Page components
│   │   │   ├── auth/
│   │   │   ├── resume/
│   │   │   ├── career/
│   │   │   └── dashboard.js
│   │   ├── components/        # Reusable components
│   │   ├── lib/               # Utilities
│   │   │   ├── api/
│   │   │   ├── context/
│   │   │   └── utils/
│   │   ├── hooks/             # React hooks
│   │   └── styles/            # CSS
│   ├── package.json
│   └── public/
├── infra/                     # Infrastructure
│   ├── docker/                # Docker configs
│   └── kubernetes/            # K8s manifests
├── docs/                      # Documentation
│   ├── API.md
│   ├── ARCHITECTURE_DESIGN.md
│   ├── DEPLOYMENT.md
│   ├── QUICKSTART.md
│   └── SECURITY.md
├── tests/                     # Test suite
│   ├── test_auth.py
│   ├── test_resume.py
│   ├── test_jobs.py
│   └── test_security.py
├── data/                      # Data storage
│   └── career.db              # SQLite database
├── docker-compose.yml         # Local dev setup
├── start_backend.bat          # Windows start script
├── start_frontend.bat         # Windows start script
├── .env.example               # Environment template
└── README.md
```

### Code Style

- **Python**: Black, isort, pylint
- **JavaScript**: Prettier, ESLint, Next.js conventions

```bash
# Format code
cd frontend && npm run format    # Frontend
black backend/                   # Backend

# Lint
cd frontend && npm run lint      # Frontend

# Test
cd frontend && npm test          # Frontend
pytest tests/                    # Backend
```

---

## Deployment

### Local Development

```bash
# Terminal 1: Backend
./start_backend.bat

# Terminal 2: Frontend
./start_frontend.bat

# Or with Docker Compose:
docker-compose up -d
```

### Cloud Deployment

See [Deployment Guide](./docs/DEPLOYMENT.md) for:

- **AWS**: ECS, RDS, CloudFront
- **Azure**: App Service, SQL Database
- **Kubernetes**: Full K8s deployment with Helm
- **CI/CD**: GitHub Actions pipelines

---

## Environment Variables

See [.env.example](./.env.example) for all configuration options.

**Required Variables**:

```bash
# Security
JWT_SECRET=<generate-with: python -c "import secrets; print(secrets.token_hex(32))">
JWT_ALGORITHM=HS256
JWT_EXP_MINUTES=120

# AI Provider (Free Groq API)
GROQ_API_KEY=<get-free-key-at-https://console.groq.com>

# CORS & URLs
CORS_ALLOW_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
```

**Optional Variables**:

```bash
# Email (for verification & password reset)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password

# GitHub OAuth
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...

# Monitoring
PROMETHEUS_ENABLED=false
SENTRY_DSN=...
```

---

## Testing

### Backend Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=backend backend/

# Run specific test
pytest backend/tests/test_api/test_auth.py::test_login
```

### Frontend Tests

```bash
# Run tests
npm test

# Watch mode
npm run test:watch

# Coverage
npm test -- --coverage
```

---

## Security

- **Authentication**: JWT tokens with refresh tokens
- **Authorization**: Role-based access control
- **API Keys**: Encrypted storage
- **HTTPS**: Required in production
- **Rate Limiting**: Per-user and per-IP
- **Input Validation**: Server-side validation with Pydantic
- **CORS**: Configurable origins
- **SQL Injection**: Protected via SQLAlchemy ORM
- **XSS**: React auto-escaping + CSP headers

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Submit a Pull Request

---

## License

This project is licensed under the MIT License - see [LICENSE](./LICENSE) file for details.

---

## Support & Community

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Documentation**: [docs/](./docs/)

---

## Roadmap

- [ ] Cover letter generation
- [ ] Interview coaching AI
- [ ] Job board integration
- [ ] Resume analytics
- [ ] Team collaboration features
- [ ] Mobile app (React Native)
- [ ] Advanced customization options

---

**Start building better resumes today! 🚀**

## License

MIT — free to use, modify, and distribute.
