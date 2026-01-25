from app.repositories.attendance_repo import AttendanceRepo
from app.core.audit import audit

class AttendanceService:
    def list(self, request, query: dict, skip: int, limit: int):
        repo = AttendanceRepo()
        items = repo.list(query, skip, limit)
        total = repo.count(query)
        return items, total

    def upsert(self, request, data: dict):
        repo = AttendanceRepo()
        doc = repo.upsert(data)
        audit(request, "UPSERT", "attendance", doc["id"], {"date": doc.get("date")})
        return doc
