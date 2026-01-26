from pymongo.errors import DuplicateKeyError
from app.core.errors import NotFound, Conflict
from app.core.audit import audit
from app.repositories.companies_repo import CompaniesRepo
from app.core.security import require_user_id

class CompaniesService:
    def list(self, request, query: dict, skip: int, limit: int):
        require_user_id(request)
        repo = CompaniesRepo()
        items = repo.list(query, skip, limit)
        total = repo.count(query)
        return items, total

    def get(self, request, id: str):
        require_user_id(request)
        repo = CompaniesRepo()
        doc = repo.get(id)
        if not doc:
            raise NotFound("Company not found")
        return doc

    def create(self, request, data: dict):
        require_user_id(request)
        repo = CompaniesRepo()
        try:
            doc = repo.create(data)
        except DuplicateKeyError:
            raise Conflict("Company name already exists", {"field": "name"})
        audit(request, "CREATE", "company", doc["id"], {"name": doc.get("name")})
        return doc

    def update(self, request, id: str, data: dict):
        require_user_id(request)
        repo = CompaniesRepo()
        matched, doc = repo.update(id, data)
        if matched == 0 or not doc:
            raise NotFound("Company not found")
        audit(request, "UPDATE", "company", id, {"name": doc.get("name")})
        return doc
