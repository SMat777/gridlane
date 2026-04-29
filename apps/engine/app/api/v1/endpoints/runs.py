"""
Pipeline run endpoints.

POST /runs — Execute a pipeline and return results.
"""

from fastapi import APIRouter

from app.api.v1.schemas import RunPipelineRequest, RunPipelineResponse
from app.services.execution import ExecutionEngine

router = APIRouter()


@router.post("/runs", response_model=RunPipelineResponse)
async def run_pipeline(request: RunPipelineRequest) -> dict:
    """
    Execute a pipeline and return the run result.

    Receives a pipeline definition, executes each node in topological
    order with stub executors, and returns per-step results with timing.
    """
    # Convert Pydantic model to dict for the execution engine
    pipeline_dict = request.pipeline.model_dump()

    engine = ExecutionEngine()
    run_result = engine.execute(pipeline_dict)

    return {"run": run_result}
