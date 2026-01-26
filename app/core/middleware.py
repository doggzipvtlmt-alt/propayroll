import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import get_logger, request_id_filter
from app.core.security import get_role, get_company_id, get_user_id

logger = get_logger("middleware")

class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        request_id_filter.request_id = request_id

        role = get_role(request)
        company_id = get_company_id(request)
        user_id = get_user_id(request)
        request.state.role = role
        request.state.company_id = company_id
        request.state.user_id = user_id

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
