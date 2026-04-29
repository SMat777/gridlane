"""
Tests for pipeline execution engine.

Pure unit tests — no database, no HTTP. Tests the execution logic
in isolation: topological sort, step execution, stub executors.
"""

import pytest

from app.services.execution import (
    ExecutionEngine,
    topological_sort,
)
from app.services.executors import (
    NodeExecutor,
    StubDataSourceExecutor,
    StubAIExecutor,
    StubActionExecutor,
    StubHumanExecutor,
    get_executor,
    _EXECUTORS,
)


# ── Test Fixtures ─────────────────────────────────────────────────────


def make_pipeline(nodes, edges):
    """Helper to build a pipeline definition dict."""
    return {
        "id": "test-pipeline",
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
            {"id": f"e-{e[0]}-{e[1]}", "source": e[0], "target": e[1]} for e in edges
        ],
    }


# ── Topological Sort Tests ────────────────────────────────────────────


class TestTopologicalSort:
    """Topological sort determines execution order from DAG structure."""

    def test_linear_chain(self):
        """A → B → C should execute in order A, B, C."""
        nodes = [
            {"id": "a", "type": "datasource"},
            {"id": "b", "type": "ai"},
            {"id": "c", "type": "action"},
        ]
        edges = [("a", "b"), ("b", "c")]
        pipeline = make_pipeline(nodes, edges)

        order = topological_sort(pipeline["nodes"], pipeline["edges"])
        ids = [n["id"] for n in order]

        assert ids == ["a", "b", "c"]

    def test_single_node(self):
        """Single node with no edges."""
        nodes = [{"id": "a", "type": "datasource"}]
        pipeline = make_pipeline(nodes, [])

        order = topological_sort(pipeline["nodes"], pipeline["edges"])
        assert len(order) == 1
        assert order[0]["id"] == "a"

    def test_diamond_shape(self):
        """Diamond: A → B, A → C, B → D, C → D.
        A must come first, D must come last. B and C can be either order."""
        nodes = [
            {"id": "a", "type": "datasource"},
            {"id": "b", "type": "ai"},
            {"id": "c", "type": "action"},
            {"id": "d", "type": "action"},
        ]
        edges = [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")]
        pipeline = make_pipeline(nodes, edges)

        order = topological_sort(pipeline["nodes"], pipeline["edges"])
        ids = [n["id"] for n in order]

        assert ids[0] == "a"
        assert ids[-1] == "d"
        assert set(ids[1:3]) == {"b", "c"}

    def test_empty_pipeline_returns_empty(self):
        """No nodes → empty order."""
        order = topological_sort([], [])
        assert order == []


# ── Stub Executor Tests ───────────────────────────────────────────────


class TestStubExecutors:
    """Stub executors return predictable dummy data for US2."""

    def test_datasource_executor(self):
        result = StubDataSourceExecutor().execute(
            config={"sourceType": "rest", "url": "https://api.example.com"},
            input_data=None,
        )
        assert "data" in result
        assert isinstance(result["data"], list)

    def test_ai_executor(self):
        result = StubAIExecutor().execute(
            config={"provider": "anthropic", "prompt": "Analyze this"},
            input_data={"data": [1, 2, 3]},
        )
        assert "analysis" in result
        assert "token_usage" in result
        assert result["token_usage"]["total_tokens"] > 0

    def test_action_executor(self):
        result = StubActionExecutor().execute(
            config={"actionType": "transform", "outputFormat": "json"},
            input_data={"analysis": "test"},
        )
        assert "output" in result
        assert result["format"] == "json"

    def test_human_executor(self):
        result = StubHumanExecutor().execute(
            config={"instructions": "Review this", "requireComment": False},
            input_data={"data": "test"},
        )
        assert result["approved"] is True
        assert result["decision"] == "auto-approved"

    def test_get_executor_returns_correct_type(self):
        assert isinstance(get_executor("datasource"), StubDataSourceExecutor)
        assert isinstance(get_executor("ai"), StubAIExecutor)
        assert isinstance(get_executor("action"), StubActionExecutor)
        assert isinstance(get_executor("human"), StubHumanExecutor)

    def test_get_executor_unknown_type_raises(self):
        with pytest.raises(ValueError, match="Unknown node type"):
            get_executor("nonexistent")


# ── Execution Engine Tests ────────────────────────────────────────────


class TestExecutionEngine:
    """Integration tests for the full execution pipeline (in-memory, no DB)."""

    def test_execute_linear_pipeline(self):
        """Run a simple datasource → ai → action pipeline."""
        pipeline = make_pipeline(
            nodes=[
                {"id": "src", "type": "datasource", "label": "API Source"},
                {"id": "analyze", "type": "ai", "label": "Analyzer"},
                {"id": "out", "type": "action", "label": "Output"},
            ],
            edges=[("src", "analyze"), ("analyze", "out")],
        )

        engine = ExecutionEngine()
        run = engine.execute(pipeline)

        assert run["status"] == "completed"
        assert len(run["steps"]) == 3
        assert run["steps"][0]["node_id"] == "src"
        assert run["steps"][0]["status"] == "completed"
        assert run["steps"][1]["node_id"] == "analyze"
        assert run["steps"][2]["node_id"] == "out"
        assert run["total_duration_ms"] >= 0

    def test_execute_passes_output_to_next_step(self):
        """Output of step N becomes input of step N+1."""
        pipeline = make_pipeline(
            nodes=[
                {"id": "src", "type": "datasource"},
                {"id": "ai", "type": "ai"},
            ],
            edges=[("src", "ai")],
        )

        engine = ExecutionEngine()
        run = engine.execute(pipeline)

        # AI step should have received datasource output as input
        assert run["steps"][1]["input"] is not None

    def test_execute_single_node(self):
        """A pipeline with just one node should still work."""
        pipeline = make_pipeline(
            nodes=[{"id": "src", "type": "datasource"}],
            edges=[],
        )

        engine = ExecutionEngine()
        run = engine.execute(pipeline)

        assert run["status"] == "completed"
        assert len(run["steps"]) == 1

    def test_execute_records_timing(self):
        """Each step should have timing information."""
        pipeline = make_pipeline(
            nodes=[
                {"id": "src", "type": "datasource"},
                {"id": "ai", "type": "ai"},
            ],
            edges=[("src", "ai")],
        )

        engine = ExecutionEngine()
        run = engine.execute(pipeline)

        for step in run["steps"]:
            assert "started_at" in step
            assert "completed_at" in step
            assert "duration_ms" in step
            assert step["duration_ms"] >= 0

    def test_execute_includes_pipeline_metadata(self):
        """Run result includes pipeline ID and name."""
        pipeline = make_pipeline(
            nodes=[{"id": "src", "type": "datasource"}],
            edges=[],
        )
        pipeline["id"] = "my-pipeline-id"
        pipeline["name"] = "My Test Pipeline"

        engine = ExecutionEngine()
        run = engine.execute(pipeline)

        assert run["pipeline_id"] == "my-pipeline-id"
        assert run["pipeline_name"] == "My Test Pipeline"

    def test_execute_empty_pipeline(self):
        """Empty pipeline should return completed with no steps."""
        pipeline = make_pipeline(nodes=[], edges=[])

        engine = ExecutionEngine()
        run = engine.execute(pipeline)

        assert run["status"] == "completed"
        assert run["steps"] == []

    def test_execute_step_failure_cancels_remaining(self):
        """When a step fails, remaining steps are marked cancelled."""

        class FailingExecutor(NodeExecutor):
            def execute(self, config, input_data):
                raise RuntimeError("Connection refused")

        # Temporarily register a failing executor
        original = _EXECUTORS["ai"]
        _EXECUTORS["ai"] = FailingExecutor
        try:
            pipeline = make_pipeline(
                nodes=[
                    {"id": "src", "type": "datasource"},
                    {"id": "fail", "type": "ai"},
                    {"id": "out", "type": "action"},
                ],
                edges=[("src", "fail"), ("fail", "out")],
            )

            engine = ExecutionEngine()
            run = engine.execute(pipeline)

            assert run["status"] == "failed"
            assert run["steps"][0]["status"] == "completed"  # src ran fine
            assert run["steps"][1]["status"] == "failed"  # ai failed
            assert run["steps"][1]["error"] == "Connection refused"
            assert run["steps"][2]["status"] == "cancelled"  # action never ran
        finally:
            _EXECUTORS["ai"] = original
