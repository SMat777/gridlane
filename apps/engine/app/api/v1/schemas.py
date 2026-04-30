"""
Pydantic schemas for API request/response validation.

These are the Python equivalents of the TypeScript types
in packages/shared/src/execution.ts.
"""

from pydantic import BaseModel, Field


class NodeData(BaseModel):
    """Data carried by a pipeline node."""

    label: str
    nodeType: str  # noqa: N815
    config: dict | None = None


class PipelineNode(BaseModel):
    """A node in the pipeline definition."""

    id: str
    type: str
    position: dict = Field(default_factory=lambda: {"x": 0, "y": 0})
    data: NodeData


class PipelineEdge(BaseModel):
    """A directed edge between two nodes."""

    id: str
    source: str
    target: str


class PipelineDefinition(BaseModel):
    """The pipeline to execute."""

    id: str
    name: str
    nodes: list[PipelineNode]
    edges: list[PipelineEdge]


class RunPipelineRequest(BaseModel):
    """Request body for POST /runs."""

    pipeline: PipelineDefinition


class TokenUsage(BaseModel):
    """Token usage metrics for AI steps."""

    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


class StepResultResponse(BaseModel):
    """A single step result in the run response."""

    node_id: str
    node_type: str
    node_label: str
    status: str
    order: int
    input: object | None = None
    output: object | None = None
    error: str | None = None
    started_at: str
    completed_at: str | None = None
    duration_ms: int | None = None
    token_usage: TokenUsage | None = None
    cost_usd: float | None = None


class PipelineRunResponse(BaseModel):
    """A complete pipeline run response."""

    id: str
    pipeline_id: str
    pipeline_name: str
    status: str
    steps: list[StepResultResponse]
    total_duration_ms: int | None = None
    total_cost_usd: float | None = None
    started_at: str
    completed_at: str | None = None


class RunPipelineResponse(BaseModel):
    """Response wrapper for POST /runs."""

    run: PipelineRunResponse


class RunListItem(BaseModel):
    """Summary item for run history listing."""

    id: str
    pipeline_id: str
    pipeline_name: str
    status: str
    total_duration_ms: int | None = None
    total_cost_usd: float | None = None
    started_at: str
    completed_at: str | None = None
    step_count: int = 0


class RunHistoryResponse(BaseModel):
    """Response wrapper for GET /runs."""

    runs: list[RunListItem]


class RunDetailResponse(BaseModel):
    """Response wrapper for GET /runs/{run_id}."""

    run: PipelineRunResponse
