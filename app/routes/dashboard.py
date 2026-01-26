from fastapi import APIRouter, Request
from app.core.responses import ok
from app.schemas.response import SuccessResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])
svc = DashboardService()

@router.get("/summary", response_model=SuccessResponse)
def summary(request: Request):
    return ok(svc.summary(request), request.state.request_id)
