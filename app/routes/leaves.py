from fastapi import APIRouter, Request, Query
from app.core.permissions import require_permission
from app.core.responses import ok
from app.schemas.leaves import LeaveCreate, LeaveDecision
from app.schemas.response import SuccessResponse
from app.utils.pagination import normalize_pagination
from app.services.leaves_service import LeavesService

router = APIRouter(prefix="/api/leaves", tags=["Leaves"])
svc = LeavesService()

@router.get("", response_model=SuccessResponse)
def list_leaves(
    request: Request,
    status: str | None = None,
    employee_id: str | None = None,
    page: int | None = Query(default=1),
    page_size: int | None = Query(default=10),
):
    require_permission(request, "leaves:read")
    q: dict = {}
    if status:
        q["status"] = status
    if employee_id:
        q["employee_id"] = employee_id
    page, page_size, skip = normalize_pagination(page, page_size)
    items, total = svc.list(request, q, skip, page_size, [("start_date", -1)])
    return ok({"items": items, "page": page, "page_size": page_size, "total": total}, request.state.request_id)

@router.post("", response_model=SuccessResponse)
def apply_leave(request: Request, payload: LeaveCreate):
    require_permission(request, "leaves:write")
    doc = svc.create(request, payload.model_dump())
    return ok(doc, request.state.request_id)

@router.put("/{id}/approve", response_model=SuccessResponse)
def approve_leave(request: Request, id: str, payload: LeaveDecision | None = None, comment: str | None = None):
    require_permission(request, "leaves:approve")
    final_comment = payload.comment if payload else comment
    doc = svc.approve(request, id, final_comment)
    return ok(doc, request.state.request_id)

@router.put("/{id}/reject", response_model=SuccessResponse)
def reject_leave(request: Request, id: str, payload: LeaveDecision | None = None, comment: str | None = None):
    require_permission(request, "leaves:approve")
    final_comment = payload.comment if payload else comment
    doc = svc.reject(request, id, final_comment)
    return ok(doc, request.state.request_id)
