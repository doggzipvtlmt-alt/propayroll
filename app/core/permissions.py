from fastapi import Request
from app.core.errors import Forbidden

ROLE_PERMISSIONS = {
    "MD": ["*"],
    "HR": [
        "employees:read",
        "employees:write",
        "leaves:read",
        "leaves:write",
        "leaves:approve",
        "attendance:read",
        "vault:read",
        "vault:write",
    ],
    "FINANCE": [
        "finance:read",
        "finance:write",
        "payroll:read",
        "payroll:write",
        "employees:read",
    ],
    "ADMIN": [
        "admin:read",
        "admin:write",
        "attendance:read",
        "attendance:write",
        "employees:read",
    ],
    "EMPLOYEE": [
        "employees:read",
        "leaves:read",
        "leaves:write",
        "attendance:read",
        "vault:read",
        "vault:write",
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
