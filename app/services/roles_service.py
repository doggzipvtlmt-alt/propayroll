from pymongo.errors import DuplicateKeyError
from app.core.errors import NotFound, Conflict
from app.core.security import require_company_id, require_user_id
from app.core.audit import audit
from app.repositories.roles_repo import RolesRepo

class RolesService:
    def list(self, request, query: dict, skip: int, limit: int):
        company_id = require_company_id(request)
        require_user_id(request)
        query = {**query, "company_id": company_id}
        repo = RolesRepo()
        items = repo.list(query, skip, limit)
        total = repo.count(query)
        return items, total

    def create(self, request, data: dict):
        company_id = require_company_id(request)
        require_user_id(request)
        data["company_id"] = company_id
        repo = RolesRepo()
        try:
            doc = repo.create(data)
        except DuplicateKeyError:
            raise Conflict("Role key already exists", {"field": "key"})
        audit(request, "CREATE", "role", doc["id"], {"key": doc.get("key")})
        return doc

    def update(self, request, id: str, data: dict):
        company_id = require_company_id(request)
        require_user_id(request)
        repo = RolesRepo()
        matched, doc = repo.update(id, company_id, data)
        if matched == 0 or not doc:
            raise NotFound("Role not found")
        audit(request, "UPDATE", "role", id, {"key": doc.get("key")})
        return doc

    def delete(self, request, id: str):
        company_id = require_company_id(request)
        require_user_id(request)
        repo = RolesRepo()
        deleted = repo.delete(id, company_id)
        if deleted == 0:
            raise NotFound("Role not found")
        audit(request, "DELETE", "role", id)
        return True
