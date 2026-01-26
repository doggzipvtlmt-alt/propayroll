from app.core.audit import audit
from app.core.errors import NotFound
from app.core.security import require_company_id, require_user_id
from app.repositories.leaves_repo import LeavesRepo
from app.repositories.approvals_repo import ApprovalsRepo
from app.repositories.notifications_repo import NotificationsRepo
from app.repositories.users_repo import UsersRepo

class LeavesService:
    def list(self, request, query: dict, skip: int, limit: int, sort):
        company_id = require_company_id(request)
        require_user_id(request)
        query = {**query, "company_id": company_id}
        repo = LeavesRepo()
        items = repo.list(query, skip, limit, sort)
        total = repo.count(query)
        return items, total

    def create(self, request, data: dict):
        company_id = require_company_id(request)
        user_id = require_user_id(request)
        data["company_id"] = company_id
        data["requested_by_user_id"] = user_id
        repo = LeavesRepo()
        doc = repo.create(data)

        approvals_repo = ApprovalsRepo()
        approvals_repo.create({
            "company_id": company_id,
            "entity_type": "leave",
            "entity_id": doc["id"],
            "workflow_key": "leave_default",
            "current_step": 1,
            "status": "pending",
            "requested_by_user_id": user_id,
            "decided_by_user_id": None,
            "decision_comment": "",
        })

        users_repo = UsersRepo()
        hr_users = users_repo.list({"company_id": company_id, "role_key": "HR", "status": "active"}, 0, 500)
        notifications = []
        for hr_user in hr_users:
            notifications.append({
                "company_id": company_id,
                "user_id": hr_user["id"],
                "title": "New leave request",
                "message": f"{doc.get('employee_name') or doc.get('employee_id')} requested leave.",
                "type": "info",
                "read": False,
            })
        NotificationsRepo().create_many(notifications)

        audit(request, "CREATE", "leave", doc["id"], {"status": doc.get("status")})
        return doc

    def approve(self, request, id: str, comment: str | None = None):
        return self._decide(request, id, "approved", comment)

    def reject(self, request, id: str, comment: str | None = None):
        return self._decide(request, id, "rejected", comment)

    def _decide(self, request, id: str, status: str, comment: str | None = None):
        company_id = require_company_id(request)
        user_id = require_user_id(request)
        repo = LeavesRepo()
        matched, doc = repo.set_status(id, company_id, status, comment or "")
        if matched == 0 or not doc:
            raise NotFound("Leave request not found")

        ApprovalsRepo().set_status_by_entity(company_id, "leave", id, status, user_id, comment)

        requester_id = doc.get("requested_by_user_id")
        if requester_id:
            NotificationsRepo().create_one({
                "company_id": company_id,
                "user_id": requester_id,
                "title": f"Leave {status}",
                "message": f"Your leave request was {status}.",
                "type": "success" if status == "approved" else "warn",
                "read": False,
            })

        audit(request, status.upper(), "leave", id, {"status": status})
        return doc
