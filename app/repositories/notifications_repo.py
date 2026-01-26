from datetime import datetime, timezone
from typing import List
from app.core.db import require_db
from app.utils.oid import to_objectid, with_id

class NotificationsRepo:
    def __init__(self):
        self.db = require_db()

    def list(self, query: dict, skip: int, limit: int):
        cursor = self.db.notifications.find(query).sort([("created_at", -1)]).skip(skip).limit(limit)
        return [with_id(d) for d in cursor]

    def count(self, query: dict) -> int:
        return self.db.notifications.count_documents(query)

    def create_many(self, items: List[dict]) -> int:
        if not items:
            return 0
        now = datetime.now(timezone.utc).isoformat()
        for item in items:
            item.setdefault("created_at", now)
            item.setdefault("read", False)
        res = self.db.notifications.insert_many(items)
        return len(res.inserted_ids)

    def create_one(self, data: dict):
        now = datetime.now(timezone.utc).isoformat()
        data.setdefault("created_at", now)
        data.setdefault("read", False)
        res = self.db.notifications.insert_one(data)
        doc = self.db.notifications.find_one({"_id": res.inserted_id})
        return with_id(doc) if doc else None

    def mark_read(self, id: str, company_id: str, user_id: str):
        res = self.db.notifications.update_one(
            {"_id": to_objectid(id), "company_id": company_id, "user_id": user_id},
            {"$set": {"read": True}},
        )
        return res.matched_count

    def mark_all_read(self, company_id: str, user_id: str):
        res = self.db.notifications.update_many(
            {"company_id": company_id, "user_id": user_id, "read": False},
            {"$set": {"read": True}},
        )
        return res.modified_count
