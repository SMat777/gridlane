"""
Tests for pipeline run API endpoints.

Uses FastAPI TestClient — no real database or external services needed.
"""

from fastapi.testclient import TestClient

from app.main import app

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
