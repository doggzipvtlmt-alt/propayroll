from datetime import datetime, timezone
from app.core.db import require_db
from app.utils.oid import with_id


class SessionsRepo:
    def __init__(self):
        self.db = require_db()

    def get_by_token_hash(self, token_hash: str):
        doc = self.db.sessions.find_one({"token_hash": token_hash})
        return with_id(doc) if doc else None

    def create(self, data: dict):
        now = datetime.now(timezone.utc)
        data["created_at"] = now
        data["last_seen_at"] = now
        res = self.db.sessions.insert_one(data)
        return self.get_by_token_hash(data["token_hash"])

    def delete_by_token_hash(self, token_hash: str) -> int:
        res = self.db.sessions.delete_one({"token_hash": token_hash})
        return res.deleted_count

    def touch(self, token_hash: str, user_agent: str | None, ip: str | None):
        update = {"last_seen_at": datetime.now(timezone.utc)}
        if user_agent:
            update["user_agent"] = user_agent
        if ip:
            update["ip"] = ip
        self.db.sessions.update_one({"token_hash": token_hash}, {"$set": update})
