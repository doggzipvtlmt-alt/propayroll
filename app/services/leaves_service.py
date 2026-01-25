from app.core.errors import NotFound
from app.repositories.leaves_repo import LeavesRepo
from app.core.audit import audit

class LeavesService:
    def list(self, request, query: dict, skip: int, limit: int, sort):
        repo = LeavesRepo()
        items = repo.list(query, skip, limit, sort)
        total = repo.count(query)
        return items, total

    def create(self, request, data: dict):
        repo = LeavesRepo()
        doc = repo.create(data)
        audit(request, "CREATE", "leave", doc["id"], {"leave_type": doc.get("leave_type")})
        return doc

    def approve(self, request, id: str, comment: str = ""):
        repo = LeavesRepo()
        matched, doc = repo.set_status(id, "approved", comment)
        if matched == 0 or not doc:
            raise NotFound("Leave request not found")
        audit(request, "APPROVE", "leave", id, {"comment": comment})
        return doc

    def reject(self, request, id: str, comment: str = ""):
        repo = LeavesRepo()
        matched, doc = repo.set_status(id, "rejected", comment)
        if matched == 0 or not doc:
            raise NotFound("Leave request not found")
        audit(request, "REJECT", "leave", id, {"comment": comment})
        return doc
