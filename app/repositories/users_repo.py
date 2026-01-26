from datetime import datetime, timezone
import re
from app.core.db import require_db
from app.utils.oid import to_objectid, with_id

class UsersRepo:
    def __init__(self):
        self.db = require_db()

    def list(self, query: dict, skip: int, limit: int):
        cursor = self.db.users.find(query).sort([("full_name", 1)]).skip(skip).limit(limit)
        return [with_id(d) for d in cursor]

    def count(self, query: dict) -> int:
        return self.db.users.count_documents(query)

    def get(self, id: str, company_id: str):
        doc = self.db.users.find_one({"_id": to_objectid(id), "company_id": company_id})
        return with_id(doc) if doc else None

    def find_by_email(self, company_id: str, email: str):
        doc = self.db.users.find_one({"company_id": company_id, "email": email})
        return with_id(doc) if doc else None

    def find_by_email_case_insensitive(self, email: str):
        regex = f"^{re.escape(email)}$"
        doc = self.db.users.find_one({"email": {"$regex": regex, "$options": "i"}})
        return with_id(doc) if doc else None

    def create(self, data: dict):
        now = datetime.now(timezone.utc).isoformat()
        data["created_at"] = now
        data["updated_at"] = now
        res = self.db.users.insert_one(data)
        return self.get(str(res.inserted_id), data["company_id"])

    def update(self, id: str, company_id: str, data: dict):
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        res = self.db.users.update_one({"_id": to_objectid(id), "company_id": company_id}, {"$set": data})
        return res.matched_count, self.get(id, company_id)

    def set_status(self, id: str, company_id: str, status: str):
        data = {"status": status, "updated_at": datetime.now(timezone.utc).isoformat()}
        res = self.db.users.update_one({"_id": to_objectid(id), "company_id": company_id}, {"$set": data})
        return res.matched_count, self.get(id, company_id)
