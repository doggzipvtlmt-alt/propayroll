from datetime import datetime, timezone
from app.core.db import require_db
from app.utils.oid import with_id

class AttendanceRepo:
    def __init__(self):
        self.db = require_db()

    def list(self, query: dict, skip: int, limit: int):
        cursor = self.db.attendance.find(query).sort([("date", -1)]).skip(skip).limit(limit)
        return [with_id(d) for d in cursor]

    def count(self, query: dict) -> int:
        return self.db.attendance.count_documents(query)

    def upsert(self, data: dict):
        # unique by (date, employee_id) because of index
        now = datetime.now(timezone.utc).isoformat()
        data["updated_at"] = now
        data.setdefault("created_at", now)

        key = {"date": data["date"], "employee_id": data["employee_id"]}
        self.db.attendance.update_one(key, {"": data}, upsert=True)
        doc = self.db.attendance.find_one(key)
        return with_id(doc)
