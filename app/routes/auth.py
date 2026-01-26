from fastapi import APIRouter, Request
from app.core.responses import ok
from app.core.security import get_bearer_token, require_company_id, require_user_id
from app.schemas.auth import LoginRequest
from app.schemas.response import SuccessResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["Auth"])
svc = AuthService()


@router.post("/login", response_model=SuccessResponse)
def login(request: Request, payload: LoginRequest):
    user_agent = request.headers.get("User-Agent")
    ip = request.client.host if request.client else None
    data = svc.login(payload.company_id, payload.identifier, payload.dob_or_pin, user_agent, ip)
    return ok(data, request.state.request_id)


@router.post("/logout", response_model=SuccessResponse)
def logout(request: Request):
    token = get_bearer_token(request)
    svc.logout(token)
    return ok({"logged_out": True}, request.state.request_id)


@router.get("/me", response_model=SuccessResponse)
def me(request: Request):
    company_id = require_company_id(request)
    user_id = require_user_id(request)
    data = svc.me(company_id, user_id)
    return ok(data, request.state.request_id)
