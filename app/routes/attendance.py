from fastapi import APIRouter, Request, Query
from app.schemas.attendance import AttendanceCreate
from app.utils.pagination import normalize_pagination
from app.core.responses import ok
from app.services.attendance_service import AttendanceService

router = APIRouter(prefix="/api/attendance", tags=["Attendance"])
svc = AttendanceService()

@router.get("")
def list_attendance(
    request: Request,
    date: str | None = None,
    department: str | None = None,
    page: int | None = Query(default=1),
    page_size: int | None = Query(default=10),
):
    q = {}
    if date:
        q["date"] = date
    if department:
        q["department"] = department

    page, page_size, skip = normalize_pagination(page, page_size)
    items, total = svc.list(request, q, skip, page_size)
    return ok({"items": items, "page": page, "page_size": page_size, "total": total}, request.state.request_id)

@router.post("")
def upsert_attendance(request: Request, payload: AttendanceCreate):
    doc = svc.upsert(request, payload.model_dump())
    return ok(doc, request.state.request_id)
