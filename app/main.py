from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.middleware import RequestContextMiddleware
from app.core.db import connect, ensure_indexes, ping
from app.core.errors import AppError, DatabaseDown
from app.core.responses import ok, err
from app.schemas.response import SuccessResponse

from app.routes import employees, leaves
from app.routes.attendance import router as attendance_router
from app.routes.dashboard import router as dashboard_router
from app.routes.meta import router as meta_router
from app.routes.companies import router as companies_router
from app.routes.roles import router as roles_router
from app.routes.users import router as users_router
from app.routes.approvals import router as approvals_router
from app.routes.notifications import router as notifications_router
from app.routes.vault import router as vault_router
from app.routes.audit import router as audit_router

setup_logging()
logger = get_logger("app")

app = FastAPI(title=settings.APP_NAME, version="0.1")

# CORS
origins = ["*"] if settings.FRONTEND_ORIGIN.strip() == "*" else [o.strip() for o in settings.FRONTEND_ORIGIN.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware
app.add_middleware(RequestContextMiddleware)

# Routers
app.include_router(employees.router)
app.include_router(leaves.router)
app.include_router(attendance_router)
app.include_router(dashboard_router)
app.include_router(meta_router)
app.include_router(companies_router)
app.include_router(roles_router)
app.include_router(users_router)
app.include_router(approvals_router)
app.include_router(notifications_router)
app.include_router(vault_router)
app.include_router(audit_router)

@app.on_event("startup")
def on_startup():
    connect()
    if not ping():
        logger.error("Mongo ping failed on startup")
        if settings.MONGO_STARTUP_STRICT:
            raise DatabaseDown("Mongo is not reachable")
        logger.warning("Continuing startup without Mongo due to MONGO_STARTUP_STRICT=false")
        return
    ensure_indexes()
    logger.info("Startup OK - Mongo connected and indexes ensured")

@app.get("/", response_model=SuccessResponse)
def root(request: Request):
    return ok({"service": settings.APP_NAME}, request.state.request_id)

@app.get("/health", response_model=SuccessResponse)
def health(request: Request):
    healthy = ping()
    return ok({"mongo": healthy, "env": settings.ENV}, request.state.request_id)

# Exception handlers
@app.exception_handler(AppError)
async def app_error_handler(request: Request, ex: AppError):
    rid = getattr(request.state, "request_id", "-")
    return JSONResponse(status_code=ex.status_code, content=err(ex.code, ex.message, rid, ex.details))

@app.exception_handler(Exception)
async def unhandled_handler(request: Request, ex: Exception):
    rid = getattr(request.state, "request_id", "-")
    logger.exception("Unhandled exception")
    return JSONResponse(status_code=500, content=err("INTERNAL_ERROR", "Something went wrong", rid))
