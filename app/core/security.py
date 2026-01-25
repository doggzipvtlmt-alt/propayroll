from fastapi import Request

def get_role(request: Request) -> str:
    role = request.headers.get("X-ROLE", "EMPLOYEE").upper()
    if role not in {"HR", "MD", "EMPLOYEE"}:
        return "EMPLOYEE"
    return role
