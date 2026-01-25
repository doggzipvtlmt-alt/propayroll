from pymongo import MongoClient
from app.core.config import MONGO_URI, MONGO_DB

_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = _client[MONGO_DB]

# Fail fast if connection is broken
_client.admin.command("ping")
