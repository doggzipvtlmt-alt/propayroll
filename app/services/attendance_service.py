from app.repositories.attendance_repo import AttendanceRepo
from app.core.audit import audit
from app.core.security import require_company_id, require_user_id

class AttendanceService:
    def list(self, request, query: dict, skip: int, limit: int):
        company_id = require_company_id(request)
        require_user_id(request)
        query = {**query, "company_id": company_id}
        repo = AttendanceRepo()
        items = repo.list(query, skip, limit)
        total = repo.count(query)
        return items, total

    def upsert(self, request, data: dict):
        company_id = require_company_id(request)
        require_user_id(request)
        data["company_id"] = company_id
        repo = AttendanceRepo()
        doc = repo.upsert(data)
        audit(request, "UPSERT", "attendance", doc["id"], {"date": doc.get("date")})
        return doc
