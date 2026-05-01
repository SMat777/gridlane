"""
RunService unit tests.

Tests the service layer that converts execution results to DB models
and provides CRUD operations for run history.
"""

import uuid
from datetime import timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.run import PipelineRunModel, StepResultModel
from app.services.run_service import RunService
from tests.conftest import PIPE_UUID


class TestSaveRun:
    """Tests for RunService.save_run()."""

    @pytest.mark.asyncio
    async def test_save_run_adds_run_model(self, mock_session, sample_run_result):
        """save_run should create a PipelineRunModel and add it to the session."""
        service = RunService(mock_session)

        pipeline_snapshot = {"id": str(PIPE_UUID), "name": "Test Pipeline"}
        await service.save_run(sample_run_result, pipeline_snapshot)

        # Should call session.add() with a PipelineRunModel
        mock_session.add.assert_called_once()
        added_model = mock_session.add.call_args[0][0]
        assert isinstance(added_model, PipelineRunModel)
        assert added_model.pipeline_id == PIPE_UUID
        assert added_model.pipeline_name == "Test Pipeline"
        assert added_model.status == "completed"
        assert added_model.total_duration_ms == 2000

    @pytest.mark.asyncio
    async def test_save_run_creates_step_models(self, mock_session, sample_run_result):
        """save_run should create StepResultModel for each step."""
        service = RunService(mock_session)

        pipeline_snapshot = {"id": str(PIPE_UUID), "name": "Test Pipeline"}
        await service.save_run(sample_run_result, pipeline_snapshot)

        added_model = mock_session.add.call_args[0][0]
        assert len(added_model.steps) == 2

        step_0 = added_model.steps[0]
        assert isinstance(step_0, StepResultModel)
        assert step_0.node_id == "node_1"
        assert step_0.node_type == "datasource"
        assert step_0.order == 0

    @pytest.mark.asyncio
    async def test_save_run_maps_ai_metrics(self, mock_session, sample_run_result):
        """save_run should map token_usage and cost_usd from AI steps."""
        service = RunService(mock_session)

        await service.save_run(sample_run_result, {})

        added_model = mock_session.add.call_args[0][0]
        ai_step = added_model.steps[1]
        assert ai_step.input_tokens == 100
        assert ai_step.output_tokens == 50
        assert ai_step.total_tokens == 150
        assert ai_step.cost_usd == Decimal("0.002")

    @pytest.mark.asyncio
    async def test_save_run_flushes_session(self, mock_session, sample_run_result):
        """save_run should flush to get the generated IDs without committing."""
        service = RunService(mock_session)

        await service.save_run(sample_run_result, {})

        mock_session.flush.assert_awaited_once()


class TestListRuns:
    """Tests for RunService.list_runs()."""

    @pytest.mark.asyncio
    async def test_list_runs_returns_all(self, mock_session, sample_run_model):
        """list_runs with no filter should return all runs."""
        # Mock the query result
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_run_model]
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = RunService(mock_session)
        runs = await service.list_runs()

        assert len(runs) == 1
        assert runs[0].pipeline_id == PIPE_UUID

    @pytest.mark.asyncio
    async def test_list_runs_with_pipeline_filter(self, mock_session, sample_run_model):
        """list_runs should accept pipeline_id filter."""
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_run_model]
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = RunService(mock_session)
        runs = await service.list_runs(pipeline_id="pipe-001")

        assert len(runs) == 1
        # Verify the query was executed (we can't inspect SQLAlchemy query easily)
        mock_session.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_list_runs_empty(self, mock_session):
        """list_runs should return empty list when no runs exist."""
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = RunService(mock_session)
        runs = await service.list_runs()

        assert runs == []


class TestCreatePendingRun:
    """Tests for RunService.create_pending_run() — used by async launch."""

    @pytest.mark.asyncio
    async def test_creates_run_with_running_status(
        self, mock_session, sample_pipeline_dict
    ):
        """A new pending run starts with status='running' and no completion fields."""
        service = RunService(mock_session)

        run_id = uuid.uuid4()
        await service.create_pending_run(
            run_id=run_id,
            pipeline_dict=sample_pipeline_dict,
        )

        mock_session.add.assert_called_once()
        added = mock_session.add.call_args[0][0]
        assert isinstance(added, PipelineRunModel)
        assert added.id == run_id
        assert added.status == "running"
        assert added.completed_at is None
        assert added.total_duration_ms is None
        assert added.cancel_requested is False
        assert added.pipeline_id == PIPE_UUID
        assert added.pipeline_name == "Test Pipeline"
        assert added.pipeline_snapshot == sample_pipeline_dict

    @pytest.mark.asyncio
    async def test_flushes_to_persist(self, mock_session, sample_pipeline_dict):
        """create_pending_run flushes so the row exists for foreign key references."""
        service = RunService(mock_session)
        await service.create_pending_run(uuid.uuid4(), sample_pipeline_dict)
        mock_session.flush.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_handles_missing_pipeline_id(self, mock_session):
        """If pipeline hasn't been saved yet, pipeline_id is None (nullable FK)."""
        service = RunService(mock_session)
        pipeline = {"id": "", "name": "Untitled", "nodes": [], "edges": []}

        await service.create_pending_run(uuid.uuid4(), pipeline)

        added = mock_session.add.call_args[0][0]
        assert added.pipeline_id is None
        assert added.pipeline_name == "Untitled"


class TestUpdateRunStatus:
    """Tests for RunService.update_run_status() — terminal state transitions."""

    @pytest.mark.asyncio
    async def test_marks_run_completed(self, mock_session):
        """Transitioning to a terminal state sets completed_at and totals."""
        run_id = uuid.uuid4()
        service = RunService(mock_session)

        await service.update_run_status(
            run_id=run_id,
            status="completed",
            total_duration_ms=2500,
            total_cost_usd=0.012,
        )

        # Should issue an UPDATE statement
        mock_session.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_marks_run_failed_without_cost(self, mock_session):
        """A failed run with no AI steps has no cost — total_cost_usd may be None."""
        service = RunService(mock_session)

        await service.update_run_status(
            run_id=uuid.uuid4(),
            status="failed",
            total_duration_ms=120,
            total_cost_usd=None,
        )

        mock_session.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_marks_run_cancelled(self, mock_session):
        """Cancellation is a terminal state too."""
        service = RunService(mock_session)
        await service.update_run_status(
            run_id=uuid.uuid4(),
            status="cancelled",
            total_duration_ms=500,
            total_cost_usd=None,
        )
        mock_session.execute.assert_awaited_once()


class TestSetCancelRequested:
    """Tests for RunService.set_cancel_requested() — used by /cancel endpoint."""

    @pytest.mark.asyncio
    async def test_sets_flag_on_running_run(self, mock_session):
        """Sets cancel_requested=true when run is in a non-terminal state."""
        service = RunService(mock_session)

        # Mock the SELECT step that fetches current status
        mock_run = MagicMock()
        mock_run.status = "running"
        mock_run.cancel_requested = False
        mock_select_result = MagicMock()
        mock_select_scalars = MagicMock()
        mock_select_scalars.first.return_value = mock_run
        mock_select_result.scalars.return_value = mock_select_scalars
        mock_session.execute = AsyncMock(return_value=mock_select_result)

        result = await service.set_cancel_requested(uuid.uuid4())

        assert result == "cancelling"
        # Should have called execute (select + update)
        assert mock_session.execute.await_count >= 2

    @pytest.mark.asyncio
    async def test_returns_existing_status_when_terminal(self, mock_session):
        """If run already finished, return its current status without modifying it."""
        service = RunService(mock_session)

        mock_run = MagicMock()
        mock_run.status = "completed"
        mock_run.cancel_requested = False
        mock_select_result = MagicMock()
        mock_select_scalars = MagicMock()
        mock_select_scalars.first.return_value = mock_run
        mock_select_result.scalars.return_value = mock_select_scalars
        mock_session.execute = AsyncMock(return_value=mock_select_result)

        result = await service.set_cancel_requested(uuid.uuid4())

        assert result == "completed"
        # Only the SELECT, no UPDATE
        assert mock_session.execute.await_count == 1

    @pytest.mark.asyncio
    async def test_returns_none_when_run_not_found(self, mock_session):
        """If run doesn't exist, return None so endpoint can return 404."""
        service = RunService(mock_session)

        mock_select_result = MagicMock()
        mock_select_scalars = MagicMock()
        mock_select_scalars.first.return_value = None
        mock_select_result.scalars.return_value = mock_select_scalars
        mock_session.execute = AsyncMock(return_value=mock_select_result)

        result = await service.set_cancel_requested(uuid.uuid4())

        assert result is None


class TestUpsertStepResult:
    """Tests for RunService.upsert_step_result() — progressive step persistence."""

    @pytest.mark.asyncio
    async def test_inserts_new_step(self, mock_session):
        """A new step is inserted with started_at and status='running'."""
        service = RunService(mock_session)

        await service.upsert_step_result(
            run_id=uuid.uuid4(),
            step_dict={
                "node_id": "node_1",
                "node_type": "datasource",
                "node_label": "Source",
                "status": "running",
                "order": 0,
                "input": None,
                "started_at": "2026-04-30T12:00:00+00:00",
            },
        )

        # Should call execute (postgres ON CONFLICT upsert)
        mock_session.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_upserts_completion(self, mock_session):
        """An update to an existing step writes output, duration, cost."""
        service = RunService(mock_session)

        await service.upsert_step_result(
            run_id=uuid.uuid4(),
            step_dict={
                "node_id": "node_1",
                "node_type": "ai",
                "node_label": "Analyze",
                "status": "completed",
                "order": 0,
                "input": {"x": 1},
                "output": {"y": 2},
                "started_at": "2026-04-30T12:00:00+00:00",
                "completed_at": "2026-04-30T12:00:01+00:00",
                "duration_ms": 1000,
                "token_usage": {
                    "input_tokens": 10,
                    "output_tokens": 5,
                    "total_tokens": 15,
                },
                "cost_usd": 0.001,
            },
        )

        mock_session.execute.assert_awaited_once()


class TestAppendEvent:
    """Tests for RunService.append_event() — backs SSE persistence."""

    @pytest.mark.asyncio
    async def test_inserts_event_with_sequence(self, mock_session):
        """append_event creates a RunEventModel with the given sequence."""
        from app.models.run import RunEventModel

        service = RunService(mock_session)
        run_id = uuid.uuid4()

        await service.append_event(
            run_id=run_id,
            sequence=0,
            event_type="run_started",
            payload={"total_steps": 3},
        )

        mock_session.add.assert_called_once()
        added = mock_session.add.call_args[0][0]
        assert isinstance(added, RunEventModel)
        assert added.run_id == run_id
        assert added.sequence == 0
        assert added.event_type == "run_started"
        assert added.payload == {"total_steps": 3}
        mock_session.flush.assert_awaited_once()


class TestListEventsAfter:
    """Tests for RunService.list_events_after() — backs SSE replay."""

    @pytest.mark.asyncio
    async def test_returns_empty_when_no_events(self, mock_session):
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = RunService(mock_session)
        events = await service.list_events_after(uuid.uuid4(), after_sequence=-1)
        assert events == []

    @pytest.mark.asyncio
    async def test_filters_by_sequence(self, mock_session):
        """list_events_after issues a SELECT — query exactness is hard to
        assert without a real DB, so we verify execute was called."""
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = RunService(mock_session)
        await service.list_events_after(uuid.uuid4(), after_sequence=5)
        mock_session.execute.assert_awaited_once()


class TestGetRun:
    """Tests for RunService.get_run()."""

    @pytest.mark.asyncio
    async def test_get_run_returns_run(self, mock_session, sample_run_model):
        """get_run should return the run with matching ID."""
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.first.return_value = sample_run_model
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = RunService(mock_session)
        run = await service.get_run(sample_run_model.id)

        assert run is not None
        assert run.id == sample_run_model.id

    @pytest.mark.asyncio
    async def test_get_run_returns_none_for_missing(self, mock_session):
        """get_run should return None when run doesn't exist."""
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.first.return_value = None
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = RunService(mock_session)
        run = await service.get_run(uuid.uuid4())

        assert run is None


class TestMarkOrphanedRunsFailed:
    """Tests for RunService.mark_orphaned_runs_failed() — startup cleanup."""

    @pytest.mark.asyncio
    async def test_returns_rowcount_from_update(self, mock_session):
        """Returns the number of rows the UPDATE affected."""
        mock_result = MagicMock()
        mock_result.rowcount = 3
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = RunService(mock_session)
        cleaned = await service.mark_orphaned_runs_failed(
            older_than=timedelta(hours=1)
        )

        assert cleaned == 3
        mock_session.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_returns_zero_when_rowcount_is_none(self, mock_session):
        """Some DB drivers return None for rowcount — coerce to 0."""
        mock_result = MagicMock()
        mock_result.rowcount = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = RunService(mock_session)
        cleaned = await service.mark_orphaned_runs_failed(
            older_than=timedelta(hours=1)
        )

        assert cleaned == 0

    @pytest.mark.asyncio
    async def test_uses_provided_threshold(self, mock_session):
        """The cutoff in the WHERE clause derives from the threshold passed in.

        We can't introspect the SQL easily, but we can verify the call ran
        without exception for any reasonable threshold value.
        """
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = RunService(mock_session)
        for hours in (1, 24, 168):
            await service.mark_orphaned_runs_failed(
                older_than=timedelta(hours=hours)
            )

        assert mock_session.execute.await_count == 3
