import logging
from contextlib import asynccontextmanager
from datetime import timedelta

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import async_session
from app.core.errors import ErrorCode, PipelineError
from app.services.run_service import RunService

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Application startup/shutdown.

    On startup we sweep for orphaned runs — runs left in 'running' state
    by a process that died or restarted before completion. Without this,
    they'd appear "running" indefinitely, blocking the cancel UI and
    confusing run history. The threshold is generous (default 1h) so
    in-flight runs from a graceful redeploy aren't touched.

    DB errors here must not prevent the app from booting. We log and
    continue — better to serve traffic with stale rows than not at all.
    """
    try:
        async with async_session() as session:
            service = RunService(session)
            cleaned = await service.mark_orphaned_runs_failed(
                older_than=timedelta(seconds=settings.orphan_run_age_seconds),
            )
            await session.commit()
            if cleaned:
                logger.warning(
                    "Marked %d orphaned run(s) as failed on startup", cleaned
                )
    except Exception:
        logger.exception("Failed to clean up orphaned runs on startup")
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.api_version,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.exception_handler(PipelineError)
async def pipeline_error_handler(_request: Request, exc: PipelineError) -> JSONResponse:
    """Convert PipelineError to structured JSON error response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(_request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for unhandled exceptions — never leak stack traces."""
    logger.error("Unhandled exception", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": ErrorCode.INTERNAL_ERROR,
                "message": "An internal error occurred",
                "details": None,
            }
        },
    )


app.include_router(api_router, prefix="/api/v1")
