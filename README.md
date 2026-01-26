# Propayroll Office OS Backend

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export MONGO_URI="mongodb://localhost:27017"
export MONGO_DB="hrms"
uvicorn app.main:app --reload
```

## Required headers (simulated identity)

All tenant-scoped endpoints expect these headers:

- `X-COMPANY-ID`: Company ID string
- `X-USER-ID`: User ID string
- `X-ROLE`: Role key (MD, HR, FINANCE, ADMIN, EMPLOYEE). Defaults to `EMPLOYEE`.

### PowerShell example (Invoke-WebRequest)

```powershell
iwr -Method Get `
  -Uri http://localhost:8000/api/employees?page=1&page_size=10 `
  -Headers @{
    "X-COMPANY-ID" = "<company_id>"
    "X-USER-ID" = "<user_id>"
    "X-ROLE" = "HR"
  }
```

## Key endpoints

- Employees: `GET/POST/PUT/DELETE /api/employees`
- Leaves: `GET/POST /api/leaves`, `PUT /api/leaves/{id}/approve|reject`
- Attendance: `GET/POST /api/attendance`
- Dashboard: `GET /api/dashboard/summary`
- Meta: `GET /api/meta/departments|designations|leave-types`
- Companies: `GET/POST/PUT /api/companies`
- Roles: `GET/POST/PUT/DELETE /api/roles`
- Users: `GET/POST/PUT /api/users`, `PATCH /api/users/{id}/status`
- Approvals: `GET/POST /api/approvals`, `PUT /api/approvals/{id}/approve|reject`
- Notifications: `GET /api/notifications`, `PUT /api/notifications/{id}/read`, `PUT /api/notifications/read-all`
- Vault: `GET/POST /api/vault`, `GET/PUT/DELETE /api/vault/{id}`, `PUT /api/vault/{id}/reset-secret`
- Audit Logs: `GET /api/audit`
