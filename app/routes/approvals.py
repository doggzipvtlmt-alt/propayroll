from fastapi import APIRouter, Request, Query
from app.core.permissions import require_permission, require_role
from app.core.responses import ok
from app.schemas.response import SuccessResponse
from app.schemas.approvals import ApprovalCreate, ApprovalDecision
from app.utils.pagination import normalize_pagination
from app.services.approvals_service import ApprovalsService
from app.repositories.approvals_repo import ApprovalsRepo
from app.core.security import require_company_id

router = APIRouter(prefix="/api/approvals", tags=["Approvals"])
svc = ApprovalsService()

@router.get("", response_model=SuccessResponse)
def list_approvals(
    request: Request,
    status: str | None = None,
    entity_type: str | None = None,
    page: int | None = Query(default=1),
    page_size: int | None = Query(default=10),
):
    require_permission(request, "admin:read")
    q: dict = {}
    if status:
        q["status"] = status
    if entity_type:
        q["entity_type"] = entity_type
    page, page_size, skip = normalize_pagination(page, page_size)
    items, total = svc.list(request, q, skip, page_size)
    return ok({"items": items, "page": page, "page_size": page_size, "total": total}, request.state.request_id)

@router.post("", response_model=SuccessResponse)
def create_approval(request: Request, payload: ApprovalCreate):
    require_permission(request, "admin:write")
    doc = svc.create(request, payload.model_dump())
    return ok(doc, request.state.request_id)

@router.put("/{id}/approve", response_model=SuccessResponse)
def approve_approval(request: Request, id: str, payload: ApprovalDecision):
    company_id = require_company_id(request)
    approval = ApprovalsRepo().get(id, company_id)
    if approval and approval.get("entity_type") == "user_signup":
        require_role(request, "SUPERUSER")
    elif approval and approval.get("entity_type") == "leave":
        require_permission(request, "leaves:approve")
    else:
        require_permission(request, "admin:write")
    doc = svc.approve(request, id, payload.comment)
    return ok(doc, request.state.request_id)

@router.put("/{id}/reject", response_model=SuccessResponse)
def reject_approval(request: Request, id: str, payload: ApprovalDecision):
    company_id = require_company_id(request)
    approval = ApprovalsRepo().get(id, company_id)
    if approval and approval.get("entity_type") == "user_signup":
        require_role(request, "SUPERUSER")
    elif approval and approval.get("entity_type") == "leave":
        require_permission(request, "leaves:approve")
    else:
        require_permission(request, "admin:write")
    doc = svc.reject(request, id, payload.comment)
    return ok(doc, request.state.request_id)
