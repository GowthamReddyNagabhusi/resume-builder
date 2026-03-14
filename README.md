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
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **AI Integration**: OpenAI/Anthropic APIs with modular fallbacks
- **Caching**: Redis
- **Authentication**: JWT + OAuth2

**Frontend**:
- **Framework**: Next.js (React)
- **Styling**: Tailwind CSS
- **State Management**: Zustand/React Context
- **HTTP Client**: Axios

**Infrastructure**:
- **Containerization**: Docker
- **Orchestration**: Docker Compose (dev), Kubernetes (production)
- **CI/CD**: GitHub Actions
- **Cloud**: AWS/Azure ready

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

- Docker & Docker Compose
- Git
- Python 3.11+ (for local development without Docker)
- Node.js 18+ (for frontend development)

### Local Development (Recommended)

**Using Docker** (simplest):

```bash
# Clone repository
git clone https://github.com/yourusername/resume-builder.git
cd resume-builder

# Run setup script
./scripts/setup.sh  # Linux/Mac
# or
.\scripts\setup.bat  # Windows

# Navigate to http://localhost:3000
```

**Without Docker**:

See [Local Setup Guide](./docs/setup/LOCAL_SETUP.md)

### Common Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down

# Access services
API: http://localhost:8000
API Docs: http://localhost:8000/docs
Frontend: http://localhost:3000
Database Admin: http://localhost:5050
```

---

## API Documentation

The API is fully documented with interactive Swagger UI:

**Swagger UI**: http://localhost:8000/docs
**ReDoc**: http://localhost:8000/redoc

### Example API Calls

**Generate Resume**:

```bash
curl -X POST http://localhost:8000/api/v1/resumes/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "We are looking for a Python developer...",
    "template_id": "modern",
    "title": "Software Engineer - XYZ Company"
  }'
```

**Get Career Data**:

```bash
curl http://localhost:8000/api/v1/career/summary \
  -H "Authorization: Bearer YOUR_TOKEN"
```

See API documentation for complete endpoint reference.

---

## Development Workflow

### Project Structure

```
resume-builder/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API endpoint handlers
│   │   ├── ai/          # AI pipeline modules
│   │   ├── services/    # Business logic layer
│   │   ├── database/    # Database models
│   │   └── core/        # Configuration, exceptions, security
│   ├── requirements.txt
│   └── tests/
├── frontend/            # Next.js frontend
│   ├── src/
│   │   ├── pages/       # Page components
│   │   ├── components/  # Reusable components
│   │   ├── lib/         # Utilities and API client
│   │   └── styles/      # CSS
│   ├── package.json
│   └── public/
├── infra/              # Infrastructure configuration
│   ├── docker/         # Dockerfiles
│   ├── kubernetes/     # K8s manifests
│   └── terraform/      # IaC templates
├── docs/               # Documentation
├── docker-compose.yml  # Local development
└── README.md
```

### Code Style

- **Python**: Black, isort, pylint
- **JavaScript**: Prettier, ESLint
- **Git Hooks**: Pre-commit hooks for linting

```bash
# Format code
npm run format              # Frontend
black backend/             # Backend

# Lint
npm run lint               # Frontend
pylint backend/            # Backend

# Test
npm test                   # Frontend
pytest backend/            # Backend
```

---

## Deployment

### Local Development

```bash
docker-compose up -d
```

### Cloud Deployment

The system is designed for cloud deployment. See [Deployment Guide](./docs/DEPLOYMENT.md) for:

- **AWS Deployment**: ECS, RDS, S3
- **Azure Deployment**: App Service, Database, Blob Storage
- **Kubernetes**: Full K8s setup with manifests
- **CI/CD**: GitHub Actions pipelines

---

## Environment Variables

See [.env.example](./.env.example) for all available configuration options.

Key variables:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/resume_builder

# AI Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Application
SECRET_KEY=your-secret-key
DEBUG=False

# External APIs
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...
```

---

## Testing

### Backend Tests

```bash
# Run all tests
pytest backend/

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
