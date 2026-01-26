import time
import uuid
from datetime import datetime, timezone
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings
from app.core.errors import Unauthorized
from app.core.logging import get_logger, request_id_filter
from app.core.security import get_bearer_token, hash_token
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

        if not self._is_exempt_path(request.method.upper(), request.url.path):
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
        if not path.startswith("/api"):
            return

        auth_header = request.headers.get("Authorization")
        token = get_bearer_token(request)
        if not token:
            reason = "invalid token" if auth_header else "missing token"
            logger.info("Denied request method=%s path=%s reason=%s", method, path, reason)
            raise Unauthorized("Authentication required")

        token_hash = hash_token(token)
        repo = SessionsRepo()
        session = repo.get_by_token_hash(token_hash)
        if not session:
            logger.info("Denied request method=%s path=%s reason=invalid token", method, path)
            raise Unauthorized("Invalid or expired session")
        expires_at = session.get("expires_at")
        if isinstance(expires_at, datetime):
            if expires_at < datetime.now(timezone.utc):
                repo.delete_by_token_hash(token_hash)
                logger.info("Denied request method=%s path=%s reason=invalid token", method, path)
                raise Unauthorized("Session expired")
        request.state.company_id = session.get("company_id")
        request.state.user_id = session.get("user_id")
        request.state.role = (session.get("role_key") or "EMPLOYEE").upper()
        request.state.session_id = session.get("id")
        user_agent = request.headers.get("User-Agent")
        ip = request.client.host if request.client else None
        repo.touch(token_hash, user_agent, ip)
        return

    def _is_exempt_path(self, method: str, path: str) -> bool:
        if (method, path) in EXEMPT_PATHS:
            return True
        if settings.ENV.lower() not in {"prod", "production"} and method == "GET" and path in {"/docs", "/openapi.json"}:
            return True
        return False
