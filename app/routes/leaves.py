from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.core.db import db
from app.models.common import oid_str, parse_objectid

router = APIRouter(prefix="/api/leaves", tags=["Leaves"])

class LeaveIn(BaseModel):
    employee_id: str
    employee_name: Optional[str] = None
    leave_type: str
    start_date: str
    end_date: str
    reason: Optional[str] = None
    status: str = "pending"
    approver_comment: Optional[str] = None

@router.get("", response_model=List[dict])
def list_leaves(status: Optional[str] = None):
    q = {}
    if status:
        q["status"] = status
    docs = list(db.leave_requests.find(q).sort("start_date", -1))
    return [oid_str(d) for d in docs]

@router.post("", response_model=dict)
def apply_leave(payload: LeaveIn):
    res = db.leave_requests.insert_one(payload.model_dump())
    doc = db.leave_requests.find_one({"_id": res.inserted_id})
    return oid_str(doc)

@router.put("/{id}/approve", response_model=dict)
def approve_leave(id: str, comment: Optional[str] = None):
    res = db.leave_requests.update_one(
        {"_id": parse_objectid(id)},
        {"": {"status": "approved", "approver_comment": comment or ""}}
    )
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Leave request not found")
    doc = db.leave_requests.find_one({"_id": parse_objectid(id)})
    return oid_str(doc)

@router.put("/{id}/reject", response_model=dict)
def reject_leave(id: str, comment: Optional[str] = None):
    res = db.leave_requests.update_one(
        {"_id": parse_objectid(id)},
        {"": {"status": "rejected", "approver_comment": comment or ""}}
    )
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Leave request not found")
    doc = db.leave_requests.find_one({"_id": parse_objectid(id)})
    return oid_str(doc)
