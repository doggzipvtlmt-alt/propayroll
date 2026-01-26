from app.core.crypto import hash_secret, mask_secret
from app.core.errors import NotFound, Forbidden
from app.core.security import require_company_id, require_user_id
from app.repositories.vault_repo import VaultRepo
from app.core.audit import audit

class VaultService:
    def list(self, request, query: dict, skip: int, limit: int):
        company_id = require_company_id(request)
        user_id = require_user_id(request)
        role = getattr(request.state, "role", "EMPLOYEE")
        base_query = {"company_id": company_id}
        if role != "MD":
            base_query["owner_user_id"] = user_id
        query = {**query, **base_query}
        repo = VaultRepo()
        items = [self._mask(repo_item) for repo_item in repo.list(query, skip, limit)]
        total = repo.count(query)
        return items, total

    def get(self, request, id: str):
        company_id = require_company_id(request)
        user_id = require_user_id(request)
        role = getattr(request.state, "role", "EMPLOYEE")
        repo = VaultRepo()
        doc = repo.get(id, company_id)
        if not doc:
            raise NotFound("Vault item not found")
        if role != "MD" and doc.get("owner_user_id") != user_id:
            raise Forbidden("You do not have access to this vault item")
        return self._mask(doc)

    def create(self, request, data: dict):
        company_id = require_company_id(request)
        user_id = require_user_id(request)
        data["company_id"] = company_id
        data["owner_user_id"] = user_id
        password_meta = hash_secret(data.pop("password"))
        notes_value = data.pop("notes", None)
        notes_meta = hash_secret(notes_value) if notes_value else {}
        data.update({
            "password_hash": password_meta.get("hash"),
            "password_salt": password_meta.get("salt"),
            "password_iterations": password_meta.get("iterations"),
            "notes_hash": notes_meta.get("hash"),
            "notes_salt": notes_meta.get("salt"),
            "notes_iterations": notes_meta.get("iterations"),
        })
        repo = VaultRepo()
        doc = repo.create(data)
        audit(request, "CREATE", "vault_item", doc["id"], {"title": doc.get("title")})
        return self._mask(doc)

    def update(self, request, id: str, data: dict):
        company_id = require_company_id(request)
        user_id = require_user_id(request)
        role = getattr(request.state, "role", "EMPLOYEE")
        repo = VaultRepo()
        existing = repo.get(id, company_id)
        if not existing:
            raise NotFound("Vault item not found")
        if role != "MD" and existing.get("owner_user_id") != user_id:
            raise Forbidden("You do not have access to this vault item")
        matched, doc = repo.update(id, company_id, data)
        if matched == 0 or not doc:
            raise NotFound("Vault item not found")
        audit(request, "UPDATE", "vault_item", id, {"title": doc.get("title")})
        return self._mask(doc)

    def reset_secret(self, request, id: str, password: str | None, notes: str | None):
        company_id = require_company_id(request)
        user_id = require_user_id(request)
        role = getattr(request.state, "role", "EMPLOYEE")
        repo = VaultRepo()
        existing = repo.get(id, company_id)
        if not existing:
            raise NotFound("Vault item not found")
        if role != "MD" and existing.get("owner_user_id") != user_id:
            raise Forbidden("You do not have access to this vault item")
        update: dict = {}
        if password:
            password_meta = hash_secret(password)
            update.update({
                "password_hash": password_meta.get("hash"),
                "password_salt": password_meta.get("salt"),
                "password_iterations": password_meta.get("iterations"),
            })
        if notes is not None:
            notes_meta = hash_secret(notes) if notes else {}
            update.update({
                "notes_hash": notes_meta.get("hash"),
                "notes_salt": notes_meta.get("salt"),
                "notes_iterations": notes_meta.get("iterations"),
            })
        if update:
            repo.update(id, company_id, update)
        doc = repo.get(id, company_id)
        audit(request, "RESET_SECRET", "vault_item", id, {"title": doc.get("title")})
        return self._mask(doc)

    def delete(self, request, id: str):
        company_id = require_company_id(request)
        user_id = require_user_id(request)
        role = getattr(request.state, "role", "EMPLOYEE")
        repo = VaultRepo()
        doc = repo.get(id, company_id)
        if not doc:
            raise NotFound("Vault item not found")
        if role != "MD" and doc.get("owner_user_id") != user_id:
            raise Forbidden("You do not have access to this vault item")
        deleted = repo.delete(id, company_id)
        if deleted == 0:
            raise NotFound("Vault item not found")
        audit(request, "DELETE", "vault_item", id)
        return True

    def _mask(self, doc: dict) -> dict:
        doc = {**doc}
        doc["password"] = mask_secret(doc.get("password_hash"))
        doc["notes"] = mask_secret(doc.get("notes_hash"))
        for key in ["password_hash", "password_salt", "password_iterations", "notes_hash", "notes_salt", "notes_iterations"]:
            doc.pop(key, None)
        return doc
