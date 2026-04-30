"""
Shared test fixtures for the engine test suite.

Provides mocked DB sessions and sample data for run persistence tests.
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.run import PipelineRunModel, StepResultModel


@pytest.fixture
def mock_session():
    """Mocked AsyncSession for DB-dependent tests."""
    session = AsyncMock()

    # execute() returns a mock result
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()

    return session


@pytest.fixture
def sample_run_result():
    """Sample execution result dict matching ExecutionEngine output."""
    return {
        "id": str(uuid.uuid4()),
        "pipeline_id": "pipe-001",
        "pipeline_name": "Test Pipeline",
        "status": "completed",
        "steps": [
            {
                "node_id": "node_1",
                "node_type": "datasource",
                "node_label": "Fetch Data",
                "status": "completed",
                "order": 0,
                "input": None,
                "output": {"data": [1, 2, 3]},
                "started_at": "2025-01-01T00:00:00+00:00",
                "completed_at": "2025-01-01T00:00:01+00:00",
                "duration_ms": 1000,
            },
            {
                "node_id": "node_2",
                "node_type": "ai",
                "node_label": "Process",
                "status": "completed",
                "order": 1,
                "input": {"data": [1, 2, 3]},
                "output": {"result": "processed"},
                "started_at": "2025-01-01T00:00:01+00:00",
                "completed_at": "2025-01-01T00:00:02+00:00",
                "duration_ms": 1000,
                "token_usage": {
                    "input_tokens": 100,
                    "output_tokens": 50,
                    "total_tokens": 150,
                },
                "cost_usd": 0.002,
            },
        ],
        "total_duration_ms": 2000,
        "total_cost_usd": 0.002,
        "started_at": "2025-01-01T00:00:00+00:00",
        "completed_at": "2025-01-01T00:00:02+00:00",
    }


@pytest.fixture
def sample_pipeline_dict():
    """Sample pipeline definition for execution requests."""
    return {
        "id": "pipe-001",
        "name": "Test Pipeline",
        "nodes": [
            {
                "id": "node_1",
                "type": "datasource",
                "position": {"x": 0, "y": 0},
                "data": {
                    "label": "Fetch Data",
                    "nodeType": "datasource",
                    "config": {"source_type": "static", "static_data": "test"},
                },
            },
            {
                "id": "node_2",
                "type": "ai",
                "position": {"x": 200, "y": 0},
                "data": {
                    "label": "Process",
                    "nodeType": "ai",
                    "config": {"prompt": "summarize"},
                },
            },
        ],
        "edges": [{"id": "e1", "source": "node_1", "target": "node_2"}],
    }


@pytest.fixture
def sample_run_model():
    """Sample PipelineRunModel for GET endpoint tests."""
    run = PipelineRunModel(
        id=uuid.UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"),
        pipeline_id="pipe-001",
        pipeline_name="Test Pipeline",
        status="completed",
        started_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
        completed_at=datetime(2025, 1, 1, 0, 0, 2, tzinfo=timezone.utc),
        total_duration_ms=2000,
        total_cost_usd=0.002,
        pipeline_snapshot={"id": "pipe-001", "name": "Test Pipeline"},
    )

    step = StepResultModel(
        id=uuid.uuid4(),
        run_id=run.id,
        node_id="node_1",
        node_type="datasource",
        node_label="Fetch Data",
        status="completed",
        order=0,
        input_data=None,
        output_data={"data": [1, 2, 3]},
        started_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
        completed_at=datetime(2025, 1, 1, 0, 0, 1, tzinfo=timezone.utc),
        duration_ms=1000,
    )

    run.steps = [step]
    return run
