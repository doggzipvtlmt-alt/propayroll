from fastapi import Request
from app.core.errors import MissingHeader

ALLOWED_ROLES = {"MD", "HR", "FINANCE", "ADMIN", "EMPLOYEE"}

def get_company_id(request: Request) -> str | None:
    return request.headers.get("X-COMPANY-ID")

def require_company_id(request: Request) -> str:
    company_id = get_company_id(request)
    if not company_id:
        raise MissingHeader("X-COMPANY-ID header required", {"header": "X-COMPANY-ID"})
    return company_id

def get_user_id(request: Request) -> str | None:
    return request.headers.get("X-USER-ID")

def require_user_id(request: Request) -> str:
    user_id = get_user_id(request)
    if not user_id:
        raise MissingHeader("X-USER-ID header required", {"header": "X-USER-ID"})
    return user_id

def get_role(request: Request) -> str:
    role = request.headers.get("X-ROLE", "EMPLOYEE").upper()
    if role not in ALLOWED_ROLES:
        return "EMPLOYEE"
    return role
