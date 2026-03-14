# Development Quickstart

Get the Resume Builder project running in minutes.

## 5-Minute Setup (Docker)

```bash
# 1. Clone
git clone https://github.com/yourusername/resume-builder.git
cd resume-builder

# 2. Run setup script
./scripts/setup.sh  # macOS/Linux
# or
.\scripts\setup.bat  # Windows

# 3. Wait for initialization (2-3 minutes)

# 4. Open browser
# Frontend:  http://localhost:3000
# Backend:   http://localhost:8000
# API Docs:  http://localhost:8000/docs
```

Done! 🎉

## First Steps After Setup

### 1. Create Test User

Go to http://localhost:3000 and sign up:
- Email: `test@example.com`
- Password: `TestPassword123!`

### 2. Add Career Data

From the dashboard, add some sample data:
- **Education**: Add your degree
- **Experience**: Add a past job
- **Skills**: Add 5-10 skills
- **Projects**: Add a portfolio project

### 3. Try Resume Generation

1. Click "Generate Resume"
2. Paste a job description
3. Select "Modern" template
4. Click "Generate"

The system will create a tailored resume in seconds!

## Common Commands

```bash
# See all services
docker-compose ps

# View logs
docker-compose logs -f backend

# Restart a service
docker-compose restart backend

# Stop everything
docker-compose down

# Start again
docker-compose up -d
```

## Troubleshooting Setup

### Port Already in Use

```bash
# Find what's using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows
```

Kill the process or change ports in docker-compose.yml.

### Services Won't Start

```bash
# Check Docker daemon
docker ps

# Rebuild everything
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Frontend shows blank page

```bash
# Clear Next.js cache
rm -rf frontend/.next

# Restart
docker-compose restart frontend
```

## Making Code Changes

### Backend Code

The backend container mounts the `backend/` directory, so changes reload automatically:

1. Edit a file in `backend/`
2. Changes apply immediately (uvicorn auto-reload enabled)

### Frontend Code

The frontend container mounts the `frontend/` directory, so changes reload automatically:

1. Edit a file in `frontend/`
2. Changes apply immediately (Next.js hot reload enabled)

## Running Without Docker

See [Local Setup Guide](../docs/setup/LOCAL_SETUP.md) for detailed instructions.

## Next: Understand the Code

- **Frontend**: Start at [frontend/src/pages/index.js](../frontend/src/pages/index.js)
- **Backend**: Start at [backend/app/main.py](../backend/app/main.py)
- **Database**: Check [backend/app/database/models.py](../backend/app/database/models.py)
- **AI**: Explore [backend/app/ai/__init__.py](../backend/app/ai/__init__.py)

## What Happens on Startup

```
docker-compose up -d
    ↓
PostgreSQL starts
    ↓ (waits for health check)
Backend starts (applies migrations, initializes DB)
    ↓ (waits for backend health check)
Redis starts
    ↓ (waits for health check)
Frontend starts
    ↓
Application ready!
```

## API Quick Test

```bash
# Get health status
curl http://localhost:8000/health

# Register user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "full_name": "Test User"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }'

# Copy the access_token from response
# Then test authenticated endpoint

curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Database Access

Access the database admin at http://localhost:5050:

- Email: `admin@admin.com`
- Password: `admin`

Then add a new server:
- Host: `postgres`
- Port: `5432`
- Database: `resume_builder`
- Username: `resume_user`
- Password: `password123`

## Environment Variables

The setup script creates a `.env` file with defaults. These are suitable for development.

For production, see `.env.example` for all variables and update accordingly.

## File Structure Reference

```
resume-builder/
├── backend/          # FastAPI application
│   ├── app/
│   │   ├── api/      # API endpoints
│   │   ├── services/ # Business logic
│   │   ├── ai/       # AI pipeline
│   │   └── database/ # Database models
│   └── requirements.txt
├── frontend/         # Next.js application
│   ├── src/pages/    # Page components
│   ├── src/lib/      # Utilities
│   └── package.json
├── docs/            # Documentation
├── infra/           # Infrastructure configs
└── docker-compose.yml
```

## Popular Endpoints

After creating an account and token:

```bash
TOKEN="your_jwt_token"

# Add education
curl -X POST http://localhost:8000/api/v1/career/education \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "institution": "Stanford University",
    "degree": "BS",
    "field_of_study": "Computer Science",
    "start_date": "2020-09-01",
    "end_date": "2024-05-15"
  }'

# List education
curl http://localhost:8000/api/v1/career/education \
  -H "Authorization: Bearer $TOKEN"

# Add experience
curl -X POST http://localhost:8000/api/v1/career/experience \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Google",
    "position": "Software Engineer",
    "employment_type": "full_time",
    "start_date": "2024-01-01",
    "technologies": ["Python", "Go", "Kubernetes"]
  }'
```

## Need Help?

- 📖 Read [README.md](../README.md)
- 🏗️ Check [ARCHITECTURE_DESIGN.md](../ARCHITECTURE_DESIGN.md)
- 📚 See [docs/](../docs/)
- 🐛 Open a GitHub issue
- 💬 Start a discussion

---

**Happy developing! 🚀**
