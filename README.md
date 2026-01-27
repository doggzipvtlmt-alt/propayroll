# Doggzi Office OS Backend (Django + DRF + MongoDB)

Production-ready HRMS/Office OS backend for Doggzi Pvt Ltd using Django, DRF, and MongoDB Atlas.

## Features
- Approval-based onboarding with maker-only approvals
- Role-based access: MAKER, HR, MD, EMPLOYEE, FINANCE
- HR employee onboarding with finance/MD/maker approvals
- Appraisal and promotion workflows
- Employee self-service module
- Finance module with revenue/expense/payroll/budget entries
- Excel export/import for list endpoints
- Swagger and Redoc documentation
- MongoDB Atlas (pymongo) with startup checks and indexes

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
MONGO_DB_NAME=propayroll

JWT_ACCESS_MINUTES=60
JWT_REFRESH_DAYS=7
```

## Default Maker Seed
On startup, the backend auto-seeds the MAKER user:
- Email: `abhiyash@doggzi.com`
- Password: `211310`
- Role: `MAKER`

You can also run:
```bash
python manage.py seed_maker
```

## Render Deployment
- **Build command:** `pip install -r requirements.txt`
- **Start command:** `gunicorn office_os.wsgi:application`
- Ensure `.env` variables are configured in Render dashboard.

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
- `GET /api/auth/pending` (maker)
- `POST /api/auth/approve/{request_id}` (maker)
- `POST /api/auth/reject/{request_id}` (maker)

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
| MAKER | Approve/reject signup requests, set salary limits, override approvals, templates/imports |
| HR | Create and manage employee profiles, create appraisals/promotions |
| MD | Approve employee onboarding, approve appraisals/promotions |
| FINANCE | Approve employee onboarding, manage finance records |
| EMPLOYEE | View profile, submit documents/leave/grievances, view notices/surveys |

## Notes
- All list endpoints support `?export=true` to download Excel reports.
- MongoDB indexes are created automatically on startup.
- Login returns JWT access/refresh tokens and user profile.
