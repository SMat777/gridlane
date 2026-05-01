"""
Tests for pipeline run API endpoints.

Uses FastAPI TestClient with mocked DB session — no real database needed.
"""

import time
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app
from app.services.executors import (
    ConnectorManifest,
    ExecutorResult,
    NodeExecutor,
    _EXECUTORS,
)


async def mock_get_db():
    """Override DB dependency with a mock that accepts writes but returns nothing."""
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    # For GET queries — return empty by default
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = []
    mock_scalars.first.return_value = None
    mock_result.scalars.return_value = mock_scalars
    session.execute = AsyncMock(return_value=mock_result)

    yield session


app.dependency_overrides[get_db] = mock_get_db
client = TestClient(app)


TEST_PIPELINE_ID = "22222222-2222-2222-2222-222222222222"

# Valid default configs for each node type — used when tests don't
# specify a config. Matches the minimum required by validate_config().
VALID_DEFAULTS = {
    # Use sql so the API tests don't accidentally fire HTTP requests via
    # the real REST executor. REST is covered separately with mocks.
    "datasource": {"sourceType": "sql", "url": "postgresql://localhost/test"},
    "ai": {
        "provider": "anthropic",
        "model": "claude-sonnet-4-20250514",
        "prompt": "Analyze: {{ input }}",
    },
    "action": {"actionType": "transform", "outputFormat": "json"},
    "human": {},
}


def make_run_request(nodes, edges):
    """Helper to build a run request body."""
    return {
        "pipeline": {
            "id": TEST_PIPELINE_ID,
            "name": "Test Pipeline",
            "nodes": [
                {
                    "id": n["id"],
                    "type": n["type"],
                    "position": {"x": 0, "y": 0},
                    "data": {
                        "label": n.get("label", n["type"].title()),
                        "nodeType": n["type"],
                        "config": n.get("config", VALID_DEFAULTS.get(n["type"], {})),
                    },
                }
                for n in nodes
            ],
            "edges": [
                {"id": f"e-{e[0]}-{e[1]}", "source": e[0], "target": e[1]}
                for e in edges
            ],
        }
    }


class TestRunPipelineEndpoint:
    """POST /api/v1/runs — execute a pipeline."""

    def test_run_simple_pipeline(self):
        """Run a datasource → ai → action pipeline."""
        body = make_run_request(
            nodes=[
                {"id": "src", "type": "datasource"},
                {"id": "ai", "type": "ai"},
                {"id": "out", "type": "action"},
            ],
            edges=[("src", "ai"), ("ai", "out")],
        )

        response = client.post("/api/v1/runs", json=body)

        assert response.status_code == 200
        data = response.json()
        run = data["run"]

        assert run["status"] == "completed"
        assert run["pipeline_id"] == TEST_PIPELINE_ID
        assert run["pipeline_name"] == "Test Pipeline"
        assert len(run["steps"]) == 3
        assert run["total_duration_ms"] >= 0

    def test_run_returns_step_details(self):
        """Each step has the expected fields."""
        body = make_run_request(
            nodes=[{"id": "src", "type": "datasource"}],
            edges=[],
        )

        response = client.post("/api/v1/runs", json=body)

        data = response.json()
        step = data["run"]["steps"][0]

        assert step["node_id"] == "src"
        assert step["node_type"] == "datasource"
        assert step["status"] == "completed"
        assert step["order"] == 0
        assert "started_at" in step
        assert "completed_at" in step
        assert "duration_ms" in step
        assert step["output"] is not None

    def test_run_ai_step_includes_metrics(self):
        """AI steps include token usage and cost."""
        body = make_run_request(
            nodes=[
                {"id": "src", "type": "datasource"},
                {"id": "ai", "type": "ai"},
            ],
            edges=[("src", "ai")],
        )

        response = client.post("/api/v1/runs", json=body)

        data = response.json()
        ai_step = data["run"]["steps"][1]

        assert ai_step["token_usage"] is not None
        assert ai_step["token_usage"]["total_tokens"] > 0
        assert ai_step["cost_usd"] is not None

    def test_run_empty_pipeline(self):
        """Empty pipeline returns completed with no steps."""
        body = make_run_request(nodes=[], edges=[])

        response = client.post("/api/v1/runs", json=body)

        data = response.json()
        assert data["run"]["status"] == "completed"
        assert data["run"]["steps"] == []

    def test_run_invalid_request_returns_422(self):
        """Missing required fields returns validation error."""
        response = client.post("/api/v1/runs", json={})
        assert response.status_code == 422

    def test_run_returns_unique_run_id(self):
        """Each run gets a unique ID."""
        body = make_run_request(
            nodes=[{"id": "src", "type": "datasource"}],
            edges=[],
        )

        r1 = client.post("/api/v1/runs", json=body).json()
        r2 = client.post("/api/v1/runs", json=body).json()

        assert r1["run"]["id"] != r2["run"]["id"]

    def test_run_rejects_too_many_nodes(self):
        """Pipeline with more than 100 nodes is rejected."""
        oversized_nodes = [{"id": f"n{i}", "type": "datasource"} for i in range(101)]
        body = make_run_request(nodes=oversized_nodes, edges=[])

        response = client.post("/api/v1/runs", json=body)
        assert response.status_code == 422

    def test_run_rejects_too_many_edges(self):
        """Pipeline with more than 500 edges is rejected."""
        nodes = [{"id": "a", "type": "datasource"}, {"id": "b", "type": "ai"}]
        oversized_edges = [("a", "b")] * 501
        body = make_run_request(nodes=nodes, edges=oversized_edges)

        response = client.post("/api/v1/runs", json=body)
        assert response.status_code == 422

    def test_run_rejects_oversized_node_label(self):
        """Node label longer than 200 chars is rejected."""
        body = make_run_request(
            nodes=[{"id": "n1", "type": "datasource", "label": "x" * 201}],
            edges=[],
        )

        response = client.post("/api/v1/runs", json=body)
        assert response.status_code == 422

    def test_run_timeout_returns_504(self):
        """Pipeline exceeding timeout returns 504 Gateway Timeout."""

        class SlowExecutor(NodeExecutor):
            @classmethod
            def manifest(cls) -> ConnectorManifest:
                return ConnectorManifest(
                    name="Slow", description="Test", node_type="datasource"
                )

            def execute(self, config, input_data):
                time.sleep(5)
                return ExecutorResult(output={"data": "should not reach here"})

        original = _EXECUTORS["datasource"]
        _EXECUTORS["datasource"] = SlowExecutor
        try:
            body = make_run_request(
                nodes=[{"id": "src", "type": "datasource"}],
                edges=[],
            )

            # Use a very short timeout for testing
            with patch("app.api.v1.endpoints.runs.EXECUTION_TIMEOUT_SECONDS", 0.1):
                response = client.post("/api/v1/runs", json=body)

            assert response.status_code == 504
            data = response.json()
            assert data["error"]["code"] == "EXECUTION_TIMEOUT"
            assert "timed out" in data["error"]["message"].lower()
        finally:
            _EXECUTORS["datasource"] = original


class TestListRunsEndpoint:
    """GET /api/v1/runs — list run history."""

    def test_list_runs_returns_empty(self):
        """Returns empty list when no runs exist."""
        response = client.get("/api/v1/runs")

        assert response.status_code == 200
        data = response.json()
        assert data["runs"] == []

    def test_list_runs_accepts_pipeline_filter(self):
        """Accepts pipeline_id query parameter."""
        response = client.get("/api/v1/runs?pipeline_id=pipe-001")

        assert response.status_code == 200
        assert "runs" in response.json()

    def test_list_runs_accepts_pagination(self):
        """Accepts limit and offset query parameters."""
        response = client.get("/api/v1/runs?limit=10&offset=0")

        assert response.status_code == 200
        assert "runs" in response.json()


class TestGetRunEndpoint:
    """GET /api/v1/runs/{run_id} — get a single run."""

    def test_get_run_returns_404_when_not_found(self):
        """Returns 404 for non-existent run ID with structured error."""
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/v1/runs/{fake_id}")

        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "NOT_FOUND"
        assert "not found" in data["error"]["message"].lower()

    def test_get_run_returns_422_for_invalid_uuid(self):
        """Returns 422 for malformed UUID."""
        response = client.get("/api/v1/runs/not-a-uuid")

        assert response.status_code == 422


class TestAsyncLaunchEndpoint:
    """POST /api/v1/runs/async — launch a run in the background."""

    def test_returns_202_with_run_id(self):
        """Async launch returns 202 + run_id immediately."""
        body = make_run_request(
            nodes=[{"id": "a", "type": "datasource"}],
            edges=[],
        )
        with patch(
            "app.api.v1.endpoints.runs.coordinator.launch", new=AsyncMock()
        ) as mock_launch:
            response = client.post("/api/v1/runs/async", json=body)

        assert response.status_code == 202
        data = response.json()
        assert "run_id" in data
        assert data["status"] == "running"
        assert data["stream_url"].startswith("/api/v1/runs/")
        assert data["stream_url"].endswith("/stream")
        # Coordinator was asked to launch the run
        mock_launch.assert_awaited_once()

    def test_returns_uuid_format(self):
        """run_id should be a valid UUID string."""
        body = make_run_request(
            nodes=[{"id": "a", "type": "datasource"}],
            edges=[],
        )
        with patch("app.api.v1.endpoints.runs.coordinator.launch", new=AsyncMock()):
            response = client.post("/api/v1/runs/async", json=body)

        # Will raise if not valid UUID
        uuid.UUID(response.json()["run_id"])


class TestCancelRunEndpoint:
    """POST /api/v1/runs/{run_id}/cancel — request cancellation."""

    def test_cancel_returns_cancelling_for_running_run(self):
        """When the run is running, cancel returns status=cancelling."""
        run_id = uuid.uuid4()

        with (
            patch(
                "app.api.v1.endpoints.runs.RunService.set_cancel_requested",
                new=AsyncMock(return_value="cancelling"),
            ),
            patch(
                "app.api.v1.endpoints.runs.coordinator.cancel", new=AsyncMock()
            ) as mock_cancel,
        ):
            response = client.post(f"/api/v1/runs/{run_id}/cancel")

        assert response.status_code == 200
        assert response.json() == {
            "run_id": str(run_id),
            "status": "cancelling",
        }
        mock_cancel.assert_awaited_once()

    def test_cancel_returns_existing_status_when_already_terminal(self):
        """Cancelling a finished run returns its current status (no-op)."""
        run_id = uuid.uuid4()

        with (
            patch(
                "app.api.v1.endpoints.runs.RunService.set_cancel_requested",
                new=AsyncMock(return_value="completed"),
            ),
            patch("app.api.v1.endpoints.runs.coordinator.cancel", new=AsyncMock()),
        ):
            response = client.post(f"/api/v1/runs/{run_id}/cancel")

        assert response.status_code == 200
        assert response.json()["status"] == "completed"

    def test_cancel_returns_404_for_unknown_run(self):
        """Cancelling a non-existent run returns 404 with structured error."""
        run_id = uuid.uuid4()

        with patch(
            "app.api.v1.endpoints.runs.RunService.set_cancel_requested",
            new=AsyncMock(return_value=None),
        ):
            response = client.post(f"/api/v1/runs/{run_id}/cancel")

        assert response.status_code == 404
        assert response.json()["error"]["code"] == "NOT_FOUND"

    def test_cancel_rejects_invalid_uuid(self):
        """Path validation rejects non-UUID run_id."""
        response = client.post("/api/v1/runs/not-a-uuid/cancel")
        assert response.status_code == 422


class TestStreamEndpoint:
    """GET /api/v1/runs/{run_id}/stream — SSE event stream."""

    def test_stream_returns_404_for_unknown_run(self):
        """When the run doesn't exist anywhere, return 404 (not an SSE 200)."""
        # Default mock returns None for get_run (no run_model), and bus has no channel
        run_id = uuid.uuid4()
        response = client.get(f"/api/v1/runs/{run_id}/stream")
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "NOT_FOUND"

    def test_stream_replays_finished_run_from_db(self):
        """If a run already finished, replay events from the DB and close."""
        run_id = uuid.uuid4()

        # Mock run exists
        mock_run = MagicMock()
        mock_run.id = run_id

        # Mock events to replay
        mock_event_1 = MagicMock()
        mock_event_1.sequence = 0
        mock_event_1.event_type = "run_started"
        mock_event_1.payload = {"total_steps": 1}

        mock_event_2 = MagicMock()
        mock_event_2.sequence = 1
        mock_event_2.event_type = "run_completed"
        mock_event_2.payload = {"status": "completed"}

        with (
            patch(
                "app.api.v1.endpoints.runs.RunService.get_run",
                new=AsyncMock(return_value=mock_run),
            ),
            patch(
                "app.api.v1.endpoints.runs.RunService.list_events_after",
                new=AsyncMock(return_value=[mock_event_1, mock_event_2]),
            ),
            patch(
                "app.api.v1.endpoints.runs.bus.get_channel",
                return_value=None,
            ),
        ):
            response = client.get(f"/api/v1/runs/{run_id}/stream")

        # SSE response is 200 + text/event-stream
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        body = response.text
        # Both events present in stream
        assert "event: run_started" in body
        assert "event: run_completed" in body
        assert "id: 0" in body
        assert "id: 1" in body

    def test_stream_respects_last_event_id_header(self):
        """Last-Event-ID skips events with sequence <= the header value."""
        run_id = uuid.uuid4()

        mock_run = MagicMock()
        mock_event_2 = MagicMock()
        mock_event_2.sequence = 2
        mock_event_2.event_type = "run_completed"
        mock_event_2.payload = {"status": "completed"}

        list_events_mock = AsyncMock(return_value=[mock_event_2])

        with (
            patch(
                "app.api.v1.endpoints.runs.RunService.get_run",
                new=AsyncMock(return_value=mock_run),
            ),
            patch(
                "app.api.v1.endpoints.runs.RunService.list_events_after",
                new=list_events_mock,
            ),
            patch(
                "app.api.v1.endpoints.runs.bus.get_channel",
                return_value=None,
            ),
        ):
            response = client.get(
                f"/api/v1/runs/{run_id}/stream",
                headers={"Last-Event-ID": "1"},
            )

        # list_events_after was called with after_sequence=1 (parsed from header)
        call_kwargs = list_events_mock.call_args.kwargs
        assert call_kwargs.get("after_sequence") == 1
        assert response.status_code == 200


class TestParseLastEventId:
    """Unit tests for the Last-Event-ID parser cap."""

    def test_returns_minus_one_for_missing_or_blank(self):
        from app.api.v1.endpoints.runs import _parse_last_event_id

        assert _parse_last_event_id(None) == -1
        assert _parse_last_event_id("") == -1

    def test_returns_minus_one_for_non_integer(self):
        from app.api.v1.endpoints.runs import _parse_last_event_id

        assert _parse_last_event_id("abc") == -1
        assert _parse_last_event_id("1.5") == -1

    def test_accepts_in_range_integers(self):
        from app.api.v1.endpoints.runs import _parse_last_event_id

        assert _parse_last_event_id("0") == 0
        assert _parse_last_event_id("42") == 42
        assert _parse_last_event_id("100000") == 100_000

    def test_caps_unreasonable_values(self):
        from app.api.v1.endpoints.runs import _parse_last_event_id

        # Above MAX_LAST_EVENT_ID — fall back to -1 instead of trusting the value
        assert _parse_last_event_id("100001") == -1
        assert _parse_last_event_id("99999999999999999") == -1
        assert _parse_last_event_id("-2") == -1
