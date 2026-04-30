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
    ConnectorManifest,
    ExecutorResult,
    NodeExecutor,
    StubDataSourceExecutor,
    StubAIExecutor,
    StubActionExecutor,
    StubHumanExecutor,
    get_executor,
    _EXECUTORS,
)


# ── Test Fixtures ─────────────────────────────────────────────────────

# Valid default configs for each node type — used when tests don't
# specify a config. Matches the minimum required by validate_config().
VALID_DEFAULTS = {
    "datasource": {"sourceType": "rest", "url": "https://api.example.com/data"},
    "ai": {"provider": "anthropic", "model": "claude-sonnet-4-20250514", "prompt": "Analyze: {{ input }}"},
    "action": {"actionType": "transform", "outputFormat": "json"},
    "human": {},
}


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
                    "config": n.get("config", VALID_DEFAULTS.get(n["type"], {})),
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

    def test_cycle_raises_value_error(self):
        """A → B → A is a cycle — should raise ValueError, not silently drop nodes."""
        nodes = [
            {"id": "a", "type": "datasource"},
            {"id": "b", "type": "ai"},
        ]
        edges = [("a", "b"), ("b", "a")]
        pipeline = make_pipeline(nodes, edges)

        with pytest.raises(ValueError, match="cycle"):
            topological_sort(pipeline["nodes"], pipeline["edges"])

    def test_self_loop_raises_value_error(self):
        """A → A is a cycle — should raise ValueError."""
        nodes = [{"id": "a", "type": "datasource"}]
        edges = [("a", "a")]
        pipeline = make_pipeline(nodes, edges)

        with pytest.raises(ValueError, match="cycle"):
            topological_sort(pipeline["nodes"], pipeline["edges"])

    def test_orphan_edge_source_raises_value_error(self):
        """Edge from non-existent source should raise ValueError."""
        nodes = [{"id": "a", "type": "datasource"}]
        edges = [("ghost", "a")]
        pipeline = make_pipeline(nodes, edges)
        # Manually inject the invalid edge (make_pipeline creates valid edges)
        pipeline["edges"] = [{"id": "e-ghost-a", "source": "ghost", "target": "a"}]

        with pytest.raises(ValueError, match="ghost"):
            topological_sort(pipeline["nodes"], pipeline["edges"])

    def test_orphan_edge_target_raises_value_error(self):
        """Edge to non-existent target should raise ValueError."""
        nodes = [{"id": "a", "type": "datasource"}]
        pipeline = make_pipeline(nodes, [])
        pipeline["edges"] = [{"id": "e-a-ghost", "source": "a", "target": "ghost"}]

        with pytest.raises(ValueError, match="ghost"):
            topological_sort(pipeline["nodes"], pipeline["edges"])


# ── Stub Executor Tests ───────────────────────────────────────────────


class TestStubExecutors:
    """Stub executors return predictable dummy data for US2."""

    def test_datasource_executor(self):
        result = StubDataSourceExecutor().execute(
            config={"sourceType": "rest", "url": "https://api.example.com"},
            input_data=None,
        )
        assert isinstance(result, ExecutorResult)
        assert "data" in result.output
        assert isinstance(result.output["data"], list)

    def test_ai_executor(self):
        result = StubAIExecutor().execute(
            config={"provider": "anthropic", "prompt": "Analyze this"},
            input_data={"data": [1, 2, 3]},
        )
        assert isinstance(result, ExecutorResult)
        assert "analysis" in result.output
        assert result.token_usage is not None
        assert result.token_usage["total_tokens"] > 0
        assert result.cost_usd is not None

    def test_action_executor(self):
        result = StubActionExecutor().execute(
            config={"actionType": "transform", "outputFormat": "json"},
            input_data={"analysis": "test"},
        )
        assert isinstance(result, ExecutorResult)
        assert "output" in result.output
        assert result.output["format"] == "json"

    def test_human_executor(self):
        result = StubHumanExecutor().execute(
            config={"instructions": "Review this", "requireComment": False},
            input_data={"data": "test"},
        )
        assert isinstance(result, ExecutorResult)
        assert result.output["approved"] is True
        assert result.output["decision"] == "auto-approved"

    def test_manifest_returns_metadata(self):
        """Each executor should provide a ConnectorManifest."""
        for executor_cls in [
            StubDataSourceExecutor,
            StubAIExecutor,
            StubActionExecutor,
            StubHumanExecutor,
        ]:
            manifest = executor_cls.manifest()
            assert isinstance(manifest, ConnectorManifest)
            assert manifest.name
            assert manifest.node_type

    def test_validate_config_catches_missing_required(self):
        """validate_config should report missing required fields."""
        executor = StubAIExecutor()
        errors = executor.validate_config({})
        field_names = [e.field for e in errors]
        assert "provider" in field_names
        assert "model" in field_names
        assert "prompt" in field_names

    def test_validate_config_passes_with_required_fields(self):
        """validate_config should return empty list when all required fields present."""
        executor = StubAIExecutor()
        errors = executor.validate_config(
            {
                "provider": "anthropic",
                "model": "claude-sonnet-4-20250514",
                "prompt": "test",
            }
        )
        assert errors == []

    # ── Enhanced validation (type/range/format checks) ─────────────

    def test_datasource_validates_url_required_for_rest(self):
        """REST source type requires a non-empty URL."""
        executor = StubDataSourceExecutor()
        errors = executor.validate_config({"sourceType": "rest", "url": ""})
        field_names = [e.field for e in errors]
        assert "url" in field_names

    def test_datasource_validates_url_required_for_sql(self):
        """SQL source type requires a non-empty connection string."""
        executor = StubDataSourceExecutor()
        errors = executor.validate_config({"sourceType": "sql", "url": ""})
        field_names = [e.field for e in errors]
        assert "url" in field_names

    def test_datasource_accepts_file_without_url(self):
        """File source type does not require URL."""
        executor = StubDataSourceExecutor()
        errors = executor.validate_config({"sourceType": "file"})
        assert errors == []

    def test_datasource_rejects_invalid_source_type(self):
        """sourceType must be one of rest/sql/file."""
        executor = StubDataSourceExecutor()
        errors = executor.validate_config({"sourceType": "ftp"})
        field_names = [e.field for e in errors]
        assert "sourceType" in field_names

    def test_ai_validates_temperature_range(self):
        """Temperature must be between 0 and 2."""
        executor = StubAIExecutor()
        config = {"provider": "anthropic", "model": "claude-sonnet-4-20250514", "prompt": "test"}

        # Too high
        errors = executor.validate_config({**config, "temperature": 3.0})
        assert any(e.field == "temperature" for e in errors)

        # Too low
        errors = executor.validate_config({**config, "temperature": -1.0})
        assert any(e.field == "temperature" for e in errors)

        # Valid boundary
        errors = executor.validate_config({**config, "temperature": 0.0})
        assert not any(e.field == "temperature" for e in errors)

    def test_ai_validates_max_tokens_range(self):
        """maxTokens must be 1-100000."""
        executor = StubAIExecutor()
        config = {"provider": "anthropic", "model": "claude-sonnet-4-20250514", "prompt": "test"}

        errors = executor.validate_config({**config, "maxTokens": 0})
        assert any(e.field == "maxTokens" for e in errors)

        errors = executor.validate_config({**config, "maxTokens": 200000})
        assert any(e.field == "maxTokens" for e in errors)

    def test_ai_validates_provider_enum(self):
        """Provider must be anthropic or openai."""
        executor = StubAIExecutor()
        errors = executor.validate_config({
            "provider": "google",
            "model": "gemini",
            "prompt": "test",
        })
        assert any(e.field == "provider" for e in errors)

    def test_action_validates_enums(self):
        """actionType and outputFormat must be valid enum values."""
        executor = StubActionExecutor()

        errors = executor.validate_config({"actionType": "delete"})
        assert any(e.field == "actionType" for e in errors)

        errors = executor.validate_config({"actionType": "transform", "outputFormat": "xml"})
        assert any(e.field == "outputFormat" for e in errors)

    def test_action_accepts_valid_config(self):
        executor = StubActionExecutor()
        errors = executor.validate_config({"actionType": "transform", "outputFormat": "json"})
        assert errors == []

    def test_human_accepts_empty_config(self):
        """Human step has no required fields."""
        executor = StubHumanExecutor()
        errors = executor.validate_config({})
        assert errors == []

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
            @classmethod
            def manifest(cls) -> ConnectorManifest:
                return ConnectorManifest(
                    name="Failing", description="Test", node_type="ai"
                )

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

    def test_execute_preflight_catches_invalid_config(self):
        """Engine should validate all configs before executing any step."""
        from app.core.errors import PipelineError, ErrorCode

        pipeline = make_pipeline(
            nodes=[
                {"id": "src", "type": "datasource", "config": {"sourceType": "rest", "url": ""}},
                {"id": "analyze", "type": "ai", "config": {"provider": "anthropic", "model": "", "prompt": ""}},
            ],
            edges=[("src", "analyze")],
        )

        engine = ExecutionEngine()
        with pytest.raises(PipelineError) as exc_info:
            engine.execute(pipeline)

        assert exc_info.value.code == ErrorCode.VALIDATION_ERROR
        # Should contain details about which nodes/fields failed
        assert exc_info.value.details is not None
        assert len(exc_info.value.details.get("validation_errors", [])) > 0

    def test_execute_preflight_passes_with_valid_config(self):
        """Valid configs should not trigger preflight errors."""
        pipeline = make_pipeline(
            nodes=[
                {"id": "src", "type": "datasource", "config": {"sourceType": "rest", "url": "https://example.com"}},
                {"id": "out", "type": "action", "config": {"actionType": "transform", "outputFormat": "json"}},
            ],
            edges=[("src", "out")],
        )

        engine = ExecutionEngine()
        run = engine.execute(pipeline)
        assert run["status"] == "completed"
