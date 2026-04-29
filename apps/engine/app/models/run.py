"""
Pipeline execution models.

PipelineRunModel: a single execution of a pipeline.
StepResultModel: what happened at one node during a run.

These mirror the shared TypeScript types (execution.ts) but live
in the database. The API layer converts between these and the
shared response types.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class PipelineRunModel(Base):
    """A single execution of a pipeline."""

    __tablename__ = "pipeline_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    pipeline_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    pipeline_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")

    # Timing
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    total_duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Cost
    total_cost_usd: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Store the pipeline definition snapshot at time of execution
    pipeline_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)

    # Relationships
    steps: Mapped[list["StepResultModel"]] = relationship(
        back_populates="run",
        cascade="all, delete-orphan",
        order_by="StepResultModel.order",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class StepResultModel(Base):
    """Result of executing a single node in a pipeline."""

    __tablename__ = "step_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pipeline_runs.id", ondelete="CASCADE")
    )
    node_id: Mapped[str] = mapped_column(String(255), nullable=False)
    node_type: Mapped[str] = mapped_column(String(50), nullable=False)
    node_label: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    order: Mapped[int] = mapped_column(Integer, nullable=False)

    # Data
    input_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    output_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timing
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # AI-specific metrics
    input_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cost_usd: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Relationships
    run: Mapped["PipelineRunModel"] = relationship(back_populates="steps")
