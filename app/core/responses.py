from typing import Any, Optional, Dict

def ok(data: Any = None, request_id: str = "-") -> Dict[str, Any]:
    return {"ok": True, "data": data, "request_id": request_id}

def err(code: str, message: str, request_id: str = "-", details: Optional[dict] = None) -> Dict[str, Any]:
    return {"ok": False, "error": {"code": code, "message": message, "details": details or {}, "request_id": request_id}}
