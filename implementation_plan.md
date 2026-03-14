# CareerForge — Data Isolation, Education & New Features

Fixes critical user data mixing, improves modals/forms, extends education fields, and adds Achievements + Platform Links features.

## User Review Required

> [!CAUTION]
> **Data isolation bug**: The [resumes](file:///c:/resume-builder/backend/database/models.py#468-475) and [manual_skills](file:///c:/resume-builder/backend/database/models.py#494-498) tables have no [user_id](file:///c:/resume-builder/backend/database/models.py#799-803) column. All users see everyone's data. This is the highest priority fix — requires schema migration.

> [!IMPORTANT]
> **Existing data**: The migration will add [user_id](file:///c:/resume-builder/backend/database/models.py#799-803) to existing tables and default old rows to `user_id=1`. If there are no important rows to preserve, this is fine. Otherwise let me know.

## Proposed Changes

### 1. Data Isolation — Database Layer

#### [MODIFY] [models.py](file:///c:/resume-builder/backend/database/models.py)
- **[resumes](file:///c:/resume-builder/backend/database/models.py#468-475) table**: Add `user_id INTEGER` column + migration for existing DB
- **[manual_skills](file:///c:/resume-builder/backend/database/models.py#494-498) table**: Add `user_id INTEGER` column + migration
- **[log_resume()](file:///c:/resume-builder/backend/database/models.py#456-466)**: Accept [user_id](file:///c:/resume-builder/backend/database/models.py#799-803) parameter, insert it
- **[get_resumes()](file:///c:/resume-builder/backend/database/models.py#468-475) / [count_resumes()](file:///c:/resume-builder/backend/database/models.py#477-481)**: Accept [user_id](file:///c:/resume-builder/backend/database/models.py#799-803), add `WHERE user_id=?`
- **[add_skill()](file:///c:/resume-builder/backend/database/models.py#485-492) / [get_manual_skills()](file:///c:/resume-builder/backend/database/models.py#494-498)**: Accept [user_id](file:///c:/resume-builder/backend/database/models.py#799-803), filter by it
- **New tables**: `achievements`, `platform_links`
- **Schema migrations**: `ALTER TABLE` for backward compatibility with existing DBs

---

### 2. Data Isolation — API Layer

#### [MODIFY] [resume.py](file:///c:/resume-builder/backend/api/resume.py)
- [list_resumes](file:///c:/resume-builder/backend/api/resume.py#45-64): Pass `user["id"]` to `db.get_resumes()` and `db.count_resumes()`
- [generate_resume](file:///c:/resume-builder/backend/api/resume.py#27-43): Add `Depends(get_current_user)`, pass user_id to [build_docx](file:///c:/resume-builder/backend/services/resume_builder.py#210-387) and [log_resume](file:///c:/resume-builder/backend/database/models.py#456-466)
- [download_resume](file:///c:/resume-builder/backend/api/resume.py#66-86): Add auth, verify resume belongs to user

#### [MODIFY] [resume_builder.py](file:///c:/resume-builder/backend/services/resume_builder.py)
- [build_docx](file:///c:/resume-builder/backend/services/resume_builder.py#210-387): Accept [user_id](file:///c:/resume-builder/backend/database/models.py#799-803), pass to [log_resume](file:///c:/resume-builder/backend/database/models.py#456-466)

#### [MODIFY] [career.py](file:///c:/resume-builder/backend/api/career.py)
- Skills endpoints: Pass [user_id](file:///c:/resume-builder/backend/database/models.py#799-803) to all skill DB calls
- Add achievements CRUD endpoints
- Add platform_links CRUD endpoints

---

### 3. Modal UI Fix

#### [MODIFY] [career/index.js](file:///c:/resume-builder/frontend/src/pages/career/index.js)
- [FormModal](file:///c:/resume-builder/frontend/src/pages/career/index.js#20-64): Add stronger `bg-surface-900/95` backdrop, thicker border (`border-white/[0.15]`), `shadow-glass-lg`, padding increase
- All category modals inherit the improved base

---

### 4. Education Enhancements

#### [MODIFY] [career/index.js](file:///c:/resume-builder/frontend/src/pages/career/index.js) (EducationTab)
- Add month dropdowns (Jan–Dec), "Currently studying" toggle, grade type selector (CGPA/GPA/Percentage/Marks)

#### [MODIFY] [career.py](file:///c:/resume-builder/backend/api/career.py) (education endpoints)
- Accept `start_month`, `end_month`, `is_current`, `grade_type` fields

#### [MODIFY] [models.py](file:///c:/resume-builder/backend/database/models.py) (education table)
- Add columns: `start_month`, `end_month`, `is_current`, `grade_type`

---

### 5. Achievements Section

#### [MODIFY] [models.py](file:///c:/resume-builder/backend/database/models.py)
- New `achievements` table: `id, user_id, title, description, organization, date, link, created_at`

#### [MODIFY] [career.py](file:///c:/resume-builder/backend/api/career.py)
- GET/POST/DELETE `/api/career/achievements`

#### [MODIFY] [career/index.js](file:///c:/resume-builder/frontend/src/pages/career/index.js)
- New "Achievements" tab with form fields: Title, Description, Organization/Event, Date, Link

#### [MODIFY] [client.js](file:///c:/resume-builder/frontend/src/lib/api/client.js)
- Add `getAchievements`, `createAchievement`, `deleteAchievement` methods

---

### 6. Platform Links

#### [MODIFY] [models.py](file:///c:/resume-builder/backend/database/models.py)
- New `platform_links` table: `id, user_id, platform, username, profile_url, created_at`

#### [MODIFY] [career.py](file:///c:/resume-builder/backend/api/career.py)
- GET/POST/DELETE `/api/career/platforms`

#### [MODIFY] [career/index.js](file:///c:/resume-builder/frontend/src/pages/career/index.js)
- New "Profiles" tab with platform selector + username input

#### [MODIFY] [dashboard.js](file:///c:/resume-builder/frontend/src/pages/dashboard.js)
- Show connected platform icons with clickable links

#### [MODIFY] [client.js](file:///c:/resume-builder/frontend/src/lib/api/client.js)
- Add `getPlatforms`, `createPlatform`, `deletePlatform` methods

---

## Verification Plan

### Automated Tests
```bash
cd c:\resume-builder
& "C:\Users\hp\AppData\Local\Programs\Python\Python313\python.exe" -m pytest tests/ -v
```

### Browser Tests
1. Create User A → add education, skills → generate a resume
2. Create User B → verify dashboard shows 0 resumes, 0 skills
3. Verify modals render with proper separation
4. Verify education form has month pickrs, grade type, "Currently studying"
5. Verify Achievements tab has CRUD
6. Verify Platform Links tab has CRUD and shows icons on dashboard
