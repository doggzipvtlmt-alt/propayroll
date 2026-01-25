from pydantic import BaseModel
from typing import Any, Optional, Dict

class ErrorBody(BaseModel):
    code: str
    message: str
    details: Dict[str, Any] = {}
    request_id: str

class SuccessResponse(BaseModel):
    ok: bool = True
    data: Any
    request_id: str

class ErrorResponse(BaseModel):
    ok: bool = False
    error: ErrorBody
