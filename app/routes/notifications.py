from fastapi import APIRouter, Request, Query
from app.core.responses import ok
from app.schemas.response import SuccessResponse
from app.utils.pagination import normalize_pagination
from app.services.notifications_service import NotificationsService

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])
svc = NotificationsService()

@router.get("", response_model=SuccessResponse)
def list_notifications(
    request: Request,
    read: bool | None = None,
    page: int | None = Query(default=1),
    page_size: int | None = Query(default=10),
):
    q: dict = {}
    if read is not None:
        q["read"] = read
    page, page_size, skip = normalize_pagination(page, page_size)
    items, total = svc.list(request, q, skip, page_size)
    return ok({"items": items, "page": page, "page_size": page_size, "total": total}, request.state.request_id)

@router.put("/{id}/read", response_model=SuccessResponse)
def mark_read(request: Request, id: str):
    svc.mark_read(request, id)
    return ok({"read": True}, request.state.request_id)

@router.put("/read-all", response_model=SuccessResponse)
def mark_all_read(request: Request):
    count = svc.mark_all_read(request)
    return ok({"updated": count}, request.state.request_id)
