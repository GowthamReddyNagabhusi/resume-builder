# API Documentation

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://api.resumebuilder.com`

All API responses are JSON. Errors include a status code and message.

## Authentication

### JWT Authentication

Most endpoints require authentication via JWT bearer token.

**Header**: `Authorization: Bearer YOUR_JWT_TOKEN`

### Getting a Token

```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Refreshing a Token

```bash
POST /api/v1/auth/refresh
Authorization: Bearer YOUR_TOKEN

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message",
  "status_code": 400,
  "error_code": "VALIDATION_ERROR"
}
```

### Common Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 429 | Too Many Requests (Rate Limited) |
| 500 | Internal Server Error |

## API Endpoints

### Authentication

#### Register User

```
POST /api/v1/auth/register
```

**Request**:
```json
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe"
}
```

**Response** (201 Created):
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

#### Login

```
POST /api/v1/auth/login
```

**Request**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

#### Get Current User

```
GET /api/v1/auth/me
Authorization: Bearer {token}
```

**Response** (200 OK):
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### Career Data

Base path: `/api/v1/career/`

#### Add Education

```
POST /api/v1/career/education
Authorization: Bearer {token}
Content-Type: application/json
```

**Request**:
```json
{
  "institution": "Stanford University",
  "degree": "BS",
  "field_of_study": "Computer Science",
  "start_date": "2018-09-01",
  "end_date": "2022-05-15",
  "gpa": 3.8,
  "description": "GPA in major: 3.9"
}
```

**Response** (201 Created):
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "institution": "Stanford University",
  "degree": "BS",
  "field_of_study": "Computer Science",
  "start_date": "2018-09-01",
  "end_date": "2022-05-15",
  "gpa": 3.8,
  "description": "GPA in major: 3.9",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

#### List Education

```
GET /api/v1/career/education
Authorization: Bearer {token}
```

**Response** (200 OK):
```json
{
  "items": [
    {
      "id": "uuid",
      "institution": "Stanford University",
      ...
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10
}
```

---

#### Add Experience

```
POST /api/v1/career/experience
Authorization: Bearer {token}
Content-Type: application/json
```

**Request**:
```json
{
  "company": "Google",
  "position": "Software Engineer",
  "employment_type": "full_time",
  "start_date": "2022-06-01",
  "end_date": null,
  "description": "Built scalable services",
  "location": "San Francisco, CA",
  "achievements": [
    "Reduced latency by 40%",
    "Led team of 3 engineers"
  ],
  "technologies": ["Python", "Go", "Kubernetes"]
}
```

**Response** (201 Created):
```json
{
  "id": "uuid",
  "company": "Google",
  "position": "Software Engineer",
  ...
}
```

---

#### List Experience

```
GET /api/v1/career/experience
Authorization: Bearer {token}
```

**Response** (200 OK):
```json
{
  "items": [...],
  "total": 1
}
```

---

#### Add Skill

```
POST /api/v1/career/skills
Authorization: Bearer {token}
Content-Type: application/json
```

**Request**:
```json
{
  "name": "Python",
  "category": "programming_language",
  "proficiency": "expert",
  "years_of_experience": 5,
  "endorsements": 25
}
```

**Response** (201 Created):
```json
{
  "id": "uuid",
  "name": "Python",
  "category": "programming_language",
  "proficiency": "expert",
  "years_of_experience": 5,
  "endorsements": 25
}
```

---

#### Add Project

```
POST /api/v1/career/projects
Authorization: Bearer {token}
Content-Type: application/json
```

**Request**:
```json
{
  "name": "Resume Builder",
  "description": "AI-powered resume compiler",
  "url": "https://github.com/user/resume-builder",
  "start_date": "2023-01-01",
  "end_date": "2024-01-15",
  "technologies": ["FastAPI", "React", "PostgreSQL"],
  "highlights": [
    "10k GitHub stars",
    "Used by 5k developers"
  ]
}
```

**Response** (201 Created):
```json
{
  "id": "uuid",
  "name": "Resume Builder",
  ...
}
```

---

### Resume Management

#### Generate Resume

```
POST /api/v1/resumes/generate
Authorization: Bearer {token}
Content-Type: application/json
```

**Request**:
```json
{
  "job_description": "Looking for a Python developer with FastAPI experience...",
  "template_id": "modern",
  "title": "Software Engineer - Company XYZ"
}
```

**Response** (201 Created):
```json
{
  "id": "uuid",
  "title": "Software Engineer - Company XYZ",
  "template_id": "modern",
  "content": {
    "summary": "Generated summary tailored to job...",
    "experience": [...],
    "education": [...],
    "skills": [...]
  },
  "generated_at": "2024-01-15T10:30:00Z",
  "job_description": "..."
}
```

---

#### List Generated Resumes

```
GET /api/v1/resumes
Authorization: Bearer {token}
```

**Query Parameters**:
- `skip`: Number of items to skip (default: 0)
- `limit`: Number of items to return (default: 10)
- `template_id`: Filter by template

**Response** (200 OK):
```json
{
  "items": [
    {
      "id": "uuid",
      "title": "Software Engineer - Company XYZ",
      "template_id": "modern",
      "generated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 1
}
```

---

#### Get Resume

```
GET /api/v1/resumes/{resume_id}
Authorization: Bearer {token}
```

**Response** (200 OK):
```json
{
  "id": "uuid",
  "title": "Software Engineer - Company XYZ",
  "template_id": "modern",
  "content": {...},
  "generated_at": "2024-01-15T10:30:00Z"
}
```

---

#### Download Resume

```
GET /api/v1/resumes/{resume_id}/download
Authorization: Bearer {token}
```

**Query Parameters**:
- `format`: `pdf` or `docx` (default: `pdf`)

**Response**: Binary file (PDF or DOCX)

---

#### Delete Resume

```
DELETE /api/v1/resumes/{resume_id}
Authorization: Bearer {token}
```

**Response** (204 No Content)

---

### Resume Templates

#### List Templates

```
GET /api/v1/templates
```

**Response** (200 OK):
```json
{
  "items": [
    {
      "id": "modern",
      "name": "Modern",
      "description": "Clean, modern design",
      "thumbnail_url": "https://...",
      "created_by": "system"
    },
    {
      "id": "classic",
      "name": "Classic",
      "description": "Traditional design",
      "thumbnail_url": "https://...",
      "created_by": "system"
    }
  ],
  "total": 2
}
```

---

#### Get Template

```
GET /api/v1/templates/{template_id}
```

**Response** (200 OK):
```json
{
  "id": "modern",
  "name": "Modern",
  "description": "Clean, modern design",
  "template_schema": {...},
  "sample_content": {...}
}
```

---

### External Platform Integration

#### List Connected Platforms

```
GET /api/v1/integrations
Authorization: Bearer {token}
```

**Response** (200 OK):
```json
{
  "items": [
    {
      "platform": "github",
      "connected": true,
      "username": "john-doe",
      "connected_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

#### Connect Platform

```
POST /api/v1/integrations/connect
Authorization: Bearer {token}
Content-Type: application/json
```

**Request**:
```json
{
  "platform": "github",
  "code": "github_oauth_code"
}
```

**Response** (200 OK):
```json
{
  "platform": "github",
  "connected": true,
  "username": "john-doe"
}
```

---

#### Disconnect Platform

```
DELETE /api/v1/integrations/{platform}
Authorization: Bearer {token}
```

**Response** (204 No Content)

---

#### Sync Platform Data

```
POST /api/v1/integrations/{platform}/sync
Authorization: Bearer {token}
```

**Response** (200 OK):
```json
{
  "status": "syncing",
  "message": "Started syncing GitHub repositories...",
  "items_found": 15
}
```

---

#### Get Integration Status

```
GET /api/v1/integrations/{platform}/status
Authorization: Bearer {token}
```

**Response** (200 OK):
```json
{
  "platform": "github",
  "connected": true,
  "last_sync": "2024-01-15T10:30:00Z",
  "items_count": 15,
  "status": "synced"
}
```

---

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Default**: 100 requests per minute per user
- **AI Endpoints**: 10 requests per minute per user
- **Status Headers**:
  - `X-RateLimit-Limit`: Maximum requests
  - `X-RateLimit-Remaining`: Requests left
  - `X-RateLimit-Reset`: Unix timestamp when limit resets

When rate limited, you'll receive a 429 response:

```json
{
  "detail": "Rate limit exceeded. Try again in 30 seconds.",
  "status_code": 429,
  "error_code": "RATE_LIMIT_EXCEEDED"
}
```

---

## Pagination

Endpoints that return lists support pagination:

**Query Parameters**:
- `skip`: Number of items to skip (default: 0)
- `limit`: Number of items to return (default: 10, max: 100)

**Response Format**:
```json
{
  "items": [...],
  "total": 50,
  "page": 1,
  "page_size": 10,
  "has_next": true,
  "has_previous": false
}
```

---

## Webhooks

Resume generation and integration sync events can be sent to a webhook URL.

**Set Webhook URL**:
```
POST /api/v1/settings/webhook
Authorization: Bearer {token}
Content-Type: application/json

{
  "url": "https://your-domain.com/webhook"
}
```

**Webhook Events**:

### Resume Generated
```json
{
  "event": "resume.generated",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "resume_id": "uuid",
    "title": "Software Engineer - Company XYZ",
    "template_id": "modern",
    "generated_at": "2024-01-15T10:30:00Z"
  }
}
```

### Integration Synced
```json
{
  "event": "integration.synced",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "platform": "github",
    "items_count": 15,
    "synced_at": "2024-01-15T10:30:00Z"
  }
}
```

---

## CORS

The API supports CORS. The frontend can make requests directly to the API.

**Allowed Origins**:
- `http://localhost:3000` (development)
- `https://resumebuilder.com` (production)

**Allowed Methods**: GET, POST, PUT, DELETE, OPTIONS

**Allowed Headers**: Authorization, Content-Type

---

## Interactive API Documentation

More details available at:

- **Swagger UI**: `GET http://localhost:8000/docs`
- **ReDoc**: `GET http://localhost:8000/redoc`
- **OpenAPI Schema**: `GET http://localhost:8000/openapi.json`

---

## Code Examples

### Python

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "your_jwt_token"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Get current user
response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
print(response.json())

# Generate resume
resume_data = {
    "job_description": "We need a Python developer...",
    "template_id": "modern",
    "title": "Software Engineer - Company XYZ"
}

response = requests.post(
    f"{BASE_URL}/resumes/generate",
    json=resume_data,
    headers=headers
)
print(response.json())
```

### JavaScript/Node.js

```javascript
const API_BASE = "http://localhost:8000/api/v1";
const TOKEN = "your_jwt_token";

const headers = {
  "Authorization": `Bearer ${TOKEN}`,
  "Content-Type": "application/json"
};

// Get current user
const userResponse = await fetch(`${API_BASE}/auth/me`, { headers });
const user = await userResponse.json();
console.log(user);

// Generate resume
const resumeData = {
  job_description: "We need a Python developer...",
  template_id: "modern",
  title: "Software Engineer - Company XYZ"
};

const resumeResponse = await fetch(`${API_BASE}/resumes/generate`, {
  method: "POST",
  headers,
  body: JSON.stringify(resumeData)
});

const resume = await resumeResponse.json();
console.log(resume);
```

### cURL

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'

# Get current user
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/auth/me

# Generate resume
curl -X POST http://localhost:8000/api/v1/resumes/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "We need a Python developer...",
    "template_id": "modern",
    "title": "Software Engineer - Company XYZ"
  }'
```

---

## Changelog

### v1.0.0 (2024-01-15)
- Initial API release
- Authentication endpoints
- Career data management
- Resume generation
- Platform integrations
- Rate limiting

---

**For questions or issues, open a GitHub issue or contact support.**
