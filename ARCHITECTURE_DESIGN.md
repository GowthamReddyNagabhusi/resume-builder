# Resume Builder - Architecture Design Document

## System Overview

The Resume Builder is an **AI-powered Career Data Platform** that compiles role-specific resumes automatically. Instead of users writing resumes manually, the system collects structured career information once and automatically generates optimized resumes for target positions using AI.

The system behaves like a **Career → Resume Compiler**.

---

## Core Principles

1. **Separation of Concerns**: Each layer has distinct responsibilities
2. **API-First Design**: Strong focus on extensible and RESTful interfaces
3. **AI as a Service**: Modular AI pipeline with swappable providers
4. **User-Centric Data Model**: Career data is the single source of truth
5. **Cloud-Ready**: Designed for containerization and horizontal scaling
6. **Production-Grade**: Enterprise-quality code, logging, error handling, security

---

## Layered Architecture

### 1. Frontend Layer (Next.js/React)
**Responsibility**: User interface for career data management and resume generation

- **Authentication Pages**: Sign up, login, OAuth flows
- **Career Data Management**: Forms for education, experience, skills, projects, certifications
- **External Integrations UI**: Connect GitHub, coding platforms, credentials
- **Resume Generation**: Job description input, template selection, customization
- **Document Management**: Preview, download, history of generated resumes

### 2. Backend API Layer (FastAPI/Python)
**Responsibility**: Business logic, data validation, orchestration

Core services:
- **User & Auth Service**: JWT-based authentication, OAuth integrations
- **Career Data Service**: CRUD operations for user's career information
- **Resume Service**: Orchestrate resume generation process
- **Integration Service**: Connect to external APIs (GitHub, LeetCode, etc.)
- **AI Orchestrator**: Coordinate AI pipeline tasks
- **Template Service**: Manage and render resume templates

### 3. AI Pipeline Layer (Modular)
**Responsibility**: Content reasoning and AI-powered transformations

Specialized AI tasks:
- **Job Analysis**: Parse and understand job descriptions
- **Relevance Ranking**: Rate which projects/skills match a role
- **Content Generation**: Create professional bullet points
- **ATS Optimization**: Ensure keyword compatibility
- **Bullet Enhancement**: Improve clarity and impact

Provider abstraction:
- Support multiple AI providers (OpenAI, Anthropic, local models)
- Easy provider swapping without code changes
- Cost optimization through provider selection

### 4. Data Layer
**Responsibility**: Persistent storage and data integrity

Tables:
- Users (authentication, profile)
- Career Data (education, experience, skills, projects, certifications, achievements)
- Resume Templates (system and user-uploaded)
- Generated Resumes (history and metadata)
- Integration Credentials (OAuth tokens, API keys - encrypted)
- Resume Customizations (user edits to generated content)

### 5. External Integrations
**Responsibility**: API connections to external platforms

- GitHub API (repositories, contributions, profile)
- Coding platforms (LeetCode, Codeforces, CodeSignal)
- Credential platforms (when APIs available)
- OAuth providers (for multi-platform authentication)

### 6. Infrastructure Layer
**Responsibility**: Deployment, containerization, infrastructure

- **Containerization**: Docker images for backend, frontend, database
- **Orchestration**: Docker Compose for local dev, Kubernetes for production
- **CI/CD**: GitHub Actions for testing, linting, deployment
- **Infrastructure as Code**: Terraform for cloud resource provisioning

---

## Data Model

### User
- user_id (PK)
- email
- password_hash
- name
- profile_picture_url
- created_at
- updated_at
- is_active

### Career Data Collections
**Education**
- education_id (PK)
- user_id (FK)
- institution
- degree
- field_of_study
- start_date
- end_date
- gpa (optional)
- awards (optional)

**Experience**
- experience_id (PK)
- user_id (FK)
- company
- position
- employment_type (full-time, part-time, internship, contract)
- start_date
- end_date
- description
- achievements (array of strings)
- technologies_used (array)

**Skills**
- skill_id (PK)
- user_id (FK)
- skill_name
- proficiency_level (beginner, intermediate, advanced, expert)
- years_of_experience
- endorsement_count (if from LinkedIn, etc.)
- category (programming, language, soft-skill, tool)

**Projects**
- project_id (PK)
- user_id (FK)
- project_name
- description
- technologies (array)
- github_url (optional)
- live_url (optional)
- start_date
- end_date
- achievements (array)
- team_size
- role_description

**Certifications**
- cert_id (PK)
- user_id (FK)
- cert_name
- issuing_organization
- issue_date
- expiration_date (optional)
- credential_url
- credential_id (for verification)

**Achievements**
- achievement_id (PK)
- user_id (FK)
- title
- description
- date
- category (award, publication, speaking, recognition)
- link (optional)

**Integration Credentials**
- credential_id (PK)
- user_id (FK)
- platform (github, leetcode, codeforces, custom)
- access_token (encrypted)
- refresh_token (encrypted, optional)
- expires_at
- linked_at
- last_synced_at

### Resume Generated
- resume_id (PK)
- user_id (FK)
- target_job_description (text)
- template_id (FK)
- content (JSON - structured resume content)
- metadata (generation parameters, AI models used, tokens consumed)
- created_at
- downloaded_count
- version

### Resume Templates
- template_id (PK)
- template_name
- template_type (json-schema, pdf, docx)
- thumbnail_url
- is_system_template
- created_by_user_id (FK, nullable)
- preview_html
- created_at

---

## API Structure

### Authentication Endpoints
```
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
POST   /api/v1/auth/refresh
POST   /api/v1/auth/oauth/{provider}/callback
```

### Career Data Endpoints
```
GET    /api/v1/career/summary
GET    /api/v1/career/education
POST   /api/v1/career/education
PUT    /api/v1/career/education/{id}
DELETE /api/v1/career/education/{id}

GET    /api/v1/career/experience
POST   /api/v1/career/experience
PUT    /api/v1/career/experience/{id}
DELETE /api/v1/career/experience/{id}

GET    /api/v1/career/skills
POST   /api/v1/career/skills
PUT    /api/v1/career/skills/{id}
DELETE /api/v1/career/skills/{id}

GET    /api/v1/career/projects
POST   /api/v1/career/projects
PUT    /api/v1/career/projects/{id}
DELETE /api/v1/career/projects/{id}

GET    /api/v1/career/certifications
POST   /api/v1/career/certifications
PUT    /api/v1/career/certifications/{id}
DELETE /api/v1/career/certifications/{id}

GET    /api/v1/career/achievements
POST   /api/v1/career/achievements
PUT    /api/v1/career/achievements/{id}
DELETE /api/v1/career/achievements/{id}
```

### Integration Endpoints
```
GET    /api/v1/integrations/status
POST   /api/v1/integrations/{platform}/connect
POST   /api/v1/integrations/{platform}/disconnect
POST   /api/v1/integrations/{platform}/sync
GET    /api/v1/integrations/{platform}/status
```

### Resume Generation Endpoints
```
POST   /api/v1/resumes/generate
GET    /api/v1/resumes
GET    /api/v1/resumes/{resume_id}
DELETE /api/v1/resumes/{resume_id}
POST   /api/v1/resumes/{resume_id}/download
POST   /api/v1/resumes/{resume_id}/customize

GET    /api/v1/templates
GET    /api/v1/templates/{template_id}
POST   /api/v1/templates/upload
```

### Admin/Analytics Endpoints (Optional)
```
GET    /api/v1/admin/stats
GET    /api/v1/admin/users
POST   /api/v1/admin/users/{user_id}/disable
```

---

## Resume Generation Pipeline

### Flow
```
1. User Input
   - Provide job description
   - Select template
   - Set preferences (length, format, emphasis)
        ↓
2. Data Retrieval
   - Load user's career data
   - Load selected template
        ↓
3. Job Analysis (AI)
   - Parse job description
   - Extract key requirements: skills, experience, keywords
   - Identify role level and industry
        ↓
4. Data Relevance Ranking (AI)
   - Score each project against job requirements
   - Score each experience entry
   - Score each skill
   - Identify top-N most relevant items
        ↓
5. Content Generation (AI)
   - Generate professional bullet points for selected projects
   - Re-articulate achievements in context of job
   - Create compelling summary statement
   - Generate cover letter snippet (optional)
        ↓
6. ATS Optimization (AI)
   - Optimize keywords for Applicant Tracking Systems
   - Ensure format compatibility
   - Check for common ATS-breaking elements
        ↓
7. Structured Content Assembly
   - Create JSON representation of resume content
   - Map content to template structure
        ↓
8. Template Rendering
   - Inject structured content into template
   - Generate final document (PDF/DOCX/HTML)
        ↓
9. Storage & Export
   - Save resume record to database
   - Generate download link
   - Provide preview
```

---

## AI System Design

### Task-Specialized Pipeline

Different AI models may specialize in different tasks:

**Job Analyzer**
- Input: Job description text
- Output: Structured JSON of requirements
- Purpose: Extract and categorize job requirements
- Recommended: Claude (for detailed analysis) or GPT-4

**Relevance Ranker**
- Input: Career data items + job requirements
- Output: Relevance scores for each item
- Purpose: Identify most important career items for the role
- Recommended: Specialized model or Claude

**Content Generator**
- Input: Career data item + target job context
- Output: Professional bullet point or achievement statement
- Purpose: Create compelling, concise resume content
- Recommended: GPT-3.5 or Claude

**ATS Optimizer**
- Input: Resume content + template format
- Output: Optimized content and format suggestions
- Purpose: Ensure ATS compatibility
- Recommended: Specialized model or fine-tuned GPT

**Bullet Enhancer**
- Input: Achievement description
- Output: Polished, impactful bullet point
- Purpose: Improve clarity and professional tone
- Recommended: GPT-3.5

### Provider Pattern

Each AI task is abstracted through a provider interface:

```
AITask (Abstract Base)
├── OpenAIProvider
├── AnthropicProvider
├── LocalLLMProvider
└── MockProvider (for testing)
```

This allows:
- Swapping providers without code changes
- A/B testing different models
- Cost optimization
- Fallback strategies
- Testing with mock implementations

---

## Deployment Architecture

### Local Development
- **Docker Compose**: All services in containers
- **Hot reload**: Code changes reflect immediately
- **Seed data**: Sample career data for testing
- **Mock AI**: Local AI or mock responses for testing

### Production (AWS/Azure)
- **Frontend**: CDN + Static hosting (S3 + CloudFront, or Azure Static Web Apps)
- **Backend**: ECS/EKS (containerized FastAPI)
- **Database**: RDS PostgreSQL or Azure Database
- **Cache**: Redis for session management
- **Storage**: S3 or Azure Blob for resume files
- **AI API Keys**: AWS Secrets Manager or Azure Key Vault
- **Monitoring**: CloudWatch or Azure Monitor
- **CI/CD**: GitHub Actions → AWS CodePipeline

### Scalability Considerations
- **Stateless backend**: Scales horizontally
- **Database connection pooling**: Handle load
- **AI rate limiting**: Manage API quotas and costs
- **Caching layer**: Reduce database hits
- **Async job queue**: For long-running resume generation
- **CDN**: Serve frontend and static assets

---

## Technology Stack

### Backend
- **Framework**: FastAPI (async, async-first design, auto OpenAPI docs)
- **Database**: PostgreSQL (robust, ACID, JSON support)
- **ORM**: SQLAlchemy (powerful, flexible)
- **Migrations**: Alembic
- **Authentication**: JWT + OAuth2
- **Validation**: Pydantic
- **Caching**: Redis
- **Job Queue**: Celery (optional, for async tasks)
- **AI Integration**: OpenAI Python SDK, Anthropic SDK
- **Document Generation**: python-docx, reportlab (PDF)
- **Logging**: Python logging + structured logs
- **Testing**: pytest, pytest-asyncio

### Frontend
- **Framework**: Next.js with React
- **Styling**: Tailwind CSS or Material-UI
- **State Management**: React Context API or Zustand
- **API Client**: Axios or Fetch API
- **Form Handling**: React Hook Form
- **Document Export**: React-PDF, docx-gen
- **Authentication**: next-auth.js

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Docker Compose (local), Kubernetes (production)
- **CI/CD**: GitHub Actions
- **Infrastructure as Code**: Terraform (optional)
- **Monitoring**: Prometheus + Grafana (optional)

---

## Security Considerations

1. **Authentication**: JWT tokens with refresh tokens
2. **API Keys**: Encrypted storage in environment variables/secrets manager
3. **OAuth Tokens**: Encrypted at rest, rotated periodically
4. **User Privacy**: GDPR compliance, data export capabilities
5. **CORS**: Strict origin validation
6. **Rate Limiting**: Per-user and per-IP limits
7. **Input Validation**: Comprehensive server-side validation
8. **SQL Injection**: Parameterized queries via ORM
9. **XSS Protection**: React escaping + CSP headers
10. **HTTPS Only**: All external communication encrypted

---

## Observability & Monitoring

1. **Structured Logging**: All service logs in JSON format
2. **Request Tracing**: Correlation IDs across distributed systems
3. **Performance Metrics**: Response times, throughput, error rates
4. **AI Cost Tracking**: Monitor API usage and costs
5. **User Analytics**: Track feature usage (privacy-compliant)
6. **Error Tracking**: Sentry or similar for error aggregation
7. **Health Checks**: Liveness and readiness probes
8. **Alerts**: Automated alerts for critical issues

---

## Development Workflow

1. **Local Development**: Run all services via Docker Compose
2. **Code Style**: Black (Python), Prettier (JavaScript)
3. **Linting**: Pylint, ESLint
4. **Testing**: Unit, integration, and E2E tests
5. **Pre-commit Hooks**: Auto-formatting and linting
6. **Code Review**: GitHub PRs with tests and linting checks
7. **Staging Deployment**: Automatic on merge to `staging` branch
8. **Production Deployment**: Manual/automated on tag or release

---

## File Organization Philosophy

- **By Feature**: Routes, models, and logic grouped by domain (auth, career, resume)
- **Layered**: Models → Services → API handlers
- **Testable**: Easy to test each layer independently
- **Scalable**: Easy to add new features without impacting others
- **Maintainable**: Clear folder structure and naming conventions

---

## Future Extensions

1. **Job Board Integration**: Auto-generate resumes for job postings
2. **CoverLetter Generation**: Extend pipeline to generate cover letters
3. **Interview Coaching**: AI-powered interview prep
4. **Salary Negotiation**: AI-powered salary guidance
5. **Career Path Analysis**: ML models to recommend career moves
6. **Resume Analytics**: Track resume views, downloads, interview callbacks
7. **Team Features**: Shared career resources, collaborative resume review
8. **Mobile App**: React Native or Flutter mobile version

---

## Success Metrics

1. **User Adoption**: Active users, resume generations per user
2. **Resume Quality**: Interview callback rates (if trackable)
3. **AI Accuracy**: User satisfaction with generated content
4. **System Performance**: API response times, resume generation time
5. **Cost**: API costs per resume generation
6. **Reliability**: System uptime, error rates
7. **Scalability**: User growth handling without degradation

---

This architecture ensures the Resume Builder is enterprise-grade, maintainable, scalable, and positioned for future growth and extension.
