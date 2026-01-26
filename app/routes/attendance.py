from fastapi import APIRouter, Request, Query
from app.schemas.attendance import AttendanceCreate
from app.utils.pagination import normalize_pagination
from app.core.responses import ok
from app.core.permissions import require_permission
from app.schemas.response import SuccessResponse
from app.services.attendance_service import AttendanceService

router = APIRouter(prefix="/api/attendance", tags=["Attendance"])
svc = AttendanceService()

@router.get("", response_model=SuccessResponse)
def list_attendance(
    request: Request,
    date: str | None = None,
    department: str | None = None,
    page: int | None = Query(default=1),
    page_size: int | None = Query(default=10),
):
    require_permission(request, "attendance:read")
    q = {}
    if date:
        q["date"] = date
    if department:
        q["department"] = department

    page, page_size, skip = normalize_pagination(page, page_size)
    items, total = svc.list(request, q, skip, page_size)
    return ok({"items": items, "page": page, "page_size": page_size, "total": total}, request.state.request_id)

@router.post("", response_model=SuccessResponse)
def upsert_attendance(request: Request, payload: AttendanceCreate):
    require_permission(request, "attendance:write")
    doc = svc.upsert(request, payload.model_dump())
    return ok(doc, request.state.request_id)
