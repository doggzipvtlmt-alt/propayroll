from fastapi import APIRouter, Request, Query
from app.core.responses import ok
from app.schemas.companies import CompanyCreate, CompanyUpdate
from app.schemas.response import SuccessResponse
from app.utils.pagination import normalize_pagination
from app.services.companies_service import CompaniesService

router = APIRouter(prefix="/api/companies", tags=["Companies"])
svc = CompaniesService()

@router.post("", response_model=SuccessResponse)
def create_company(request: Request, payload: CompanyCreate):
    doc = svc.create(request, payload.model_dump())
    return ok(doc, request.state.request_id)

@router.get("", response_model=SuccessResponse)
def list_companies(
    request: Request,
    page: int | None = Query(default=1),
    page_size: int | None = Query(default=10),
):
    page, page_size, skip = normalize_pagination(page, page_size)
    items, total = svc.list(request, {}, skip, page_size)
    return ok({"items": items, "page": page, "page_size": page_size, "total": total}, request.state.request_id)

@router.get("/{id}", response_model=SuccessResponse)
def get_company(request: Request, id: str):
    doc = svc.get(request, id)
    return ok(doc, request.state.request_id)

@router.put("/{id}", response_model=SuccessResponse)
def update_company(request: Request, id: str, payload: CompanyUpdate):
    doc = svc.update(request, id, payload.model_dump())
    return ok(doc, request.state.request_id)
