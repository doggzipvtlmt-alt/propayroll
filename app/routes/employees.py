from fastapi import APIRouter, Request, Query
from app.schemas.employees import EmployeeCreate, EmployeeUpdate
from app.schemas.response import SuccessResponse
from app.utils.pagination import normalize_pagination
from app.core.responses import ok
from app.core.permissions import require_permission
from app.services.employees_service import EmployeesService

router = APIRouter(prefix="/api/employees", tags=["Employees"])
svc = EmployeesService()

@router.get("", response_model=SuccessResponse)
def list_employees(
    request: Request,
    search: str | None = None,
    department: str | None = None,
    designation: str | None = None,
    status: str | None = None,
    page: int | None = Query(default=1),
    page_size: int | None = Query(default=10),
    sort_by: str | None = Query(default="full_name"),
    sort_dir: str | None = Query(default="asc"),
):
    require_permission(request, "employees:read")
    q = {}
    if search:
        q["full_name"] = {"$regex": search, "$options": "i"}
    if department:
        q["department"] = department
    if designation:
        q["designation"] = designation
    if status:
        q["status"] = status

    page, page_size, skip = normalize_pagination(page, page_size)
    sort = [(sort_by, 1 if sort_dir.lower() == "asc" else -1)]

    items, total = svc.list(request, q, skip, page_size, sort)
    return ok({"items": items, "page": page, "page_size": page_size, "total": total}, request.state.request_id)

@router.get("/{id}", response_model=SuccessResponse)
def get_employee(request: Request, id: str):
    require_permission(request, "employees:read")
    doc = svc.get(request, id)
    return ok(doc, request.state.request_id)

@router.post("", response_model=SuccessResponse)
def create_employee(request: Request, payload: EmployeeCreate):
    require_permission(request, "employees:write")
    doc = svc.create(request, payload.model_dump())
    return ok(doc, request.state.request_id)

@router.put("/{id}", response_model=SuccessResponse)
def update_employee(request: Request, id: str, payload: EmployeeUpdate):
    require_permission(request, "employees:write")
    doc = svc.update(request, id, payload.model_dump())
    return ok(doc, request.state.request_id)

@router.delete("/{id}", response_model=SuccessResponse)
def delete_employee(request: Request, id: str):
    require_permission(request, "employees:write")
    svc.delete(request, id)
    return ok({"deleted": True}, request.state.request_id)
