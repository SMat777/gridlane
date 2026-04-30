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
from app.services.executors import NodeExecutor, _EXECUTORS


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


def make_run_request(nodes, edges):
    """Helper to build a run request body."""
    return {
        "pipeline": {
            "id": "test-pipeline-123",
            "name": "Test Pipeline",
            "nodes": [
                {
                    "id": n["id"],
                    "type": n["type"],
                    "position": {"x": 0, "y": 0},
                    "data": {
                        "label": n.get("label", n["type"].title()),
                        "nodeType": n["type"],
                        "config": n.get("config", {}),
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
        assert run["pipeline_id"] == "test-pipeline-123"
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
            def execute(self, config, input_data):
                time.sleep(5)
                return {"data": "should not reach here"}

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
            assert "timeout" in data["detail"].lower()
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
        """Returns 404 for non-existent run ID."""
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/v1/runs/{fake_id}")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_run_returns_422_for_invalid_uuid(self):
        """Returns 422 for malformed UUID."""
        response = client.get("/api/v1/runs/not-a-uuid")

        assert response.status_code == 422
