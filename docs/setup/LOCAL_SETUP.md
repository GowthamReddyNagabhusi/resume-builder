# Local Development Setup Guide

This guide walks you through setting up the Resume Builder project for local development.

## Prerequisites

### Required
- **Docker & Docker Compose**: [Install Docker](https://docs.docker.com/get-docker/)
- **Git**: [Install Git](https://git-scm.com/)

### Optional (for development without Docker)
- **Python 3.11+**: [Install Python](https://www.python.org/downloads/)
- **Node.js 18+**: [Install Node.js](https://nodejs.org/)
- **PostgreSQL 15**: [Install PostgreSQL](https://www.postgresql.org/download/)
- **Redis**: [Install Redis](https://redis.io/download)

## Setup with Docker (Recommended)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/resume-builder.git
cd resume-builder
```

### Step 2: Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your settings (optional for local dev)
# nano .env
```

### Step 3: Start Services

```bash
# Run setup script (automated)
./scripts/setup.sh   # Linux/Mac
# or
.\scripts\setup.bat  # Windows

# Or manually start services
docker-compose up -d
```

### Step 4: Verify Services

```bash
# Check service health
docker-compose ps

# Check backend health
curl http://localhost:8000/health

# Check frontend
open http://localhost:3000
```

### Services Endpoints

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | Web application |
| Backend API | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Database | localhost:5432 | PostgreSQL |
| Database Admin | http://localhost:5050 | PgAdmin (admin/admin) |
| Cache | localhost:6379 | Redis |

## Setup without Docker

### Backend

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Configure database
export DATABASE_URL="postgresql://user:password@localhost:5432/resume_builder"

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

Backend runs on `http://localhost:8000`

### Frontend

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs on `http://localhost:3000`

### Database Setup

```bash
# Create database and user
createuser resume_user
createdb -O resume_user resume_builder

# Run migrations
alembic upgrade head
```

## Common Development Tasks

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Formatting

```bash
# Backend
black backend/
isort backend/

# Frontend
npm run format
```

### Linting

```bash
# Backend
pylint backend/

# Frontend
npm run lint
```

### Database Management

```bash
# Check database connection
psql postgresql://resume_user:password@localhost:5432/resume_builder

# Create a backup
pg_dump -U resume_user resume_builder > backup.sql

# Restore from backup
psql -U resume_user resume_builder < backup.sql
```

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Stopping Services

```bash
# Stop but keep data
docker-compose down

# Stop and remove data
docker-compose down -v

# Stop specific service
docker stop resume_builder_backend
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # Linux/Mac
taskkill /PID <PID> /F  # Windows
```

### Database Connection Error

```bash
# Check PostgreSQL is running
psql --version

# Verify connection
psql postgresql://resume_user:password@localhost:5432/resume_builder

# Check DATABASE_URL in .env
echo $DATABASE_URL
```

### Docker Issues

```bash
# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check Docker is running
docker ps

# View error logs
docker-compose logs backend
```

### Frontend Not Loading

```bash
# Clear Next.js cache
rm -rf frontend/.next

# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install

# Try again
npm run dev
```

### Reset Everything

```bash
# Complete reset
docker-compose down -v
rm -rf backend/migrations/versions/*
docker-compose build --no-cache
docker-compose up -d
```

## Development Workflow

### Creating a Feature

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes and test
npm test       # Frontend
pytest backend # Backend

# Format code
npm run format
black backend/

# Commit and push
git add .
git commit -m "Add my feature"
git push origin feature/my-feature

# Create Pull Request on GitHub
```

### Database Migrations

```bash
# Generate migration
cd backend
alembic revision --autogenerate -m "Add new field"

# Review migration file
cat alembic/versions/<timestamp>_add_new_field.py

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

### Testing AI Pipeline Locally

```python
from app.ai import AIPipeline

# Use mock provider for testing
pipeline = AIPipeline(provider_name="mock")

# Test job analysis
result = pipeline.analyze_job_description(
    "We need a Python developer with FastAPI experience"
)
print(result)
```

## IDE Setup

### VS Code

Recommended extensions:
- Python
- Pylance
- ES Lint
- Prettier
- REST Client

Create `.vscode/settings.json`:

```json
{
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "ms-python.black-formatter"
  },
  "[javascript]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

### PyCharm

1. Configure Python Interpreter
2. Mark `backend/app` as Sources Root
3. Configure Run/Debug configurations
4. Enable Black formatter

## Next Steps

1. **Explore the codebase**: Check out [ARCHITECTURE_DESIGN.md](./ARCHITECTURE_DESIGN.md)
2. **API Documentation**: Visit http://localhost:8000/docs
3. **Create test user**: Sign up at http://localhost:3000
4. **Add career data**: Fill in your education, experience, etc.
5. **Generate resume**: Test the resume generation with a job description

## Getting Help

- Check logs: `docker-compose logs -f service_name`
- Read documentation: [docs/](../docs/)
- Search GitHub Issues
- Start a GitHub Discussion

---

Happy developing! 🚀
