from fastapi import APIRouter, Request, Query
from app.core.permissions import require_permission
from app.core.responses import ok
from app.schemas.response import SuccessResponse
from app.schemas.roles import RoleCreate, RoleUpdate
from app.utils.pagination import normalize_pagination
from app.services.roles_service import RolesService

router = APIRouter(prefix="/api/roles", tags=["Roles"])
svc = RolesService()

@router.get("", response_model=SuccessResponse)
def list_roles(
    request: Request,
    page: int | None = Query(default=1),
    page_size: int | None = Query(default=10),
):
    require_permission(request, "admin:read")
    page, page_size, skip = normalize_pagination(page, page_size)
    items, total = svc.list(request, {}, skip, page_size)
    return ok({"items": items, "page": page, "page_size": page_size, "total": total}, request.state.request_id)

@router.post("", response_model=SuccessResponse)
def create_role(request: Request, payload: RoleCreate):
    require_permission(request, "admin:write")
    doc = svc.create(request, payload.model_dump())
    return ok(doc, request.state.request_id)

@router.put("/{id}", response_model=SuccessResponse)
def update_role(request: Request, id: str, payload: RoleUpdate):
    require_permission(request, "admin:write")
    doc = svc.update(request, id, payload.model_dump())
    return ok(doc, request.state.request_id)

@router.delete("/{id}", response_model=SuccessResponse)
def delete_role(request: Request, id: str):
    require_permission(request, "admin:write")
    svc.delete(request, id)
    return ok({"deleted": True}, request.state.request_id)
