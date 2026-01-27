import secrets
from app.core.errors import NotFound, AppError
from app.core.security import require_company_id, require_user_id
from app.core.audit import audit
from app.core.crypto import hash_secret
from app.repositories.approvals_repo import ApprovalsRepo
from app.repositories.notifications_repo import NotificationsRepo
from app.repositories.users_repo import UsersRepo

class ApprovalsService:
    def list(self, request, query: dict, skip: int, limit: int):
        company_id = require_company_id(request)
        require_user_id(request)
        query = {**query, "company_id": company_id}
        repo = ApprovalsRepo()
        items = repo.list(query, skip, limit)
        total = repo.count(query)
        return items, total

    def create(self, request, data: dict):
        company_id = require_company_id(request)
        user_id = require_user_id(request)
        data["company_id"] = company_id
        data["status"] = "pending"
        data["requested_by_user_id"] = user_id
        data["decided_by_user_id"] = None
        data["decision_comment"] = ""
        repo = ApprovalsRepo()
        doc = repo.create(data)
        audit(request, "CREATE", "approval", doc["id"], {"entity_type": doc.get("entity_type")})
        return doc

    def approve(self, request, id: str, comment: str | None = None):
        return self._decide(request, id, "approved", comment)

    def reject(self, request, id: str, comment: str | None = None):
        return self._decide(request, id, "rejected", comment)

    def _decide(self, request, id: str, status: str, comment: str | None = None):
        company_id = require_company_id(request)
        user_id = require_user_id(request)
        repo = ApprovalsRepo()
        approval = repo.get(id, company_id)
        if not approval:
            raise NotFound("Approval not found")
        matched, doc = repo.set_status(id, company_id, status, user_id, comment)
        if matched == 0 or not doc:
            raise NotFound("Approval not found")
        if approval.get("entity_type") == "user_signup":
            self._handle_user_signup_decision(company_id, approval, status, comment)
        audit(request, status.upper(), "approval", id, {"status": status})
        return doc

    def _handle_user_signup_decision(self, company_id: str, approval: dict, status: str, comment: str | None = None) -> None:
        user_id = approval.get("entity_id")
        users_repo = UsersRepo()
        user = users_repo.get(user_id, company_id)
        if not user:
            raise AppError("Signup user not found")
        notifications_repo = NotificationsRepo()
        if status == "approved":
            role_key = user.get("requested_role_key") or user.get("role_key") or "EMPLOYEE"
            temp_password = secrets.token_urlsafe(10)
            password_meta = hash_secret(temp_password)
            users_repo.set_credentials(user_id, company_id, "active", role_key, password_meta)
            notifications_repo.create_one({
                "company_id": company_id,
                "user_id": user_id,
                "title": "Signup approved",
                "message": f"Your account has been approved. Temporary password: {temp_password}",
                "type": "success",
            })
        elif status == "rejected":
            users_repo.set_status(user_id, company_id, "REJECTED")
            notifications_repo.create_one({
                "company_id": company_id,
                "user_id": user_id,
                "title": "Signup rejected",
                "message": f"Your signup request was rejected. {comment or ''}".strip(),
                "type": "error",
            })
