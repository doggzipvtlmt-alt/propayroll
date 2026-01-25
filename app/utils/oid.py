from bson import ObjectId
from app.core.errors import InvalidId

def to_objectid(id: str) -> ObjectId:
    try:
        return ObjectId(id)
    except Exception:
        raise InvalidId("Invalid id format")

def with_id(doc: dict) -> dict:
    if not doc:
        return doc
    doc["id"] = str(doc.pop("_id"))
    return doc
