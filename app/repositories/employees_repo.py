from datetime import datetime, timezone
from typing import List, Tuple
from app.core.db import require_db
from app.utils.oid import to_objectid, with_id

class EmployeesRepo:
    def __init__(self):
        self.db = require_db()

    def list(self, query: dict, skip: int, limit: int, sort: List[Tuple]):
        cursor = self.db.employees.find(query).sort(sort).skip(skip).limit(limit)
        return [with_id(d) for d in cursor]

    def count(self, query: dict) -> int:
        return self.db.employees.count_documents(query)

    def get(self, id: str, company_id: str):
        doc = self.db.employees.find_one({"_id": to_objectid(id), "company_id": company_id})
        return with_id(doc) if doc else None

    def find_by_code(self, company_id: str, employee_code: str):
        doc = self.db.employees.find_one({"company_id": company_id, "employee_code": employee_code})
        return with_id(doc) if doc else None

    def create(self, data: dict):
        now = datetime.now(timezone.utc).isoformat()
        data["created_at"] = now
        data["updated_at"] = now
        res = self.db.employees.insert_one(data)
        return self.get(str(res.inserted_id), data["company_id"])

    def update(self, id: str, company_id: str, data: dict):
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        res = self.db.employees.update_one({"_id": to_objectid(id), "company_id": company_id}, {"$set": data})
        return res.matched_count, self.get(id, company_id)

    def delete(self, id: str, company_id: str):
        res = self.db.employees.delete_one({"_id": to_objectid(id), "company_id": company_id})
        return res.deleted_count
