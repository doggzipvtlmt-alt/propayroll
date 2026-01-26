from datetime import datetime, timedelta, timezone
import secrets
from app.core.crypto import verify_secret
from app.core.errors import Unauthorized, NotFound
from app.core.security import hash_token
from app.repositories.employees_repo import EmployeesRepo
from app.repositories.sessions_repo import SessionsRepo
from app.repositories.users_repo import UsersRepo


SESSION_TTL_DAYS = 7


class AuthService:
    def login(self, company_id: str, identifier: str, dob_or_pin: str, user_agent: str | None, ip: str | None):
        user = self._find_user(company_id, identifier)
        if not user:
            raise Unauthorized("Invalid credentials")
        if user.get("status") != "active":
            raise Unauthorized("User is inactive")

        if user.get("dob") and dob_or_pin == user.get("dob"):
            pass
        elif verify_secret(dob_or_pin, user.get("pin_hash"), user.get("pin_salt"), user.get("pin_iterations")):
            pass
        else:
            raise Unauthorized("Invalid credentials")

        token = secrets.token_urlsafe(32)
        token_hash = hash_token(token)
        expires_at = datetime.now(timezone.utc) + timedelta(days=SESSION_TTL_DAYS)
        SessionsRepo().create({
            "token_hash": token_hash,
            "company_id": company_id,
            "user_id": user["id"],
            "role_key": user.get("role_key", "EMPLOYEE"),
            "expires_at": expires_at,
            "user_agent": user_agent,
            "ip": ip,
        })
        return {
            "access_token": token,
            "user": {
                "id": user["id"],
                "full_name": user.get("full_name"),
                "role_key": user.get("role_key", "EMPLOYEE"),
                "company_id": company_id,
            },
        }

    def logout(self, token: str | None):
        if not token:
            return 0
        token_hash = hash_token(token)
        return SessionsRepo().delete_by_token_hash(token_hash)

    def me(self, company_id: str, user_id: str):
        user = UsersRepo().get(user_id, company_id)
        if not user:
            raise NotFound("User not found")
        return self._sanitize(user)

    def _find_user(self, company_id: str, identifier: str):
        users_repo = UsersRepo()
        if "@" in identifier:
            return users_repo.find_by_email(company_id, identifier.lower())
        employee = EmployeesRepo().find_by_code(company_id, identifier)
        if not employee:
            return None
        user_id = employee.get("user_id")
        if not user_id:
            return None
        return users_repo.get(str(user_id), company_id)

    def _sanitize(self, doc: dict) -> dict:
        doc = {**doc}
        for key in ["pin_hash", "pin_salt", "pin_iterations"]:
            doc.pop(key, None)
        return doc
