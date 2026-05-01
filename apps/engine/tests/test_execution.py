"""
Tests for pipeline execution engine.

Pure unit tests — no database, no HTTP. Tests the execution logic
in isolation: topological sort, step execution, stub executors.
"""

import asyncio

import pytest

from app.services.execution import (
    ExecutionEngine,
    topological_sort,
)
from app.services.executors import (
    ConnectorManifest,
    ExecutorResult,
    NodeExecutor,
    DataSourceExecutor,
    StubAIExecutor,
    StubActionExecutor,
    StubHumanExecutor,
    get_executor,
    _EXECUTORS,
)


# ── Test Fixtures ─────────────────────────────────────────────────────

# Valid default configs for each node type — used when tests don't
# specify a config. Matches the minimum required by validate_config().
# Tests use sourceType="sql" by default so the datasource executor stays on
# the stub-data branch and no real HTTP call is made. REST behavior is
# covered by TestRestConnector below with mocked httpx transports.
VALID_DEFAULTS = {
    "datasource": {"sourceType": "sql", "url": "postgresql://localhost/test"},
    "ai": {
        "provider": "anthropic",
        "model": "claude-sonnet-4-20250514",
        "prompt": "Analyze: {{ input }}",
    },
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

    def test_datasource_executor_sql_uses_stub(self):
        # SQL/file branch still returns sample data while those connectors
        # are unimplemented. REST goes through TestRestConnector below.
        result = DataSourceExecutor().execute(
            config={"sourceType": "sql", "url": "postgresql://localhost/db"},
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
            DataSourceExecutor,
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
        executor = DataSourceExecutor()
        errors = executor.validate_config({"sourceType": "rest", "url": ""})
        field_names = [e.field for e in errors]
        assert "url" in field_names

    def test_datasource_validates_url_required_for_sql(self):
        """SQL source type requires a non-empty connection string."""
        executor = DataSourceExecutor()
        errors = executor.validate_config({"sourceType": "sql", "url": ""})
        field_names = [e.field for e in errors]
        assert "url" in field_names

    def test_datasource_accepts_file_without_url(self):
        """File source type does not require URL."""
        executor = DataSourceExecutor()
        errors = executor.validate_config({"sourceType": "file"})
        assert errors == []

    def test_datasource_rejects_invalid_source_type(self):
        """sourceType must be one of rest/sql/file."""
        executor = DataSourceExecutor()
        errors = executor.validate_config({"sourceType": "ftp"})
        field_names = [e.field for e in errors]
        assert "sourceType" in field_names

    def test_ai_validates_temperature_range(self):
        """Temperature must be between 0 and 2."""
        executor = StubAIExecutor()
        config = {
            "provider": "anthropic",
            "model": "claude-sonnet-4-20250514",
            "prompt": "test",
        }

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
        config = {
            "provider": "anthropic",
            "model": "claude-sonnet-4-20250514",
            "prompt": "test",
        }

        errors = executor.validate_config({**config, "maxTokens": 0})
        assert any(e.field == "maxTokens" for e in errors)

        errors = executor.validate_config({**config, "maxTokens": 200000})
        assert any(e.field == "maxTokens" for e in errors)

    def test_ai_validates_provider_enum(self):
        """Provider must be anthropic or openai."""
        executor = StubAIExecutor()
        errors = executor.validate_config(
            {
                "provider": "google",
                "model": "gemini",
                "prompt": "test",
            }
        )
        assert any(e.field == "provider" for e in errors)

    def test_action_validates_enums(self):
        """actionType and outputFormat must be valid enum values."""
        executor = StubActionExecutor()

        errors = executor.validate_config({"actionType": "delete"})
        assert any(e.field == "actionType" for e in errors)

        errors = executor.validate_config(
            {"actionType": "transform", "outputFormat": "xml"}
        )
        assert any(e.field == "outputFormat" for e in errors)

    def test_action_accepts_valid_config(self):
        executor = StubActionExecutor()
        errors = executor.validate_config(
            {"actionType": "transform", "outputFormat": "json"}
        )
        assert errors == []

    def test_human_accepts_empty_config(self):
        """Human step has no required fields."""
        executor = StubHumanExecutor()
        errors = executor.validate_config({})
        assert errors == []

    def test_get_executor_returns_correct_type(self):
        assert isinstance(get_executor("datasource"), DataSourceExecutor)
        assert isinstance(get_executor("ai"), StubAIExecutor)
        assert isinstance(get_executor("action"), StubActionExecutor)
        assert isinstance(get_executor("human"), StubHumanExecutor)

    def test_get_executor_unknown_type_raises(self):
        with pytest.raises(ValueError, match="Unknown node type"):
            get_executor("nonexistent")


# ── REST Connector ────────────────────────────────────────────────────


class TestRestConnector:
    """REST execution path on DataSourceExecutor.

    Uses httpx.MockTransport so no network calls actually happen — the
    transport intercepts requests and returns canned responses.
    """

    @staticmethod
    def _executor_with_transport(handler):
        """Patch httpx.Client to use a MockTransport for one execute() call."""
        import httpx as httpx_module
        from unittest.mock import patch

        transport = httpx_module.MockTransport(handler)
        original_client = httpx_module.Client

        def make_client(*args, **kwargs):
            kwargs["transport"] = transport
            return original_client(*args, **kwargs)

        return patch.object(httpx_module, "Client", side_effect=make_client)

    def _execute(self, config, handler):
        with self._executor_with_transport(handler):
            return DataSourceExecutor().execute(config, input_data=None)

    def test_get_returns_parsed_json_body(self):
        def handler(_request):
            import httpx as httpx_module
            return httpx_module.Response(
                200,
                json={"hello": "world"},
                headers={"content-type": "application/json"},
            )

        result = self._execute(
            {"sourceType": "rest", "url": "https://x.test", "method": "GET"},
            handler,
        )
        assert result.output["status_code"] == 200
        assert result.output["body"] == {"hello": "world"}
        assert result.output["url"] == "https://x.test"

    def test_text_body_falls_back_to_string(self):
        def handler(_request):
            import httpx as httpx_module
            return httpx_module.Response(
                200,
                text="plain text",
                headers={"content-type": "text/plain"},
            )

        result = self._execute(
            {"sourceType": "rest", "url": "https://x.test", "method": "GET"},
            handler,
        )
        assert result.output["body"] == "plain text"

    def test_invalid_json_falls_back_to_text(self):
        def handler(_request):
            import httpx as httpx_module
            return httpx_module.Response(
                200,
                text="{not valid json",
                headers={"content-type": "application/json"},
            )

        result = self._execute(
            {"sourceType": "rest", "url": "https://x.test", "method": "GET"},
            handler,
        )
        assert result.output["body"] == "{not valid json"

    def test_post_sends_body(self):
        captured = {}

        def handler(request):
            import httpx as httpx_module
            captured["body"] = request.content
            captured["method"] = request.method
            return httpx_module.Response(200, json={"ok": True})

        self._execute(
            {
                "sourceType": "rest",
                "url": "https://x.test",
                "method": "POST",
                "body": '{"name":"alice"}',
            },
            handler,
        )
        assert captured["method"] == "POST"
        assert captured["body"] == b'{"name":"alice"}'

    def test_bearer_adds_authorization_header(self):
        captured = {}

        def handler(request):
            import httpx as httpx_module
            captured["headers"] = dict(request.headers)
            return httpx_module.Response(200, json={"ok": True})

        self._execute(
            {
                "sourceType": "rest",
                "url": "https://x.test",
                "method": "GET",
                "authType": "bearer",
                "bearerToken": "abc123",
            },
            handler,
        )
        assert captured["headers"]["authorization"] == "Bearer abc123"

    def test_basic_auth_uses_httpx_basicauth(self):
        captured = {}

        def handler(request):
            import httpx as httpx_module
            captured["headers"] = dict(request.headers)
            return httpx_module.Response(200, json={"ok": True})

        self._execute(
            {
                "sourceType": "rest",
                "url": "https://x.test",
                "method": "GET",
                "authType": "basic",
                "basicUsername": "user",
                "basicPassword": "pass",
            },
            handler,
        )
        # httpx encodes "user:pass" → base64
        import base64
        expected = base64.b64encode(b"user:pass").decode()
        assert captured["headers"]["authorization"] == f"Basic {expected}"

    def test_api_key_uses_custom_header(self):
        captured = {}

        def handler(request):
            import httpx as httpx_module
            captured["headers"] = dict(request.headers)
            return httpx_module.Response(200, json={"ok": True})

        self._execute(
            {
                "sourceType": "rest",
                "url": "https://x.test",
                "method": "GET",
                "authType": "api_key",
                "apiKeyHeader": "X-Custom-Key",
                "apiKeyValue": "secret",
            },
            handler,
        )
        assert captured["headers"]["x-custom-key"] == "secret"

    def test_401_raises_auth_failed(self):
        from app.core.errors import ErrorCode, PipelineError

        def handler(_request):
            import httpx as httpx_module
            return httpx_module.Response(401, json={"error": "unauth"})

        with pytest.raises(PipelineError) as exc:
            self._execute(
                {"sourceType": "rest", "url": "https://x.test", "method": "GET"},
                handler,
            )
        assert exc.value.code == ErrorCode.CONNECTOR_AUTH_FAILED

    def test_429_raises_rate_limited(self):
        from app.core.errors import ErrorCode, PipelineError

        def handler(_request):
            import httpx as httpx_module
            return httpx_module.Response(429)

        with pytest.raises(PipelineError) as exc:
            self._execute(
                {"sourceType": "rest", "url": "https://x.test", "method": "GET"},
                handler,
            )
        assert exc.value.code == ErrorCode.CONNECTOR_RATE_LIMITED

    def test_500_raises_http_error(self):
        from app.core.errors import ErrorCode, PipelineError

        def handler(_request):
            import httpx as httpx_module
            return httpx_module.Response(500)

        with pytest.raises(PipelineError) as exc:
            self._execute(
                {"sourceType": "rest", "url": "https://x.test", "method": "GET"},
                handler,
            )
        assert exc.value.code == ErrorCode.CONNECTOR_HTTP_ERROR

    def test_timeout_raises_connector_timeout(self):
        import httpx as httpx_module
        from app.core.errors import ErrorCode, PipelineError

        def handler(_request):
            raise httpx_module.TimeoutException("slow upstream")

        with pytest.raises(PipelineError) as exc:
            self._execute(
                {"sourceType": "rest", "url": "https://x.test", "method": "GET"},
                handler,
            )
        assert exc.value.code == ErrorCode.CONNECTOR_TIMEOUT

    def test_auth_error_does_not_leak_token(self):
        """Auth failure messages must never include the credentials."""
        from app.core.errors import PipelineError

        def handler(_request):
            import httpx as httpx_module
            return httpx_module.Response(403)

        with pytest.raises(PipelineError) as exc:
            self._execute(
                {
                    "sourceType": "rest",
                    "url": "https://x.test",
                    "method": "GET",
                    "authType": "bearer",
                    "bearerToken": "very-secret-token",
                },
                handler,
            )
        assert "very-secret-token" not in exc.value.message

    # ── Validation ─────────────────────────────────────────────────────

    def test_validate_rejects_invalid_auth_type(self):
        executor = DataSourceExecutor()
        errors = executor.validate_config(
            {
                "sourceType": "rest",
                "url": "https://x.test",
                "authType": "oauth2",
            }
        )
        assert any(e.field == "authType" for e in errors)

    def test_validate_bearer_requires_token(self):
        executor = DataSourceExecutor()
        errors = executor.validate_config(
            {
                "sourceType": "rest",
                "url": "https://x.test",
                "authType": "bearer",
                "bearerToken": "",
            }
        )
        assert any(e.field == "bearerToken" for e in errors)

    def test_validate_basic_requires_username_and_password(self):
        executor = DataSourceExecutor()
        errors = executor.validate_config(
            {
                "sourceType": "rest",
                "url": "https://x.test",
                "authType": "basic",
            }
        )
        fields = {e.field for e in errors}
        assert "basicUsername" in fields
        assert "basicPassword" in fields

    def test_validate_api_key_requires_header_and_value(self):
        executor = DataSourceExecutor()
        errors = executor.validate_config(
            {
                "sourceType": "rest",
                "url": "https://x.test",
                "authType": "api_key",
            }
        )
        fields = {e.field for e in errors}
        assert "apiKeyHeader" in fields
        assert "apiKeyValue" in fields

    def test_validate_passes_with_valid_bearer_config(self):
        executor = DataSourceExecutor()
        errors = executor.validate_config(
            {
                "sourceType": "rest",
                "url": "https://x.test",
                "authType": "bearer",
                "bearerToken": "abc",
            }
        )
        assert errors == []


# ── Redact ────────────────────────────────────────────────────────────


class TestRedact:
    """NodeExecutor.redact() contract — masks sensitive data before SSE/log."""

    def test_default_redact_is_identity(self):
        # Default implementation returns the dict unchanged.
        executor = StubAIExecutor()
        output = {"analysis": "secret"}
        assert executor.redact(output) == output

    def test_datasource_redact_masks_authorization_header(self):
        executor = DataSourceExecutor()
        output = {
            "status_code": 200,
            "headers": {"Authorization": "Bearer secret", "Content-Type": "json"},
            "body": {},
        }
        redacted = executor.redact(output)
        assert redacted["headers"]["Authorization"] == "[REDACTED]"
        assert redacted["headers"]["Content-Type"] == "json"

    def test_datasource_redact_is_case_insensitive(self):
        executor = DataSourceExecutor()
        output = {
            "headers": {
                "authorization": "Bearer x",
                "Set-Cookie": "session=abc",
                "X-API-Key": "k",
            }
        }
        redacted = executor.redact(output)
        assert redacted["headers"]["authorization"] == "[REDACTED]"
        assert redacted["headers"]["Set-Cookie"] == "[REDACTED]"
        assert redacted["headers"]["X-API-Key"] == "[REDACTED]"

    def test_datasource_redact_does_not_mutate_input(self):
        executor = DataSourceExecutor()
        output = {"headers": {"Authorization": "secret"}, "body": "ok"}
        original_headers = dict(output["headers"])
        executor.redact(output)
        assert output["headers"] == original_headers

    def test_redact_handles_missing_headers_key(self):
        executor = DataSourceExecutor()
        output = {"body": "no headers here"}
        # Should not raise, just return as-is
        assert executor.redact(output) == output

    def test_engine_passes_redacted_output_to_step_completed(self):
        """The step_completed event payload must use executor.redact(),
        while the persisted step_result keeps the raw output."""

        class RedactingExecutor(NodeExecutor):
            @classmethod
            def manifest(cls):
                return ConnectorManifest(
                    name="Redact Test",
                    description="x",
                    node_type="datasource",
                    required_fields=[],
                )

            def execute(self, config, input_data):
                return ExecutorResult(output={"secret": "raw-token", "ok": True})

            def redact(self, output):
                return {"secret": "MASKED", "ok": output.get("ok")}

        original = _EXECUTORS["datasource"]
        _EXECUTORS["datasource"] = RedactingExecutor
        events = []
        try:
            pipeline = make_pipeline(
                nodes=[{"id": "src", "type": "datasource"}],
                edges=[],
            )
            engine = ExecutionEngine()
            run = engine.execute(
                pipeline,
                emit=lambda et, payload: events.append((et, payload)),
            )
        finally:
            _EXECUTORS["datasource"] = original

        # The step_completed event has the redacted output
        completed = [p for et, p in events if et == "step_completed"]
        assert len(completed) == 1
        assert completed[0]["output"] == {"secret": "MASKED", "ok": True}

        # The persisted step_result keeps the raw output
        assert run["steps"][0]["output"] == {"secret": "raw-token", "ok": True}

    def test_engine_drops_output_when_redact_raises(self):
        """If a custom redact() blows up, the engine must NOT leak the raw
        output to the event stream. It substitutes a marker payload instead."""

        class BrokenRedactExecutor(NodeExecutor):
            @classmethod
            def manifest(cls):
                return ConnectorManifest(
                    name="Broken Redact",
                    description="x",
                    node_type="datasource",
                    required_fields=[],
                )

            def execute(self, config, input_data):
                return ExecutorResult(output={"secret": "should-not-leak"})

            def redact(self, output):
                raise RuntimeError("oops")

        original = _EXECUTORS["datasource"]
        _EXECUTORS["datasource"] = BrokenRedactExecutor
        events = []
        try:
            pipeline = make_pipeline(
                nodes=[{"id": "src", "type": "datasource"}],
                edges=[],
            )
            engine = ExecutionEngine()
            engine.execute(
                pipeline,
                emit=lambda et, payload: events.append((et, payload)),
            )
        finally:
            _EXECUTORS["datasource"] = original

        completed = [p for et, p in events if et == "step_completed"]
        assert len(completed) == 1
        assert completed[0]["output"] == {"_redact_failed": True}
        assert "should-not-leak" not in str(completed[0]["output"])


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
                {
                    "id": "src",
                    "type": "datasource",
                    "config": {"sourceType": "rest", "url": ""},
                },
                {
                    "id": "analyze",
                    "type": "ai",
                    "config": {"provider": "anthropic", "model": "", "prompt": ""},
                },
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
                {
                    "id": "src",
                    "type": "datasource",
                    # Use sql to stay on stub-data path; preflight only
                    # exercises validate_config, but the engine then runs
                    # execute() which would otherwise fire a real HTTP call.
                    "config": {"sourceType": "sql", "url": "postgresql://localhost/db"},
                },
                {
                    "id": "out",
                    "type": "action",
                    "config": {"actionType": "transform", "outputFormat": "json"},
                },
            ],
            edges=[("src", "out")],
        )

        engine = ExecutionEngine()
        run = engine.execute(pipeline)
        assert run["status"] == "completed"


class TestCancellation:
    """Tests for cooperative cancellation via cancel_event."""

    def test_no_cancel_event_runs_to_completion(self):
        """When no cancel_event is passed, behavior is unchanged."""
        pipeline = make_pipeline(
            nodes=[
                {"id": "a", "type": "datasource"},
                {"id": "b", "type": "action"},
            ],
            edges=[("a", "b")],
        )
        engine = ExecutionEngine()
        run = engine.execute(pipeline)
        assert run["status"] == "completed"
        assert all(s["status"] == "completed" for s in run["steps"])

    def test_cancel_set_before_run_cancels_all_steps(self):
        """If cancel is set before execute starts, every step is cancelled."""
        pipeline = make_pipeline(
            nodes=[
                {"id": "a", "type": "datasource"},
                {"id": "b", "type": "action"},
            ],
            edges=[("a", "b")],
        )
        engine = ExecutionEngine()
        cancel_event = asyncio.Event()
        cancel_event.set()
        run = engine.execute(pipeline, cancel_event=cancel_event)

        assert run["status"] == "cancelled"
        assert len(run["steps"]) == 2
        assert all(s["status"] == "cancelled" for s in run["steps"])
        assert run["completed_at"] is not None

    def test_cancel_set_mid_run_finishes_current_then_cancels_rest(self):
        """Cancel set during step 1 lets it finish, marks step 2+3 cancelled."""

        # Custom executor that sets the cancel event during its execute()
        class CancellingDataSource(NodeExecutor):
            cancel_event_ref: asyncio.Event | None = None

            @classmethod
            def manifest(cls) -> ConnectorManifest:
                return ConnectorManifest(
                    type="datasource",
                    name="Cancelling DS",
                    description="",
                    config_schema={},
                )

            def validate_config(self, config):
                return []

            def execute(self, config, input_data):
                if self.cancel_event_ref is not None:
                    self.cancel_event_ref.set()
                return ExecutorResult(output={"data": "from-step-a"})

        cancel_event = asyncio.Event()
        CancellingDataSource.cancel_event_ref = cancel_event

        # Swap the executor for this test, restore after
        original = _EXECUTORS["datasource"]
        _EXECUTORS["datasource"] = CancellingDataSource
        try:
            pipeline = make_pipeline(
                nodes=[
                    {"id": "a", "type": "datasource"},
                    {"id": "b", "type": "action"},
                    {"id": "c", "type": "action"},
                ],
                edges=[("a", "b"), ("b", "c")],
            )
            engine = ExecutionEngine()
            run = engine.execute(pipeline, cancel_event=cancel_event)
        finally:
            _EXECUTORS["datasource"] = original
            CancellingDataSource.cancel_event_ref = None

        assert run["status"] == "cancelled"
        # Step a completed (was already in flight when cancel arrived)
        assert run["steps"][0]["node_id"] == "a"
        assert run["steps"][0]["status"] == "completed"
        # Steps b and c got cancelled
        assert run["steps"][1]["status"] == "cancelled"
        assert run["steps"][2]["status"] == "cancelled"

    def test_emit_callback_receives_lifecycle_events(self):
        """The emit callback is called with run_started, step_*, run_completed."""
        events: list[tuple[str, dict]] = []

        def emit(event_type: str, payload: dict) -> None:
            events.append((event_type, payload))

        pipeline = make_pipeline(
            nodes=[{"id": "a", "type": "datasource"}],
            edges=[],
        )
        engine = ExecutionEngine()
        engine.execute(pipeline, emit=emit)

        event_types = [e[0] for e in events]
        assert "run_started" in event_types
        assert "step_started" in event_types
        assert "step_completed" in event_types
        assert "run_completed" in event_types

        # run_started carries pipeline metadata
        run_started_payload = events[0][1]
        assert run_started_payload["total_steps"] == 1

    def test_emit_callback_receives_step_failed_then_run_failed(self):
        """When a step throws, emit gets step_failed then run_failed."""

        class FailingExecutor(NodeExecutor):
            @classmethod
            def manifest(cls):
                return ConnectorManifest(
                    type="datasource", name="Bomb", description="", config_schema={}
                )

            def validate_config(self, config):
                return []

            def execute(self, config, input_data):
                raise RuntimeError("boom")

        events: list[tuple[str, dict]] = []
        original = _EXECUTORS["datasource"]
        _EXECUTORS["datasource"] = FailingExecutor
        try:
            pipeline = make_pipeline(
                nodes=[{"id": "a", "type": "datasource"}],
                edges=[],
            )
            engine = ExecutionEngine()
            engine.execute(pipeline, emit=lambda t, p: events.append((t, p)))
        finally:
            _EXECUTORS["datasource"] = original

        types = [t for t, _ in events]
        assert "step_failed" in types
        assert "run_failed" in types

    def test_emit_failure_does_not_crash_run(self):
        """A buggy emit callback must not bring down the pipeline."""

        def bad_emit(event_type: str, payload: dict) -> None:
            raise RuntimeError("emit broken")

        pipeline = make_pipeline(
            nodes=[{"id": "a", "type": "datasource"}],
            edges=[],
        )
        engine = ExecutionEngine()
        run = engine.execute(pipeline, emit=bad_emit)
        # Run completes normally despite emit raising
        assert run["status"] == "completed"

    def test_explicit_run_id_is_preserved(self):
        """When a run_id is supplied, it's used in the result instead of a new UUID."""
        pipeline = make_pipeline(
            nodes=[{"id": "a", "type": "datasource"}],
            edges=[],
        )
        engine = ExecutionEngine()
        run = engine.execute(pipeline, run_id="11111111-2222-3333-4444-555555555555")
        assert run["id"] == "11111111-2222-3333-4444-555555555555"
