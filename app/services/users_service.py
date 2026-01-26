from pymongo.errors import DuplicateKeyError
from app.core.errors import NotFound, Conflict
from app.core.security import require_company_id, require_user_id
from app.core.audit import audit
from app.repositories.users_repo import UsersRepo

class UsersService:
    def list(self, request, query: dict, skip: int, limit: int):
        company_id = require_company_id(request)
        require_user_id(request)
        query = {**query, "company_id": company_id}
        repo = UsersRepo()
        items = repo.list(query, skip, limit)
        total = repo.count(query)
        return items, total

    def create(self, request, data: dict):
        company_id = require_company_id(request)
        require_user_id(request)
        data["company_id"] = company_id
        repo = UsersRepo()
        try:
            doc = repo.create(data)
        except DuplicateKeyError:
            raise Conflict("User email already exists", {"field": "email"})
        audit(request, "CREATE", "user", doc["id"], {"email": doc.get("email")})
        return doc

    def update(self, request, id: str, data: dict):
        company_id = require_company_id(request)
        require_user_id(request)
        repo = UsersRepo()
        matched, doc = repo.update(id, company_id, data)
        if matched == 0 or not doc:
            raise NotFound("User not found")
        audit(request, "UPDATE", "user", id, {"email": doc.get("email")})
        return doc

    def set_status(self, request, id: str, status: str):
        company_id = require_company_id(request)
        require_user_id(request)
        repo = UsersRepo()
        matched, doc = repo.set_status(id, company_id, status)
        if matched == 0 or not doc:
            raise NotFound("User not found")
        audit(request, "UPDATE", "user_status", id, {"status": status})
        return doc
