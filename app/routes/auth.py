from fastapi import APIRouter, Request
from app.core.errors import Unauthorized
from app.core.logging import get_logger
from app.core.responses import ok
from app.core.security import get_bearer_token, require_company_id, require_user_id
from app.schemas.auth import LoginRequest
from app.schemas.response import SuccessResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["Auth"])
svc = AuthService()
logger = get_logger("auth")


@router.post("/login", response_model=SuccessResponse)
def login(request: Request, payload: LoginRequest):
    user_agent = request.headers.get("User-Agent")
    ip = request.client.host if request.client else None
    user, reason = svc.validate_login(payload.email, payload.password)
    if reason == "user_not_found":
        logger.info("Login failed: user not found email=%s", payload.email)
        raise Unauthorized("Invalid credentials")
    if reason == "bad_password":
        logger.info("Login failed: bad password email=%s", payload.email)
        raise Unauthorized("Invalid credentials")
    if reason == "inactive":
        raise Unauthorized("User is inactive")
    if reason:
        raise Unauthorized("Invalid credentials")
    data = svc.login_with_user(user, user_agent, ip)
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
