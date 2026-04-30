"""
Pipeline run endpoints.

POST /runs — Execute a pipeline and return results.
"""

import asyncio

from fastapi import APIRouter, HTTPException

from app.api.v1.schemas import RunPipelineRequest, RunPipelineResponse
from app.services.execution import ExecutionEngine

router = APIRouter()

# Default timeout for pipeline execution (seconds)
EXECUTION_TIMEOUT_SECONDS = 120


@router.post("/runs", response_model=RunPipelineResponse)
async def run_pipeline(request: RunPipelineRequest) -> dict:
    """
    Execute a pipeline and return the run result.

    Receives a pipeline definition, executes each node in topological
    order with stub executors, and returns per-step results with timing.

    The engine runs in a thread pool to avoid blocking the async event
    loop, with a timeout to prevent runaway executions.
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

    return {"run": run_result}
