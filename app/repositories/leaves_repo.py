from datetime import datetime, timezone
from app.core.db import require_db
from app.utils.oid import to_objectid, with_id

class LeavesRepo:
    def __init__(self):
        self.db = require_db()

    def list(self, query: dict, skip: int, limit: int, sort: list[tuple]):
        cursor = self.db.leave_requests.find(query).sort(sort).skip(skip).limit(limit)
        return [with_id(d) for d in cursor]

    def count(self, query: dict) -> int:
        return self.db.leave_requests.count_documents(query)

    def get(self, id: str):
        doc = self.db.leave_requests.find_one({"_id": to_objectid(id)})
        return with_id(doc) if doc else None

    def create(self, data: dict):
        now = datetime.now(timezone.utc).isoformat()
        data["created_at"] = now
        data["updated_at"] = now
        data["status"] = "pending"
        data["approver_comment"] = ""
        res = self.db.leave_requests.insert_one(data)
        return self.get(str(res.inserted_id))

    def set_status(self, id: str, status: str, comment: str = ""):
        update = {
            "": {
                "status": status,
                "approver_comment": comment or "",
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        }
        res = self.db.leave_requests.update_one({"_id": to_objectid(id)}, update)
        return res.matched_count, self.get(id)
