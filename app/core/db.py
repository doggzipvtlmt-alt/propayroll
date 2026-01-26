from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ServerSelectionTimeoutError
from app.core.config import settings
from app.core.errors import DatabaseDown

_client = None
db = None

def connect():
    global _client, db
    settings.validate()

    _client = MongoClient(
        settings.MONGO_URI,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=settings.REQUEST_TIMEOUT_MS,
    )
    db = _client[settings.MONGO_DB]
    return db

def ping() -> bool:
    if _client is None:
        return False
    try:
        _client.admin.command("ping")
        return True
    except Exception:
        return False

def ensure_indexes():
    if db is None:
        raise DatabaseDown("Database not connected")
    # employees unique employee_code
    db.employees.create_index([("company_id", ASCENDING), ("employee_code", ASCENDING)], unique=True)
    db.employees.create_index([("department", ASCENDING)])
    db.employees.create_index([("designation", ASCENDING)])
    db.employees.create_index([("status", ASCENDING)])
    db.employees.create_index([("company_id", ASCENDING)])

    # leaves filters
    db.leave_requests.create_index([("status", ASCENDING)])
    db.leave_requests.create_index([("leave_type", ASCENDING)])
    db.leave_requests.create_index([("employee_id", ASCENDING)])
    db.leave_requests.create_index([("start_date", ASCENDING)])
    db.leave_requests.create_index([("company_id", ASCENDING)])

    # attendance unique per employee per date
    db.attendance.create_index([("company_id", ASCENDING), ("date", ASCENDING), ("employee_id", ASCENDING)], unique=True)
    db.attendance.create_index([("department", ASCENDING)])
    db.attendance.create_index([("company_id", ASCENDING)])

    # companies
    db.companies.create_index([("name", ASCENDING)], unique=True)

    # users
    db.users.create_index([("company_id", ASCENDING), ("email", ASCENDING)], unique=True)

    # roles
    db.roles.create_index([("company_id", ASCENDING), ("key", ASCENDING)], unique=True)

    # sessions
    db.sessions.create_index([("token_hash", ASCENDING)], unique=True)
    db.sessions.create_index([("expires_at", ASCENDING)])

    # approvals
    db.approvals.create_index([("company_id", ASCENDING)])
    db.approvals.create_index([("company_id", ASCENDING), ("entity_type", ASCENDING), ("entity_id", ASCENDING)], unique=True)

    # notifications
    db.notifications.create_index([("company_id", ASCENDING), ("user_id", ASCENDING), ("read", ASCENDING)])

    # vault
    db.vault_items.create_index([("company_id", ASCENDING), ("owner_user_id", ASCENDING)])

    # audit logs
    db.audit_logs.create_index([("company_id", ASCENDING)])
    db.audit_logs.create_index([("ts", DESCENDING)])
    db.audit_logs.create_index([("entity_type", ASCENDING)])
    db.audit_logs.create_index([("entity_id", ASCENDING)])

def require_db():
    if db is None:
        raise DatabaseDown("Database not connected")
    return db
