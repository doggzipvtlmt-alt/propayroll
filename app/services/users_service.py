from pymongo.errors import DuplicateKeyError
from app.core.errors import NotFound, Conflict
from app.core.security import require_company_id, require_user_id
from app.core.audit import audit
from app.core.crypto import hash_secret
from app.repositories.users_repo import UsersRepo

class UsersService:
    def list(self, request, query: dict, skip: int, limit: int):
        company_id = require_company_id(request)
        require_user_id(request)
        query = {**query, "company_id": company_id}
        repo = UsersRepo()
        items = [self._sanitize(doc) for doc in repo.list(query, skip, limit)]
        total = repo.count(query)
        return items, total

    def create(self, request, data: dict):
        company_id = require_company_id(request)
        require_user_id(request)
        data["company_id"] = company_id
        pin = data.pop("pin", None)
        if pin:
            pin_meta = hash_secret(pin)
            data.update({
                "pin_hash": pin_meta.get("hash"),
                "pin_salt": pin_meta.get("salt"),
                "pin_iterations": pin_meta.get("iterations"),
            })
        repo = UsersRepo()
        try:
            doc = repo.create(data)
        except DuplicateKeyError:
            raise Conflict("User email already exists", {"field": "email"})
        audit(request, "CREATE", "user", doc["id"], {"email": doc.get("email")})
        return self._sanitize(doc)

    def update(self, request, id: str, data: dict):
        company_id = require_company_id(request)
        require_user_id(request)
        pin = data.pop("pin", None)
        if pin:
            pin_meta = hash_secret(pin)
            data.update({
                "pin_hash": pin_meta.get("hash"),
                "pin_salt": pin_meta.get("salt"),
                "pin_iterations": pin_meta.get("iterations"),
            })
        repo = UsersRepo()
        matched, doc = repo.update(id, company_id, data)
        if matched == 0 or not doc:
            raise NotFound("User not found")
        audit(request, "UPDATE", "user", id, {"email": doc.get("email")})
        return self._sanitize(doc)

    def set_status(self, request, id: str, status: str):
        company_id = require_company_id(request)
        require_user_id(request)
        repo = UsersRepo()
        matched, doc = repo.set_status(id, company_id, status)
        if matched == 0 or not doc:
            raise NotFound("User not found")
        audit(request, "UPDATE", "user_status", id, {"status": status})
        return self._sanitize(doc)

    def _sanitize(self, doc: dict) -> dict:
        doc = {**doc}
        for key in ["pin_hash", "pin_salt", "pin_iterations"]:
            doc.pop(key, None)
        return doc
