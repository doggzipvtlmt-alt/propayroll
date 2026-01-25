from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.middleware import RequestContextMiddleware
from app.core.db import connect, ensure_indexes, ping
from app.core.errors import AppError, DatabaseDown
from app.core.responses import ok, err

from app.routes import employees, leaves
from app.routes.attendance import router as attendance_router
from app.routes.dashboard import router as dashboard_router
from app.routes.meta import router as meta_router

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

@app.on_event("startup")
def on_startup():
    connect()
    if not ping():
        logger.error("Mongo ping failed on startup")
        raise DatabaseDown("Mongo is not reachable")
    ensure_indexes()
    logger.info("Startup OK - Mongo connected and indexes ensured")

@app.get("/")
def root(request: Request):
    return {"ok": True, "service": settings.APP_NAME}

@app.get("/health")
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
