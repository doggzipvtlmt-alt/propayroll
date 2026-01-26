from app.core.security import require_company_id, require_user_id
from app.repositories.audit_repo import AuditRepo

class AuditService:
    def list(self, request, query: dict, skip: int, limit: int):
        company_id = require_company_id(request)
        require_user_id(request)
        query = {**query, "company_id": company_id}
        repo = AuditRepo()
        items = repo.list(query, skip, limit)
        total = repo.count(query)
        return items, total
