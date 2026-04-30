"""
Run persistence service.

Converts execution engine results (dicts) to SQLAlchemy models
and provides CRUD operations for run history.

Sits between the API layer and the database. The execution engine
stays pure (no DB dependency) — this service handles persistence.

Schema is managed by Supabase CLI (supabase/migrations/).
"""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.run import PipelineRunModel, StepResultModel


def _parse_uuid(value: str | None) -> uuid.UUID | None:
    """Parse a string as UUID, return None if invalid or empty."""
    if not value:
        return None
    try:
        return uuid.UUID(value)
    except (ValueError, AttributeError):
        return None


def _parse_iso(value: str | None) -> datetime | None:
    """Parse an ISO 8601 string to datetime, return None if empty."""
    if not value:
        return None
    return datetime.fromisoformat(value)


def _to_decimal(value: float | int | None) -> Decimal | None:
    """Convert a float/int to Decimal for financial precision."""
    if value is None:
        return None
    return Decimal(str(value))


class RunService:
    """Persistence layer for pipeline runs."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_run(
        self,
        run_result: dict,
        pipeline_snapshot: dict,
    ) -> PipelineRunModel:
        """
        Persist an execution result to the database.

        Converts the flat dict from ExecutionEngine into SQLAlchemy models.
        Does NOT commit — the caller (API endpoint) owns the transaction.

        pipeline_id is a UUID FK to pipelines table. If the pipeline
        hasn't been saved yet, pipeline_id is set to None (nullable FK).
        """
        run = PipelineRunModel(
            id=uuid.UUID(run_result["id"]),
            pipeline_id=_parse_uuid(run_result.get("pipeline_id")),
            pipeline_name=run_result["pipeline_name"],
            status=run_result["status"],
            started_at=_parse_iso(run_result.get("started_at")),
            completed_at=_parse_iso(run_result.get("completed_at")),
            total_duration_ms=run_result.get("total_duration_ms"),
            total_cost_usd=_to_decimal(run_result.get("total_cost_usd")),
            pipeline_snapshot=pipeline_snapshot,
        )

        steps = []
        for step_dict in run_result.get("steps", []):
            token_usage = step_dict.get("token_usage", {})

            step = StepResultModel(
                run_id=run.id,
                node_id=step_dict["node_id"],
                node_type=step_dict["node_type"],
                node_label=step_dict["node_label"],
                status=step_dict["status"],
                order=step_dict["order"],
                input_data=step_dict.get("input"),
                output_data=step_dict.get("output"),
                error=step_dict.get("error"),
                started_at=_parse_iso(step_dict.get("started_at")),
                completed_at=_parse_iso(step_dict.get("completed_at")),
                duration_ms=step_dict.get("duration_ms"),
                input_tokens=token_usage.get("input_tokens"),
                output_tokens=token_usage.get("output_tokens"),
                total_tokens=token_usage.get("total_tokens"),
                cost_usd=_to_decimal(step_dict.get("cost_usd")),
            )
            steps.append(step)

        run.steps = steps
        self.session.add(run)
        await self.session.flush()

        return run

    async def list_runs(
        self,
        pipeline_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[PipelineRunModel]:
        """
        List pipeline runs, optionally filtered by pipeline_id.

        Returns runs ordered by most recent first.
        """
        query = (
            select(PipelineRunModel)
            .options(selectinload(PipelineRunModel.steps))
            .order_by(PipelineRunModel.started_at.desc())
            .limit(limit)
            .offset(offset)
        )

        if pipeline_id:
            query = query.where(PipelineRunModel.pipeline_id == pipeline_id)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_run(self, run_id: uuid.UUID) -> PipelineRunModel | None:
        """Get a single run by ID, including its steps."""
        query = (
            select(PipelineRunModel)
            .options(selectinload(PipelineRunModel.steps))
            .where(PipelineRunModel.id == run_id)
        )

        result = await self.session.execute(query)
        return result.scalars().first()
