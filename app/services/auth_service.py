from datetime import datetime, timedelta, timezone
import secrets
from app.core.crypto import verify_secret
from app.core.errors import Unauthorized, NotFound
from app.core.security import hash_token
from app.repositories.sessions_repo import SessionsRepo
from app.repositories.users_repo import UsersRepo


SESSION_TTL_DAYS = 7


class AuthService:
    def login(self, email: str, password: str, user_agent: str | None, ip: str | None):
        user, reason = self.validate_login(email, password)
        if reason == "inactive":
            raise Unauthorized("User is inactive")
        if reason:
            raise Unauthorized("Invalid credentials")
        return self._issue_session(user, user_agent, ip)

    def login_with_user(self, user: dict, user_agent: str | None, ip: str | None) -> dict:
        return self._issue_session(user, user_agent, ip)

    def validate_login(self, email: str, password: str) -> tuple[dict | None, str | None]:
        user = self._find_user(email)
        if not user:
            return None, "user_not_found"
        if not user.get("company_id") or not user.get("role_key"):
            return None, "invalid_profile"
        if not user.get("password_hash") or not user.get("password_salt"):
            return None, "invalid_credentials"
        if user.get("status") != "active":
            return None, "inactive"
        if not verify_secret(password, user.get("password_hash"), user.get("password_salt"), user.get("password_iterations")):
            return None, "bad_password"
        return user, None

    def _issue_session(self, user: dict, user_agent: str | None, ip: str | None) -> dict:
        token = secrets.token_urlsafe(32)
        token_hash = hash_token(token)
        expires_at = datetime.now(timezone.utc) + timedelta(days=SESSION_TTL_DAYS)
        company_id = user.get("company_id")
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
                "email": user.get("email"),
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

    def _find_user(self, email: str):
        users_repo = UsersRepo()
        return users_repo.find_by_email_case_insensitive(email.strip())

    def _sanitize(self, doc: dict) -> dict:
        doc = {**doc}
        for key in ["pin_hash", "pin_salt", "pin_iterations", "password_hash", "password_salt", "password_iterations"]:
            doc.pop(key, None)
        return doc
