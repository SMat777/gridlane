"""
Run persistence service.

Converts execution engine results (dicts) to SQLAlchemy models
and provides CRUD operations for run history.

Sits between the API layer and the database. The execution engine
stays pure (no DB dependency) — this service handles persistence.

Schema is managed by Supabase CLI (supabase/migrations/).
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.run import PipelineRunModel, RunEventModel, StepResultModel


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

    async def create_pending_run(
        self,
        run_id: uuid.UUID,
        pipeline_dict: dict,
    ) -> PipelineRunModel:
        """
        Insert a run row in 'running' state before the engine starts.

        Used by async launch flow: gives /runs/async a row to return a
        run_id for, and a row that the engine + cancel endpoint can
        coordinate around. Completion fields are filled in later via
        update_run_status().
        """
        run = PipelineRunModel(
            id=run_id,
            pipeline_id=_parse_uuid(pipeline_dict.get("id")),
            pipeline_name=pipeline_dict.get("name", "Untitled Pipeline"),
            status="running",
            cancel_requested=False,
            started_at=datetime.now(timezone.utc),
            pipeline_snapshot=pipeline_dict,
        )
        self.session.add(run)
        await self.session.flush()
        return run

    async def update_run_status(
        self,
        run_id: uuid.UUID,
        status: str,
        total_duration_ms: int | None,
        total_cost_usd: float | None,
    ) -> None:
        """
        Transition a run to a terminal state.

        Sets completed_at = now() and stores aggregate metrics. The engine
        calls this once when a run finishes (completed/failed/cancelled).
        """
        await self.session.execute(
            update(PipelineRunModel)
            .where(PipelineRunModel.id == run_id)
            .values(
                status=status,
                completed_at=datetime.now(timezone.utc),
                total_duration_ms=total_duration_ms,
                total_cost_usd=_to_decimal(total_cost_usd),
            )
        )

    async def set_cancel_requested(self, run_id: uuid.UUID) -> str | None:
        """
        Signal cooperative cancellation to the running engine.

        Returns the post-call status:
          - "cancelling" if the run was running and the flag is now set
          - "completed"/"failed"/"cancelled" if the run already finished
          - None if the run does not exist (caller should 404)

        We deliberately don't write the flag if the run is already terminal:
        it would be a no-op and would muddy the audit trail.
        """
        result = await self.session.execute(
            select(PipelineRunModel).where(PipelineRunModel.id == run_id)
        )
        run = result.scalars().first()
        if run is None:
            return None

        if run.status in ("completed", "failed", "cancelled"):
            return run.status

        await self.session.execute(
            update(PipelineRunModel)
            .where(PipelineRunModel.id == run_id)
            .values(cancel_requested=True)
        )
        return "cancelling"

    async def upsert_step_result(
        self,
        run_id: uuid.UUID,
        step_dict: dict,
    ) -> None:
        """
        Insert or update a step result by (run_id, node_id, order).

        The engine calls this twice per step: once at start (status='running',
        only started_at filled in) and once at completion (status='completed'
        or 'failed', with output/duration/metrics). This streams results to
        the DB as the run progresses, so reconnecting clients see live state.

        Uses Postgres ON CONFLICT for atomic upsert. The conflict target is
        the unique constraint on (run_id, node_id) — added in this PR's
        migration to support deterministic upserts.
        """
        token_usage = step_dict.get("token_usage") or {}

        values = {
            "run_id": run_id,
            "node_id": step_dict["node_id"],
            "node_type": step_dict["node_type"],
            "node_label": step_dict["node_label"],
            "status": step_dict["status"],
            "order": step_dict["order"],
            "input_data": step_dict.get("input"),
            "output_data": step_dict.get("output"),
            "error": step_dict.get("error"),
            "started_at": _parse_iso(step_dict.get("started_at")),
            "completed_at": _parse_iso(step_dict.get("completed_at")),
            "duration_ms": step_dict.get("duration_ms"),
            "input_tokens": token_usage.get("input_tokens"),
            "output_tokens": token_usage.get("output_tokens"),
            "total_tokens": token_usage.get("total_tokens"),
            "cost_usd": _to_decimal(step_dict.get("cost_usd")),
        }

        stmt = pg_insert(StepResultModel).values(**values)
        # On conflict, update everything except the natural key columns
        stmt = stmt.on_conflict_do_update(
            index_elements=["run_id", "node_id"],
            set_={
                k: v
                for k, v in values.items()
                if k not in ("run_id", "node_id", "node_type", "order")
            },
        )
        await self.session.execute(stmt)

    async def append_event(
        self,
        run_id: uuid.UUID,
        sequence: int,
        event_type: str,
        payload: dict,
    ) -> None:
        """Append a run event to the log for SSE replay support.

        Sequence is allocated by the caller (the event bus owns counter
        state during a live run). The unique constraint on
        (run_id, sequence) enforces ordered, gap-free writes.
        """
        event = RunEventModel(
            run_id=run_id,
            sequence=sequence,
            event_type=event_type,
            payload=payload,
        )
        self.session.add(event)
        await self.session.flush()

    async def list_events_after(
        self,
        run_id: uuid.UUID,
        after_sequence: int = -1,
        limit: int = 1000,
    ) -> list[RunEventModel]:
        """Return events for a run with sequence > after_sequence, in order.

        Used by the SSE endpoint for Last-Event-ID resume and for replaying
        already-finished runs to late subscribers. limit is generous —
        no realistic run produces 1000+ events.
        """
        query = (
            select(RunEventModel)
            .where(RunEventModel.run_id == run_id)
            .where(RunEventModel.sequence > after_sequence)
            .order_by(RunEventModel.sequence.asc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

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
