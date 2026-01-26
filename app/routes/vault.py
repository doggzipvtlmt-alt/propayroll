from fastapi import APIRouter, Request, Query
from app.core.permissions import require_permission
from app.core.responses import ok
from app.schemas.response import SuccessResponse
from app.schemas.vault import VaultCreate, VaultUpdate, VaultResetSecret
from app.utils.pagination import normalize_pagination
from app.services.vault_service import VaultService

router = APIRouter(prefix="/api/vault", tags=["Vault"])
svc = VaultService()

@router.get("", response_model=SuccessResponse)
def list_vault_items(
    request: Request,
    page: int | None = Query(default=1),
    page_size: int | None = Query(default=10),
):
    require_permission(request, "vault:read")
    page, page_size, skip = normalize_pagination(page, page_size)
    items, total = svc.list(request, {}, skip, page_size)
    return ok({"items": items, "page": page, "page_size": page_size, "total": total}, request.state.request_id)

@router.post("", response_model=SuccessResponse)
def create_vault_item(request: Request, payload: VaultCreate):
    require_permission(request, "vault:write")
    doc = svc.create(request, payload.model_dump())
    return ok(doc, request.state.request_id)

@router.get("/{id}", response_model=SuccessResponse)
def get_vault_item(request: Request, id: str):
    require_permission(request, "vault:read")
    doc = svc.get(request, id)
    return ok(doc, request.state.request_id)

@router.put("/{id}", response_model=SuccessResponse)
def update_vault_item(request: Request, id: str, payload: VaultUpdate):
    require_permission(request, "vault:write")
    doc = svc.update(request, id, payload.model_dump(exclude_unset=True))
    return ok(doc, request.state.request_id)

@router.put("/{id}/reset-secret", response_model=SuccessResponse)
def reset_vault_secret(request: Request, id: str, payload: VaultResetSecret):
    require_permission(request, "vault:write")
    doc = svc.reset_secret(request, id, payload.password, payload.notes)
    return ok(doc, request.state.request_id)

@router.delete("/{id}", response_model=SuccessResponse)
def delete_vault_item(request: Request, id: str):
    require_permission(request, "vault:write")
    svc.delete(request, id)
    return ok({"deleted": True}, request.state.request_id)
