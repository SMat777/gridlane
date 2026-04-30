"""
Run persistence service.

Converts execution engine results (dicts) to SQLAlchemy models
and provides CRUD operations for run history.

Sits between the API layer and the database. The execution engine
stays pure (no DB dependency) — this service handles persistence.
"""

import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.run import PipelineRunModel, StepResultModel


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
        """

        def _parse_iso(value: str | None) -> datetime | None:
            if not value:
                return None
            return datetime.fromisoformat(value)

        run = PipelineRunModel(
            id=uuid.UUID(run_result["id"]),
            pipeline_id=run_result["pipeline_id"],
            pipeline_name=run_result["pipeline_name"],
            status=run_result["status"],
            started_at=_parse_iso(run_result.get("started_at")),
            completed_at=_parse_iso(run_result.get("completed_at")),
            total_duration_ms=run_result.get("total_duration_ms"),
            total_cost_usd=run_result.get("total_cost_usd"),
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
                cost_usd=step_dict.get("cost_usd"),
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
