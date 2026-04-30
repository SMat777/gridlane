"""
Pipeline run endpoints.

POST /runs — Execute a pipeline and return results (with optional DB persistence).
GET  /runs — List run history.
GET  /runs/{run_id} — Get a single run with step details.
"""

import asyncio
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas import (
    RunDetailResponse,
    RunHistoryResponse,
    RunListItem,
    RunPipelineRequest,
    RunPipelineResponse,
)
from app.core.database import get_db
from app.services.execution import ExecutionEngine
from app.services.run_service import RunService

logger = logging.getLogger(__name__)

router = APIRouter()

# Default timeout for pipeline execution (seconds)
EXECUTION_TIMEOUT_SECONDS = 120


def _model_to_run_response(run_model) -> dict:
    """Convert a PipelineRunModel to the API response shape."""
    return {
        "id": str(run_model.id),
        "pipeline_id": run_model.pipeline_id,
        "pipeline_name": run_model.pipeline_name,
        "status": run_model.status,
        "total_duration_ms": run_model.total_duration_ms,
        "total_cost_usd": run_model.total_cost_usd,
        "started_at": run_model.started_at.isoformat() if run_model.started_at else "",
        "completed_at": (
            run_model.completed_at.isoformat() if run_model.completed_at else None
        ),
        "steps": [
            {
                "node_id": s.node_id,
                "node_type": s.node_type,
                "node_label": s.node_label,
                "status": s.status,
                "order": s.order,
                "input": s.input_data,
                "output": s.output_data,
                "error": s.error,
                "started_at": s.started_at.isoformat() if s.started_at else "",
                "completed_at": (
                    s.completed_at.isoformat() if s.completed_at else None
                ),
                "duration_ms": s.duration_ms,
                "token_usage": (
                    {
                        "input_tokens": s.input_tokens or 0,
                        "output_tokens": s.output_tokens or 0,
                        "total_tokens": s.total_tokens or 0,
                    }
                    if s.input_tokens is not None
                    else None
                ),
                "cost_usd": s.cost_usd,
            }
            for s in sorted(run_model.steps, key=lambda s: s.order)
        ],
    }


@router.post("/runs", response_model=RunPipelineResponse)
async def run_pipeline(
    request: RunPipelineRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Execute a pipeline and return the run result.

    Receives a pipeline definition, executes each node in topological
    order with stub executors, and returns per-step results with timing.

    After execution, persists the run to the database (soft fail —
    if DB is unavailable, the result is still returned).
    """
    pipeline_dict = request.pipeline.model_dump()
    engine = ExecutionEngine()

    try:
        # Run sync engine in thread pool so it doesn't block the event loop
        run_result = await asyncio.wait_for(
            asyncio.to_thread(engine.execute, pipeline_dict),
            timeout=EXECUTION_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail=f"Pipeline execution timeout after {EXECUTION_TIMEOUT_SECONDS} seconds",
        )
    except ValueError as e:
        # Validation errors from engine (cycle detection, orphan edges)
        raise HTTPException(status_code=422, detail=str(e))

    # Persist to DB — soft fail so the user always gets their result
    try:
        service = RunService(db)
        await service.save_run(run_result, pipeline_dict)
    except Exception:
        logger.warning("Failed to persist run to database", exc_info=True)

    return {"run": run_result}


@router.get("/runs", response_model=RunHistoryResponse)
async def list_runs(
    pipeline_id: str | None = Query(None, description="Filter by pipeline ID"),
    limit: int = Query(50, ge=1, le=200, description="Max results"),
    offset: int = Query(0, ge=0, description="Skip N results"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    List pipeline run history.

    Returns runs ordered by most recent first, with optional
    filtering by pipeline_id and pagination.
    """
    service = RunService(db)
    runs = await service.list_runs(pipeline_id=pipeline_id, limit=limit, offset=offset)

    return {
        "runs": [
            RunListItem(
                id=str(r.id),
                pipeline_id=r.pipeline_id,
                pipeline_name=r.pipeline_name,
                status=r.status,
                total_duration_ms=r.total_duration_ms,
                total_cost_usd=r.total_cost_usd,
                started_at=r.started_at.isoformat() if r.started_at else "",
                completed_at=(r.completed_at.isoformat() if r.completed_at else None),
                step_count=len(r.steps),
            ).model_dump()
            for r in runs
        ]
    }


@router.get("/runs/{run_id}", response_model=RunDetailResponse)
async def get_run(
    run_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get a single pipeline run with full step details."""
    service = RunService(db)
    run = await service.get_run(run_id)

    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    return {"run": _model_to_run_response(run)}
