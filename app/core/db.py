from pymongo import MongoClient, ASCENDING
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
    try:
        _client.admin.command("ping")
        return True
    except Exception:
        return False

def ensure_indexes():
    # employees unique employee_code
    db.employees.create_index([("employee_code", ASCENDING)], unique=True)
    db.employees.create_index([("department", ASCENDING)])
    db.employees.create_index([("designation", ASCENDING)])
    db.employees.create_index([("status", ASCENDING)])

    # leaves filters
    db.leave_requests.create_index([("status", ASCENDING)])
    db.leave_requests.create_index([("leave_type", ASCENDING)])
    db.leave_requests.create_index([("employee_id", ASCENDING)])
    db.leave_requests.create_index([("start_date", ASCENDING)])

    # attendance unique per employee per date
    db.attendance.create_index([("date", ASCENDING), ("employee_id", ASCENDING)], unique=True)
    db.attendance.create_index([("department", ASCENDING)])

def require_db():
    if db is None:
        raise DatabaseDown("Database not connected")
    return db
