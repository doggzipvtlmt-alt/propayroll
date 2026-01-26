from datetime import datetime, timezone
from app.core.db import require_db
from app.utils.oid import to_objectid, with_id

class CompaniesRepo:
    def __init__(self):
        self.db = require_db()

    def list(self, query: dict, skip: int, limit: int):
        cursor = self.db.companies.find(query).sort([("created_at", -1)]).skip(skip).limit(limit)
        return [with_id(d) for d in cursor]

    def count(self, query: dict) -> int:
        return self.db.companies.count_documents(query)

    def get(self, id: str):
        doc = self.db.companies.find_one({"_id": to_objectid(id)})
        return with_id(doc) if doc else None

    def create(self, data: dict):
        now = datetime.now(timezone.utc).isoformat()
        data["created_at"] = now
        data["updated_at"] = now
        res = self.db.companies.insert_one(data)
        return self.get(str(res.inserted_id))

    def update(self, id: str, data: dict):
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        res = self.db.companies.update_one({"_id": to_objectid(id)}, {"$set": data})
        return res.matched_count, self.get(id)
