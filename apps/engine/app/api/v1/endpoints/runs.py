"""
Pipeline run endpoints.

POST /runs — Execute a pipeline and return results (with optional DB persistence).
GET  /runs — List run history.
GET  /runs/{run_id} — Get a single run with step details.
"""

import asyncio
import json
import logging
import uuid
from typing import AsyncIterator

from fastapi import APIRouter, Depends, Header, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.api.v1.schemas import (
    CancelRunResponse,
    RunAsyncResponse,
    RunDetailResponse,
    RunHistoryResponse,
    RunListItem,
    RunPipelineRequest,
    RunPipelineResponse,
)
from app.core.database import get_db
from app.core.errors import ErrorCode, PipelineError
from app.services.event_bus import bus
from app.services.execution import ExecutionEngine
from app.services.run_coordinator import coordinator
from app.services.run_service import RunService

# How often to send SSE comment-events to keep proxies from closing the
# connection. 15 seconds is comfortably under typical 30-60s proxy timeouts.
HEARTBEAT_INTERVAL_SECONDS = 15

# Final event types — when one of these arrives the stream closes.
TERMINAL_EVENTS = {"run_completed", "run_failed", "run_cancelled"}

logger = logging.getLogger(__name__)

router = APIRouter()

# Default timeout for pipeline execution (seconds)
EXECUTION_TIMEOUT_SECONDS = 120


def _model_to_run_response(run_model) -> dict:
    """Convert a PipelineRunModel to the API response shape.

    Handles Decimal → float and UUID → str conversions for JSON serialization.
    """
    return {
        "id": str(run_model.id),
        "pipeline_id": str(run_model.pipeline_id) if run_model.pipeline_id else "",
        "pipeline_name": run_model.pipeline_name,
        "status": run_model.status,
        "total_duration_ms": run_model.total_duration_ms,
        "total_cost_usd": (
            float(run_model.total_cost_usd)
            if run_model.total_cost_usd is not None
            else None
        ),
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
                "cost_usd": float(s.cost_usd) if s.cost_usd is not None else None,
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
        raise PipelineError(
            code=ErrorCode.EXECUTION_TIMEOUT,
            message=f"Pipeline execution timed out after {EXECUTION_TIMEOUT_SECONDS}s",
            status_code=504,
        )
    except ValueError as e:
        # Validation errors from engine (cycle detection, orphan edges)
        error_msg = str(e)
        code = ErrorCode.VALIDATION_ERROR
        if "cycle" in error_msg.lower():
            code = ErrorCode.CYCLE_DETECTED
        elif "non-existent" in error_msg.lower():
            code = ErrorCode.ORPHAN_EDGE
        raise PipelineError(code=code, message=error_msg, status_code=422)

    # Persist to DB — soft fail so the user always gets their result
    try:
        service = RunService(db)
        await service.save_run(run_result, pipeline_dict)
    except Exception:
        logger.warning("Failed to persist run to database", exc_info=True)

    return {"run": run_result}


@router.post("/runs/async", response_model=RunAsyncResponse, status_code=202)
async def launch_run_async(
    request: RunPipelineRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Launch a pipeline run in the background.

    Returns immediately with the run_id. The caller subscribes to
    GET /runs/{run_id}/stream for live progress (PR a2 wires this up)
    or polls GET /runs/{run_id} for the eventual result.

    The sync POST /runs is preserved for backward compatibility while
    the frontend migrates.
    """
    pipeline_dict = request.pipeline.model_dump()
    run_id = uuid.uuid4()

    # Create the pending row first so cancel/status endpoints find it
    service = RunService(db)
    await service.create_pending_run(run_id, pipeline_dict)
    await db.commit()

    await coordinator.launch(run_id, pipeline_dict)

    return {
        "run_id": str(run_id),
        "status": "running",
        "stream_url": f"/api/v1/runs/{run_id}/stream",
    }


@router.post("/runs/{run_id}/cancel", response_model=CancelRunResponse)
async def cancel_run(
    run_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Request cancellation of a running pipeline.

    Cancellation is cooperative: the engine checks the cancel flag between
    steps. The current step is allowed to finish (avoiding half-applied
    connector side-effects). Remaining steps are marked cancelled.

    Returns the post-call status. 404 if the run doesn't exist.
    Note: a 200 with status='completed'/'failed'/'cancelled' means the run
    already finished — no transition was needed.
    """
    service = RunService(db)

    # Set the DB flag (also handles the 'already terminal' case)
    db_status = await service.set_cancel_requested(run_id)
    if db_status is None:
        raise PipelineError(
            code=ErrorCode.NOT_FOUND,
            message="Run not found",
            status_code=404,
        )

    # Also signal in-process coordinator if the task is running here
    await coordinator.cancel(run_id)

    return {"run_id": str(run_id), "status": db_status}


@router.get("/runs/{run_id}/stream")
async def stream_run(
    run_id: uuid.UUID,
    request: Request,
    last_event_id: str | None = Header(default=None, alias="Last-Event-ID"),
    db: AsyncSession = Depends(get_db),
):
    """
    Stream run progress events via SSE.

    Behavior:
      - If the run is currently active, attach to the live event bus.
        Replays any events with sequence > Last-Event-ID first, then
        continues with new events.
      - If the run already finished, replay events from the DB and close.
      - If the run is unknown (no DB row, no live channel), 404.

    Heartbeat comment-events are sent every 15s while the connection
    is open to prevent intermediate proxies from closing it.
    """
    last_seq = _parse_last_event_id(last_event_id)

    # Pre-check via the request-scoped session (returns 404 cleanly if missing)
    pre_service = RunService(db)
    run = await pre_service.get_run(run_id)
    live_channel = bus.get_channel(run_id)
    if run is None and live_channel is None:
        raise PipelineError(
            code=ErrorCode.NOT_FOUND,
            message="Run not found",
            status_code=404,
        )

    # Replay events from the same session before the connection upgrades.
    # This bounded list is fine — a run produces at most O(steps) events.
    initial_replay = await pre_service.list_events_after(
        run_id, after_sequence=last_seq
    )

    async def event_stream() -> AsyncIterator[dict]:
        replayed_max = last_seq
        for event_model in initial_replay:
            yield {
                "id": str(event_model.sequence),
                "event": event_model.event_type,
                "data": json.dumps(event_model.payload),
            }
            replayed_max = max(replayed_max, event_model.sequence)
            if event_model.event_type in TERMINAL_EVENTS:
                return  # finished run — replay is everything

        # Live attach if the run is still in flight
        channel = bus.get_channel(run_id)
        if channel is None:
            return

        queue = channel.subscribe()
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    event = await asyncio.wait_for(
                        queue.get(),
                        timeout=HEARTBEAT_INTERVAL_SECONDS,
                    )
                except asyncio.TimeoutError:
                    yield {"comment": "keepalive"}
                    continue

                if event.sequence <= replayed_max:
                    continue

                yield {
                    "id": str(event.sequence),
                    "event": event.event_type,
                    "data": json.dumps(event.payload),
                }
                if event.event_type in TERMINAL_EVENTS:
                    break
        finally:
            channel.unsubscribe(queue)

    return EventSourceResponse(event_stream())


def _parse_last_event_id(header_value: str | None) -> int:
    """Parse Last-Event-ID. -1 means "from the beginning"."""
    if not header_value:
        return -1
    try:
        return int(header_value)
    except (TypeError, ValueError):
        return -1


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
                pipeline_id=str(r.pipeline_id) if r.pipeline_id else "",
                pipeline_name=r.pipeline_name,
                status=r.status,
                total_duration_ms=r.total_duration_ms,
                total_cost_usd=(
                    float(r.total_cost_usd) if r.total_cost_usd is not None else None
                ),
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
        raise PipelineError(
            code=ErrorCode.NOT_FOUND,
            message="Run not found",
            status_code=404,
        )

    return {"run": _model_to_run_response(run)}
