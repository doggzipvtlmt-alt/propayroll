import hashlib
from fastapi import Request
from app.core.errors import Unauthorized

ALLOWED_ROLES = {"MD", "HR", "FINANCE", "ADMIN", "EMPLOYEE"}

def get_company_id(request: Request) -> str | None:
    if hasattr(request.state, "company_id") and request.state.company_id:
        return request.state.company_id
    return request.headers.get("X-COMPANY-ID")

def require_company_id(request: Request) -> str:
    company_id = get_company_id(request)
    if not company_id:
        raise Unauthorized("Authentication required")
    return company_id

def get_user_id(request: Request) -> str | None:
    if hasattr(request.state, "user_id") and request.state.user_id:
        return request.state.user_id
    return request.headers.get("X-USER-ID")

def require_user_id(request: Request) -> str:
    user_id = get_user_id(request)
    if not user_id:
        raise Unauthorized("Authentication required")
    return user_id

def get_role(request: Request) -> str:
    state_role = getattr(request.state, "role", None)
    role = state_role or request.headers.get("X-ROLE", "EMPLOYEE")
    role = role.upper()
    if role not in ALLOWED_ROLES:
        return "EMPLOYEE"
    return role


def get_bearer_token(request: Request) -> str | None:
    auth = request.headers.get("Authorization")
    if not auth:
        return None
    parts = auth.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
