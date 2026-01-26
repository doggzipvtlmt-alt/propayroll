from fastapi import APIRouter, Request, Query
from app.core.permissions import require_permission
from app.core.responses import ok
from app.schemas.response import SuccessResponse
from app.schemas.users import UserCreate, UserUpdate, UserStatusUpdate
from app.utils.pagination import normalize_pagination
from app.services.users_service import UsersService

router = APIRouter(prefix="/api/users", tags=["Users"])
svc = UsersService()

@router.get("", response_model=SuccessResponse)
def list_users(
    request: Request,
    role_key: str | None = None,
    status: str | None = None,
    page: int | None = Query(default=1),
    page_size: int | None = Query(default=10),
):
    require_permission(request, "admin:read")
    q: dict = {}
    if role_key:
        q["role_key"] = role_key
    if status:
        q["status"] = status
    page, page_size, skip = normalize_pagination(page, page_size)
    items, total = svc.list(request, q, skip, page_size)
    return ok({"items": items, "page": page, "page_size": page_size, "total": total}, request.state.request_id)

@router.post("", response_model=SuccessResponse)
def create_user(request: Request, payload: UserCreate):
    require_permission(request, "admin:write")
    doc = svc.create(request, payload.model_dump())
    return ok(doc, request.state.request_id)

@router.put("/{id}", response_model=SuccessResponse)
def update_user(request: Request, id: str, payload: UserUpdate):
    require_permission(request, "admin:write")
    doc = svc.update(request, id, payload.model_dump(exclude_unset=True))
    return ok(doc, request.state.request_id)

@router.patch("/{id}/status", response_model=SuccessResponse)
def update_user_status(request: Request, id: str, payload: UserStatusUpdate):
    require_permission(request, "admin:write")
    doc = svc.set_status(request, id, payload.status)
    return ok(doc, request.state.request_id)
