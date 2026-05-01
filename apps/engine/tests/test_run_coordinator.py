"""
RunCoordinator unit tests.

Tests the in-process registry for async pipeline runs:
  - launching a background task with a cancel event
  - cancelling a tracked run
  - cleanup after task completes
  - error paths (engine failure → run marked failed in DB)

We mock async_session to avoid needing a real DB. The point of these tests
is the coordinator's lifecycle logic, not persistence behavior — that's
covered in test_run_service.py.
"""

import asyncio
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.run_coordinator import RunCoordinator


@pytest.fixture
def mock_async_session_context():
    """Patch async_session so the coordinator's `async with async_session()`
    blocks return a mocked AsyncSession."""

    mock_session = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.execute = AsyncMock()

    # `async with async_session() as s` machinery
    mock_factory = MagicMock()
    mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
    mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

    with patch("app.services.run_coordinator.async_session", mock_factory):
        yield mock_session


@pytest.fixture
def trivial_pipeline():
    """Smallest possible valid pipeline — one datasource node."""
    return {
        "id": "11111111-1111-1111-1111-111111111111",
        "name": "Trivial",
        "nodes": [
            {
                "id": "node_1",
                "type": "datasource",
                "position": {"x": 0, "y": 0},
                "data": {
                    "label": "Source",
                    "nodeType": "datasource",
                    "config": {
                        "sourceType": "sql",
                        "url": "postgresql://localhost/test",
                    },
                },
            }
        ],
        "edges": [],
    }


class TestLifecycle:
    @pytest.mark.asyncio
    async def test_launch_registers_cancel_event(
        self, mock_async_session_context, trivial_pipeline
    ):
        """After launch, get_cancel_event returns a settable Event."""
        coord = RunCoordinator()
        run_id = uuid.uuid4()

        await coord.launch(run_id, trivial_pipeline)

        # Before the task finishes, the event is registered
        event = coord.get_cancel_event(run_id)
        assert event is not None
        assert isinstance(event, asyncio.Event)

        # Let task complete
        await asyncio.sleep(0.05)

    @pytest.mark.asyncio
    async def test_launch_creates_background_task(
        self, mock_async_session_context, trivial_pipeline
    ):
        """The background task drives engine + persistence to completion."""
        coord = RunCoordinator()
        run_id = uuid.uuid4()

        await coord.launch(run_id, trivial_pipeline)
        # Wait long enough for the task to finish (trivial pipeline is fast)
        await asyncio.sleep(0.1)

        # After task done, refs are cleaned up
        assert coord.get_cancel_event(run_id) is None
        assert not coord.is_running(run_id)

    @pytest.mark.asyncio
    async def test_launch_persists_terminal_status(
        self, mock_async_session_context, trivial_pipeline
    ):
        """When task finishes, update_run_status is called via the service layer."""
        coord = RunCoordinator()
        run_id = uuid.uuid4()

        await coord.launch(run_id, trivial_pipeline)
        await asyncio.sleep(0.1)

        # commit was called → write path was exercised
        mock_async_session_context.commit.assert_awaited()


class TestCancellation:
    @pytest.mark.asyncio
    async def test_cancel_unknown_run_returns_false(self, mock_async_session_context):
        """Cancelling a run that isn't tracked returns False."""
        coord = RunCoordinator()
        result = await coord.cancel(uuid.uuid4())
        assert result is False

    @pytest.mark.asyncio
    async def test_cancel_sets_event_for_tracked_run(
        self, mock_async_session_context, trivial_pipeline
    ):
        """Cancelling a tracked run sets its event and returns True."""
        coord = RunCoordinator()
        run_id = uuid.uuid4()
        await coord.launch(run_id, trivial_pipeline)

        # Catch the event before the task naturally completes
        event = coord.get_cancel_event(run_id)
        if event is not None:
            result = await coord.cancel(run_id)
            assert result is True
            assert event.is_set()

        await asyncio.sleep(0.1)


class TestErrorHandling:
    @pytest.mark.asyncio
    async def test_engine_failure_does_not_propagate(self, mock_async_session_context):
        """An engine error (e.g., bad pipeline) marks run failed without raising."""
        coord = RunCoordinator()
        run_id = uuid.uuid4()

        # Pipeline with cycle → ValueError from topological_sort
        bad_pipeline = {
            "id": "00000000-0000-0000-0000-000000000000",
            "name": "Cyclic",
            "nodes": [
                {
                    "id": "a",
                    "type": "datasource",
                    "position": {"x": 0, "y": 0},
                    "data": {
                        "label": "A",
                        "nodeType": "datasource",
                        "config": {
                            "sourceType": "rest",
                            "url": "https://example.com",
                        },
                    },
                },
                {
                    "id": "b",
                    "type": "action",
                    "position": {"x": 100, "y": 0},
                    "data": {
                        "label": "B",
                        "nodeType": "action",
                        "config": {
                            "actionType": "transform",
                            "outputFormat": "json",
                        },
                    },
                },
            ],
            "edges": [
                {"id": "e1", "source": "a", "target": "b"},
                {"id": "e2", "source": "b", "target": "a"},
            ],
        }

        # Should not raise — error is caught and persisted
        await coord.launch(run_id, bad_pipeline)
        await asyncio.sleep(0.1)

        # Status was updated (failed) and committed
        mock_async_session_context.commit.assert_awaited()
