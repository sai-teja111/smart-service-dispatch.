from time import perf_counter
from contextlib import asynccontextmanager

from fastapi import (
    FastAPI,
    Depends,
    Request,
    HTTPException,
)

from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from Log_config import log
from config import get_settings

from Orm.database import create_db_and_tables


# Import ORM models so SQLModel registers all tables
from Orm.customer import Customer
from Orm.technician import Technician
from Orm.skills import Skill
from Orm.technician_skill import TechnicianSkill
from Orm.service_request import ServiceRequest
from Orm.assignment import Assignment
from Orm.service_history import ServiceHistory
from Orm.feedback import Feedback
from Orm.notifications import Notification
from Orm.admin import Admin
from modules.chroma_service import refresh_service_collection

# API routers
from Api.auth import router as auth_router
from Api.admin import router as admin_router
from Api.dependencies import get_current_user
from Api.service_request import router as service_request_router
from Api.technician import router as technician_router
from Api.history import router as history_router
from Api.feedback import router as feedback_router
from Api.availability import router as availability_router
from Api.reports import router as reports_router
from Api.ai import router as ai_router
from Api.skills import router as skills_router
from Api.notifications import router as notifications_router


# --------------------------------------------------
# Settings and Logger
# --------------------------------------------------

logger = log()
settings = get_settings()


# --------------------------------------------------
# Lifespan
# --------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("FastAPI application startup")

    create_db_and_tables()

    logger.info("Database tables created successfully")

    # Initialize ChromaDB from PostgreSQL skills.
    logger.info("Refreshing ChromaDB service collection")

    refresh_service_collection()

    logger.info("ChromaDB service collection initialized successfully")

    yield

    logger.info("FastAPI application shutdown")

# --------------------------------------------------
# FastAPI Application
# --------------------------------------------------

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

allowed_origins = settings.cors_origins or [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Middleware
# --------------------------------------------------

@app.middleware("http")
async def process_time_middleware(
    request: Request,
    call_next,
):
    start_time = perf_counter()

    response = await call_next(request)

    process_time = perf_counter() - start_time

    response.headers["X-Process-Time"] = f"{process_time:.6f}"

    return response


# --------------------------------------------------
# Global HTTPException Handler
# --------------------------------------------------

@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException,
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
        },
        headers=exc.headers,
    )


# --------------------------------------------------
# Global Request Validation Error Handler
# --------------------------------------------------

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    return JSONResponse(
        status_code=422,
        content={
            "detail": jsonable_encoder(exc.errors()),
        },
    )


# --------------------------------------------------
# Global Unexpected Error Handler
# --------------------------------------------------

@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request,
    exc: Exception,
):
    logger.exception("Unexpected application error")

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error.",
        },
    )


# --------------------------------------------------
# Routers
# --------------------------------------------------

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(service_request_router)
app.include_router(technician_router)
app.include_router(history_router)
app.include_router(feedback_router)
app.include_router(availability_router)
app.include_router(reports_router)
app.include_router(ai_router)
app.include_router(skills_router)
app.include_router(notifications_router)


# --------------------------------------------------
# Home
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Smart Service Dispatch System API is running",
    }


# --------------------------------------------------
# Authentication Test
# --------------------------------------------------

@app.get("/test-auth")
def test_auth(
    current_user=Depends(get_current_user),
):
    return {
        "message": "Authentication successful",
        "user": current_user,
    }
