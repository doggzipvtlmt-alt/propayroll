from typing import Any, Dict
from bson import ObjectId

def oid_str(doc: Dict[str, Any]) -> Dict[str, Any]:
    if not doc:
        return doc
    doc["id"] = str(doc.pop("_id"))
    return doc

def parse_objectid(id: str) -> ObjectId:
    return ObjectId(id)
