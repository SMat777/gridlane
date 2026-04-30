"""
Run coordinator — owns the lifecycle of asynchronously-launched runs.

Responsibilities:
  - Spawn background tasks that drive ExecutionEngine to completion.
  - Hold per-run cancel events that the engine polls between steps.
  - Coordinate persistence (create_pending_run before launch, update_run_status
    after completion).
  - Provide a single in-process registry for the cancel endpoint to look up
    a run's cancel event.

This is intentionally a process-local singleton. Multi-worker scale-out (e.g.,
gunicorn workers) would need to move cancellation flags to Redis or directly
poll the DB cancel_requested column. For foundation phase we run a single
process so an in-memory dict is enough.

Design decisions:
  - The coordinator does NOT hold DB sessions. It opens a fresh session per
    background task via the async_session factory. Holding a session
    across a background task would tie the connection lifetime to the task,
    risking pool exhaustion under concurrent runs.
  - Errors from the engine (validation, execution) are caught and persisted
    as failed runs. Exceptions never escape the background task — they would
    be silently swallowed by asyncio otherwise.
"""

import asyncio
import logging
import uuid
from typing import Awaitable, Callable

from app.core.database import async_session
from app.core.errors import PipelineError
from app.services.execution import ExecutionEngine
from app.services.run_service import RunService

logger = logging.getLogger(__name__)


# Type alias for the async factory that yields a session
SessionFactory = Callable[[], Awaitable]


class RunCoordinator:
    """In-process registry of running pipeline executions."""

    def __init__(self):
        # run_id (uuid) → cancel event for that run
        self._cancel_events: dict[uuid.UUID, asyncio.Event] = {}
        # run_id → background task (kept so we don't get GC'd mid-flight)
        self._tasks: dict[uuid.UUID, asyncio.Task] = {}

    def is_running(self, run_id: uuid.UUID) -> bool:
        """True if the coordinator currently tracks this run as in-flight."""
        return run_id in self._cancel_events

    def get_cancel_event(self, run_id: uuid.UUID) -> asyncio.Event | None:
        """Return the cancel event for a tracked run, or None if not tracked."""
        return self._cancel_events.get(run_id)

    async def launch(
        self,
        run_id: uuid.UUID,
        pipeline_dict: dict,
    ) -> None:
        """
        Spawn a background task that runs the engine to completion.

        Caller is responsible for having INSERTed the pending run row first
        (so cancel/status endpoints find a row immediately). This method
        never blocks on the engine — it returns as soon as the task is
        scheduled.
        """
        cancel_event = asyncio.Event()
        self._cancel_events[run_id] = cancel_event

        task = asyncio.create_task(
            self._run(run_id, pipeline_dict, cancel_event),
            name=f"pipeline-run-{run_id}",
        )
        self._tasks[run_id] = task
        # When task finishes (success or failure), drop our refs
        task.add_done_callback(lambda _t: self._cleanup(run_id))

    async def cancel(self, run_id: uuid.UUID) -> bool:
        """
        Signal cancellation to a running task.

        Returns True if the run was being tracked and the flag was set,
        False if no task is currently tracked for that run_id (caller
        should consult the DB to see if the run already finished).
        """
        event = self._cancel_events.get(run_id)
        if event is None:
            return False
        event.set()
        return True

    def _cleanup(self, run_id: uuid.UUID) -> None:
        """Drop our references to a finished run. Called from task done."""
        self._cancel_events.pop(run_id, None)
        self._tasks.pop(run_id, None)

    async def _run(
        self,
        run_id: uuid.UUID,
        pipeline_dict: dict,
        cancel_event: asyncio.Event,
    ) -> None:
        """
        Background task body: executes engine, persists final state.

        All exceptions are caught here. The DB row is updated with the
        terminal state in every case so clients always see a final status.
        """
        engine = ExecutionEngine()
        run_id_str = str(run_id)

        try:
            run_result = await asyncio.to_thread(
                engine.execute,
                pipeline_dict,
                cancel_event,
                run_id_str,
            )
        except PipelineError as e:
            # Validation errors caught from engine — persist as failed
            logger.warning("Pipeline validation failed for run %s: %s", run_id, e)
            await self._mark_failed(run_id, error_message=e.message)
            return
        except ValueError as e:
            # Cycle detection / orphan edges
            logger.warning("Pipeline structure invalid for run %s: %s", run_id, e)
            await self._mark_failed(run_id, error_message=str(e))
            return
        except Exception as e:  # noqa: BLE001 — defensive: never let bg task die silently
            logger.exception("Unexpected error in run %s", run_id)
            await self._mark_failed(run_id, error_message=f"Internal error: {e}")
            return

        # Persist terminal state and step results
        async with async_session() as session:
            try:
                service = RunService(session)
                # Save all step results progressively (or in bulk here at end —
                # PR a2 will switch this to per-step emission via an event bus)
                for step in run_result.get("steps", []):
                    await service.upsert_step_result(run_id, step)
                await service.update_run_status(
                    run_id=run_id,
                    status=run_result["status"],
                    total_duration_ms=run_result.get("total_duration_ms"),
                    total_cost_usd=run_result.get("total_cost_usd"),
                )
                await session.commit()
            except Exception:
                logger.exception("Failed to persist run result for %s", run_id)
                await session.rollback()

    async def _mark_failed(self, run_id: uuid.UUID, error_message: str) -> None:
        """Update DB run row to status=failed when engine raised before any step."""
        async with async_session() as session:
            try:
                service = RunService(session)
                await service.update_run_status(
                    run_id=run_id,
                    status="failed",
                    total_duration_ms=0,
                    total_cost_usd=None,
                )
                await session.commit()
            except Exception:
                logger.exception("Failed to mark run %s as failed", run_id)
                await session.rollback()


# Process-local singleton. FastAPI imports this directly. If we ever move
# to multi-process workers, this needs to become a per-worker registry plus
# DB-polled cancellation (since workers can't share asyncio.Event across
# process boundaries).
coordinator = RunCoordinator()
