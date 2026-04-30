"""
RunService unit tests.

Tests the service layer that converts execution results to DB models
and provides CRUD operations for run history.
"""

import uuid
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
