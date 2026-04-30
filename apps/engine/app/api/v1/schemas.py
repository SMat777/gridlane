"""
Pydantic schemas for API request/response validation.

These are the Python equivalents of the TypeScript types
in packages/shared/src/execution.ts.
"""

from pydantic import BaseModel, Field


class NodeData(BaseModel):
    """Data carried by a pipeline node."""

    label: str = Field(max_length=200)
    nodeType: str = Field(max_length=50)  # noqa: N815
    config: dict | None = None


class PipelineNode(BaseModel):
    """A node in the pipeline definition."""

    id: str = Field(max_length=100)
    type: str = Field(max_length=50)
    position: dict = Field(default_factory=lambda: {"x": 0, "y": 0})
    data: NodeData


class PipelineEdge(BaseModel):
    """A directed edge between two nodes."""

    id: str
    source: str
    target: str


class PipelineDefinition(BaseModel):
    """The pipeline to execute.

    Size limits prevent memory exhaustion from oversized requests.
    100 nodes and 500 edges are generous for any realistic pipeline.
    """

    id: str = Field(max_length=100)
    name: str = Field(max_length=200)
    nodes: list[PipelineNode] = Field(max_length=100)
    edges: list[PipelineEdge] = Field(max_length=500)


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
