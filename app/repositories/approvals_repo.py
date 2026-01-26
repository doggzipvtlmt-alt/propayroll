from datetime import datetime, timezone
from app.core.db import require_db
from app.utils.oid import to_objectid, with_id

class ApprovalsRepo:
    def __init__(self):
        self.db = require_db()

    def list(self, query: dict, skip: int, limit: int):
        cursor = self.db.approvals.find(query).sort([("created_at", -1)]).skip(skip).limit(limit)
        return [with_id(d) for d in cursor]

    def count(self, query: dict) -> int:
        return self.db.approvals.count_documents(query)

    def get(self, id: str, company_id: str):
        doc = self.db.approvals.find_one({"_id": to_objectid(id), "company_id": company_id})
        return with_id(doc) if doc else None

    def get_by_entity(self, company_id: str, entity_type: str, entity_id: str):
        doc = self.db.approvals.find_one({"company_id": company_id, "entity_type": entity_type, "entity_id": entity_id})
        return with_id(doc) if doc else None

    def create(self, data: dict):
        now = datetime.now(timezone.utc).isoformat()
        data["created_at"] = now
        data["updated_at"] = now
        res = self.db.approvals.insert_one(data)
        return self.get(str(res.inserted_id), data["company_id"])

    def set_status(self, id: str, company_id: str, status: str, decided_by_user_id: str | None, comment: str | None = None):
        data = {
            "status": status,
            "decided_by_user_id": decided_by_user_id,
            "decision_comment": comment or "",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        res = self.db.approvals.update_one({"_id": to_objectid(id), "company_id": company_id}, {"$set": data})
        return res.matched_count, self.get(id, company_id)

    def set_status_by_entity(self, company_id: str, entity_type: str, entity_id: str, status: str, decided_by_user_id: str | None, comment: str | None = None):
        data = {
            "status": status,
            "decided_by_user_id": decided_by_user_id,
            "decision_comment": comment or "",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        res = self.db.approvals.update_one(
            {"company_id": company_id, "entity_type": entity_type, "entity_id": entity_id},
            {"$set": data},
        )
        return res.matched_count
