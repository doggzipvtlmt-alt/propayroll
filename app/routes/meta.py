from fastapi import APIRouter, Request
from app.core.responses import ok
from app.core.db import require_db
from app.core.security import require_company_id, require_user_id
from app.schemas.response import SuccessResponse

router = APIRouter(prefix="/api/meta", tags=["Meta"])

@router.get("/departments", response_model=SuccessResponse)
def departments(request: Request):
    db = require_db()
    company_id = require_company_id(request)
    require_user_id(request)
    values = db.employees.distinct("department", {"company_id": company_id})
    values = [v for v in values if v]
    values.sort()
    return ok(values, request.state.request_id)

@router.get("/designations", response_model=SuccessResponse)
def designations(request: Request):
    db = require_db()
    company_id = require_company_id(request)
    require_user_id(request)
    values = db.employees.distinct("designation", {"company_id": company_id})
    values = [v for v in values if v]
    values.sort()
    return ok(values, request.state.request_id)

@router.get("/leave-types", response_model=SuccessResponse)
def leave_types(request: Request):
    require_user_id(request)
    values = ["CL", "SL", "PL", "LOP", "WFH"]
    return ok(values, request.state.request_id)
