from datetime import datetime, timedelta, timezone
import secrets
from app.core.crypto import verify_secret
from app.core.errors import Unauthorized, NotFound, Conflict, AppError
from app.core.security import hash_token
from app.repositories.approvals_repo import ApprovalsRepo
from app.repositories.companies_repo import CompaniesRepo
from app.repositories.notifications_repo import NotificationsRepo
from app.repositories.sessions_repo import SessionsRepo
from app.repositories.users_repo import UsersRepo


SESSION_TTL_DAYS = 7
ALLOWED_DOMAINS = ("@doggzi.com",)


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

    def register(self, payload: dict) -> dict:
        email = payload.get("email", "").strip().lower()
        if not any(email.endswith(domain) for domain in ALLOWED_DOMAINS):
            raise AppError("Registration requires a @doggzi.com email")
        role_requested = (payload.get("role_requested") or "").upper()
        if role_requested not in {"HR", "MD", "EMPLOYEE", "FINANCE"}:
            raise AppError("Invalid role requested")
        company = self._ensure_company()
        company_id = company["id"]
        users_repo = UsersRepo()
        existing = users_repo.find_by_email(company_id, email)
        if existing:
            raise Conflict("User email already exists", {"field": "email"})
        user_doc = users_repo.create({
            "company_id": company_id,
            "full_name": payload.get("full_name"),
            "email": email,
            "phone": payload.get("phone"),
            "role_key": role_requested,
            "requested_role_key": role_requested,
            "status": "PENDING_APPROVAL",
        })
        approval = ApprovalsRepo().create({
            "company_id": company_id,
            "entity_type": "user_signup",
            "entity_id": user_doc["id"],
            "workflow_key": "user_signup_default",
            "current_step": 1,
            "status": "pending",
            "requested_by_user_id": user_doc["id"],
            "decided_by_user_id": None,
            "decision_comment": "",
        })
        superuser = users_repo.find_by_email(company_id, "abhiyash@doggzi.com")
        if superuser:
            NotificationsRepo().create_one({
                "company_id": company_id,
                "user_id": superuser["id"],
                "title": "New signup approval required",
                "message": f"Signup request for {user_doc.get('full_name')} ({email}) requires approval.",
                "type": "info",
            })
        return {"user_id": user_doc["id"], "approval_id": approval["id"], "status": user_doc["status"]}

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

    def _ensure_company(self) -> dict:
        repo = CompaniesRepo()
        company = repo.find_by_name("Doggzi Pvt Ltd")
        if company:
            return company
        doc = repo.create({
            "name": "Doggzi Pvt Ltd",
            "legal_name": "Doggzi Private Limited",
            "gstin": "29ABCDE1234F1Z5",
            "pan": "ABCDE1234F",
            "address": "Gurgaon, India",
            "phone": "+91-99999-00000",
            "email": "contact@doggzi.com",
            "currency": "INR",
            "timezone": "Asia/Kolkata",
            "jurisdiction": "Gurgaon, India",
        })
        return doc

    def _sanitize(self, doc: dict) -> dict:
        doc = {**doc}
        for key in ["pin_hash", "pin_salt", "pin_iterations", "password_hash", "password_salt", "password_iterations"]:
            doc.pop(key, None)
        return doc
