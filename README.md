# Doggzi Office OS Backend (Django + DRF + MongoDB)

Production-ready HRMS/Office OS backend for Doggzi Pvt Ltd using Django, DRF, and MongoDB Atlas.

## Features
- Approval-based onboarding with maker-only approvals
- Role-based access: SUPERUSER, HR, MD, EMPLOYEE, FINANCE
- HR employee onboarding with finance/MD/maker approvals
- Appraisal and promotion workflows
- Employee self-service module
- Finance module with revenue/expense/payroll/budget entries
- Excel export/import for list endpoints
- Swagger and Redoc documentation
- MongoDB Atlas (pymongo) with startup checks and indexes
- Built-in web UI for login and signup requests at `/`

## Recruitment & Interview Management (WhatsApp-first)
### Architecture (brief)
- **Django app:** `recruitment` with SQLite persistence.
- **UI:** Simple server-rendered templates + mobile-friendly CSS.
- **Roles:** Recruiter (intake + pipeline), Interviewer (today panel), HR (docs), Admin (dashboard).
- **Automation:** Simulated WhatsApp logs stored in `WhatsAppMessage`.

### Folder Structure
```
recruitment/
  models.py
  views.py
  urls.py
  utils.py
  templates/recruitment/
  static/recruitment/
  management/commands/seed_recruitment.py
```

### Key URLs
- `GET /recruitment/` → Home
- `GET/POST /recruitment/intake` → Candidate intake form
- `GET /recruitment/pipeline` → Pipeline view + status update
- `GET/POST /recruitment/login/interviewer` → Interviewer PIN login
- `GET /recruitment/interviewer/today` → Today’s interviews
- `GET/POST /recruitment/login/hr` → HR PIN login
- `GET /recruitment/hr/panel` → Selected candidates + documents
- `GET/POST /recruitment/login/admin` → Admin PIN login
- `GET /recruitment/admin/dashboard` → Daily metrics

### Status Pipeline (fixed)
```
NEW
→ INTERVIEW_SCHEDULED
→ CONFIRMED
→ INTERVIEW_DONE
→ SELECTED / REJECTED / HOLD
→ DOCUMENT_PENDING
→ DOCUMENT_COMPLETED
→ JOINED / DROPPED
```

### WhatsApp Message Templates (Simulated)
- **Interview confirmation:** “Namaste {name}! {role} interview fix ho gaya hai...”
- **12-hour reminder:** “Reminder: {name}, kal {date} {time} interview hai...”
- **Document request:** “Shabash {name}! Aap select ho gaye...”

### Sample Test Data
Seed sample candidates:
```bash
python manage.py seed_recruitment
```

### PINs (Simple Login)
Defaults (override in `.env`):
```
RECRUITMENT_INTERVIEWER_PIN=1234
RECRUITMENT_HR_PIN=5678
RECRUITMENT_ADMIN_PIN=9999
```

## Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.sample .env
python manage.py runserver
```

## Environment Variables
Create a `.env` file in the project root:
```env
DJANGO_SECRET_KEY=replace-me
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=*
CORS_ALLOW_ALL_ORIGINS=true

MONGO_URI=mongodb+srv://doggzipvtlmt_db_user:<db_password>@cluster0.wpzevmb.mongodb.net/?appName=Cluster0
MONGO_DB_NAME=doggzi_office_os

JWT_ACCESS_MINUTES=60
JWT_REFRESH_DAYS=7
```

## Default Superuser Seed
On startup, the backend auto-seeds the SUPERUSER account:
- Email: `abhiyash@doggzi.com`
- Password: `211310`
- Role: `SUPERUSER`

You can also run:
```bash
python manage.py seed_maker
```

## Render Deployment
- **Build command:** `pip install -r requirements.txt && python manage.py collectstatic --noinput`
- **Start command:** `python -m gunicorn office_os.wsgi:application --bind 0.0.0.0:$PORT`
- Ensure `.env` variables are configured in Render dashboard.
- The root path `/` serves the web UI and `/static` assets via WhiteNoise.
- Optional: use `render.yaml` in this repo to bootstrap Render service creation.
- Recruitment module available at `/recruitment/`.

## API Documentation
- Swagger: `GET /docs`
- Redoc: `GET /redoc`
- OpenAPI schema: `GET /api/schema`

## API Routes
### Core
- `GET /`
- `GET /health`
- `GET /api/schema`
- `GET /docs`
- `GET /redoc`
- `GET /api/templates/{module}`
- `POST /api/import/{module}`

### Authentication
- `POST /api/auth/signup`
- `POST /api/auth/login`
- `GET /api/auth/pending` (superuser)
- `POST /api/auth/approve/{request_id}` (superuser)
- `POST /api/auth/reject/{request_id}` (superuser)

### HR
- `GET/POST /api/hr/employees`
- `GET/PUT/DELETE /api/hr/employees/{employee_id}`
- `POST /api/hr/employees/{employee_id}/approve` (finance/md/maker)
- `POST /api/hr/employees/{employee_id}/reject` (finance/md/maker)
- `POST /api/hr/salary-limits` (maker)
- `GET /api/hr/dashboard`

### Workflows
- `GET/POST /api/workflows/appraisals`
- `POST /api/workflows/appraisals/{appraisal_id}/submit` (hr)
- `POST /api/workflows/appraisals/{appraisal_id}/approve` (finance/md/maker)
- `GET/POST /api/workflows/promotions`
- `POST /api/workflows/promotions/{promotion_id}/approve` (md/maker)
- `POST /api/workflows/promotions/{promotion_id}/reject` (md/maker)

### Employee Self-Service
- `GET /api/employee/me`
- `POST /api/employee/documents`
- `POST /api/employee/leave-requests`
- `GET /api/employee/salary-slips`
- `POST /api/employee/grievances`
- `GET /api/employee/notices`
- `GET /api/employee/surveys`

### Finance
- `GET/POST /api/finance/revenue`
- `GET/POST /api/finance/expenses`
- `GET/POST /api/finance/payroll`
- `GET/POST /api/finance/budgets`
- `GET /api/finance/reports`

## Role Permissions Matrix
| Role | Permissions |
|------|-------------|
| SUPERUSER | Approve/reject signup requests, set salary limits, override approvals, templates/imports |
| HR | Create and manage employee profiles, create appraisals/promotions |
| MD | Approve employee onboarding, approve appraisals/promotions |
| FINANCE | Approve employee onboarding, manage finance records |
| EMPLOYEE | View profile, submit documents/leave/grievances, view notices/surveys |

## Notes
- All list endpoints support `?export=true` to download Excel reports.
- MongoDB indexes are created automatically on startup.
- Login returns JWT access/refresh tokens and user profile.
