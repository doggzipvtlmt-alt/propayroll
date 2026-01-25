from fastapi import APIRouter, Request
from app.core.responses import ok
from app.core.db import require_db

router = APIRouter(prefix="/api/meta", tags=["Meta"])

@router.get("/departments")
def departments(request: Request):
    db = require_db()
    values = db.employees.distinct("department")
    values = [v for v in values if v]
    values.sort()
    return ok(values, request.state.request_id)

@router.get("/designations")
def designations(request: Request):
    db = require_db()
    values = db.employees.distinct("designation")
    values = [v for v in values if v]
    values.sort()
    return ok(values, request.state.request_id)

@router.get("/leave-types")
def leave_types(request: Request):
    values = ["CL", "SL", "PL", "LOP", "WFH"]
    return ok(values, request.state.request_id)
