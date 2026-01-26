from fastapi import APIRouter, Request, Query
from app.core.errors import Forbidden
from app.core.responses import ok
from app.schemas.response import SuccessResponse
from app.utils.pagination import normalize_pagination
from app.services.audit_service import AuditService

router = APIRouter(prefix="/api/audit", tags=["Audit"])
svc = AuditService()

@router.get("", response_model=SuccessResponse)
def list_audit_logs(
    request: Request,
    entity_type: str | None = None,
    entity_id: str | None = None,
    limit: int | None = Query(default=20),
    page: int | None = Query(default=1),
):
    role = getattr(request.state, "role", "EMPLOYEE")
    if role not in {"MD", "ADMIN"}:
        raise Forbidden("You do not have permission to view audit logs")
    page, page_size, skip = normalize_pagination(page, limit)
    q: dict = {}
    if entity_type:
        q["entity_type"] = entity_type
    if entity_id:
        q["entity_id"] = entity_id
    items, total = svc.list(request, q, skip, page_size)
    return ok({"items": items, "page": page, "page_size": page_size, "total": total}, request.state.request_id)
