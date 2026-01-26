from fastapi import Request
from app.core.errors import Forbidden

ROLE_PERMISSIONS = {
    "MD": ["*"],
    "HR": [
        "employees:*",
        "leaves:*",
        "attendance:read",
    ],
    "FINANCE": [
        "finance:*",
        "payroll:*",
        "employees:read",
    ],
    "ADMIN": [
        "admin:*",
        "employees:read",
        "audit:read",
    ],
    "EMPLOYEE": [
        "leaves:read",
        "leaves:write",
        "attendance:read",
        "vault:read",
        "vault:write",
        "payslip:read",
    ],
}

def role_permissions(role_key: str) -> list[str]:
    return ROLE_PERMISSIONS.get(role_key, ROLE_PERMISSIONS["EMPLOYEE"])

def permission_allows(permissions: list[str], required: str) -> bool:
    for perm in permissions:
        if perm == "*":
            return True
        if perm == required:
            return True
        if perm.endswith(":*"):
            prefix = perm.split(":", 1)[0]
            if required.startswith(f"{prefix}:"):
                return True
    return False

def require_permission(request: Request, permission: str) -> None:
    role = getattr(request.state, "role", "EMPLOYEE")
    permissions = role_permissions(role)
    if not permission_allows(permissions, permission):
        raise Forbidden("You do not have permission to perform this action", {"permission": permission})
