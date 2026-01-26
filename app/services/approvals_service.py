from app.core.errors import NotFound
from app.core.security import require_company_id, require_user_id
from app.core.audit import audit
from app.repositories.approvals_repo import ApprovalsRepo

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
        matched, doc = repo.set_status(id, company_id, status, user_id, comment)
        if matched == 0 or not doc:
            raise NotFound("Approval not found")
        audit(request, status.upper(), "approval", id, {"status": status})
        return doc
