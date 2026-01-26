from app.core.db import require_db
from app.utils.oid import with_id

class AuditRepo:
    def __init__(self):
        self.db = require_db()

    def list(self, query: dict, skip: int, limit: int):
        cursor = self.db.audit_logs.find(query).sort([("ts", -1)]).skip(skip).limit(limit)
        return [with_id(d) for d in cursor]

    def count(self, query: dict) -> int:
        return self.db.audit_logs.count_documents(query)
