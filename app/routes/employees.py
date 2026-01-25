from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from app.core.db import db
from app.models.common import oid_str, parse_objectid

router = APIRouter(prefix="/api/employees", tags=["Employees"])

class EmployeeIn(BaseModel):
    employee_code: str
    full_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    manager_name: Optional[str] = None
    join_date: Optional[str] = None
    status: str = "active"

@router.get("", response_model=List[dict])
def list_employees():
    docs = list(db.employees.find().sort("full_name", 1))
    return [oid_str(d) for d in docs]

@router.get("/{id}", response_model=dict)
def get_employee(id: str):
    doc = db.employees.find_one({"_id": parse_objectid(id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Employee not found")
    return oid_str(doc)

@router.post("", response_model=dict)
def create_employee(payload: EmployeeIn):
    if db.employees.find_one({"employee_code": payload.employee_code}):
        raise HTTPException(status_code=409, detail="employee_code already exists")
    res = db.employees.insert_one(payload.model_dump())
    doc = db.employees.find_one({"_id": res.inserted_id})
    return oid_str(doc)

@router.put("/{id}", response_model=dict)
def update_employee(id: str, payload: EmployeeIn):
    res = db.employees.update_one({"_id": parse_objectid(id)}, {"": payload.model_dump()})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Employee not found")
    doc = db.employees.find_one({"_id": parse_objectid(id)})
    return oid_str(doc)

@router.delete("/{id}", response_model=dict)
def delete_employee(id: str):
    res = db.employees.delete_one({"_id": parse_objectid(id)})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"ok": True}
