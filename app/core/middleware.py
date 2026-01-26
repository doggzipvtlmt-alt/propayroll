import time
import uuid
from datetime import datetime, timezone
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings
from app.core.errors import Unauthorized
from app.core.logging import get_logger, request_id_filter
from app.core.security import get_bearer_token, hash_token, get_role
from app.repositories.sessions_repo import SessionsRepo

logger = get_logger("middleware")

EXEMPT_PATHS = {
    ("GET", "/"),
    ("GET", "/health"),
    ("POST", "/api/auth/login"),
}

class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        request_id_filter.request_id = request_id

        self._apply_auth(request)
        role = getattr(request.state, "role", "EMPLOYEE")
        company_id = getattr(request.state, "company_id", None)
        user_id = getattr(request.state, "user_id", None)

        start = time.time()
        try:
            response = await call_next(request)
        finally:
            duration_ms = int((time.time() - start) * 1000)
            logger.info(
                f"{request.method} {request.url.path} role={role} company_id={company_id} user_id={user_id} status={(getattr(response,'status_code', '-'))} duration_ms={duration_ms}"
            )

        response.headers["X-Request-ID"] = request_id
        return response

    def _apply_auth(self, request: Request) -> None:
        path = request.url.path
        method = request.method.upper()
        if self._is_exempt_path(method, path):
            request.state.company_id = None
            request.state.user_id = None
            request.state.role = "EMPLOYEE"
            return

        token = get_bearer_token(request)
        if token:
            token_hash = hash_token(token)
            repo = SessionsRepo()
            session = repo.get_by_token_hash(token_hash)
            if not session:
                raise Unauthorized("Invalid or expired session")
            expires_at = session.get("expires_at")
            if isinstance(expires_at, datetime):
                if expires_at < datetime.now(timezone.utc):
                    repo.delete_by_token_hash(token_hash)
                    raise Unauthorized("Session expired")
            request.state.company_id = session.get("company_id")
            request.state.user_id = session.get("user_id")
            request.state.role = (session.get("role_key") or "EMPLOYEE").upper()
            request.state.session_id = session.get("id")
            user_agent = request.headers.get("User-Agent")
            ip = request.client.host if request.client else None
            repo.touch(token_hash, user_agent, ip)
            return

        if settings.DEV_MODE:
            company_id = request.headers.get("X-COMPANY-ID")
            user_id = request.headers.get("X-USER-ID")
            role = request.headers.get("X-ROLE")
            if company_id or user_id or role:
                request.state.company_id = company_id
                request.state.user_id = user_id
                request.state.role = (role or "EMPLOYEE").upper()
                request.state.role = get_role(request)
                return

        request.state.company_id = None
        request.state.user_id = None
        request.state.role = "EMPLOYEE"
        if path.startswith("/api"):
            raise Unauthorized("Authentication required")

    def _is_exempt_path(self, method: str, path: str) -> bool:
        if (method, path) in EXEMPT_PATHS:
            return True
        if settings.ENV.lower() not in {"prod", "production"} and method == "GET" and path in {"/docs", "/openapi.json"}:
            return True
        return False
