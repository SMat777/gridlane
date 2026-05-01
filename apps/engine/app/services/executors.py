"""
Node executors — connector interface contract.

Every node type has an executor that follows the same contract:
  1. manifest()        → metadata (name, description, node type)
  2. validate_config() → pre-flight config validation (before execution)
  3. execute()         → run the node and return an ExecutorResult

This makes connectors swappable — the execution engine doesn't care
whether it's a stub or a real connector. Adding a new connector means:
  1. Create a class inheriting NodeExecutor
  2. Implement the 3 methods
  3. Register it in _EXECUTORS

US2 uses stub executors that return predictable dummy data.
US3 will replace these with real connectors (REST, SQL, LLM, etc.).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import httpx

from app.core.errors import ErrorCode, PipelineError


# ── Connector Contract Types ─────────────────────────────────────────


@dataclass
class ConfigError:
    """A single validation error for a config field.

    Used by validate_config() to report what's wrong with the config
    BEFORE execution starts. Frontend can use this to show inline errors.
    """

    field: str
    message: str
    severity: str = "error"  # "error" blocks execution, "warning" doesn't


@dataclass
class ConnectorManifest:
    """Metadata about a connector — what it is and what it needs.

    Used for UI display and documentation. Required fields tells the
    frontend which config fields must be filled before execution.
    """

    name: str
    description: str
    node_type: str
    required_fields: list[str] = field(default_factory=list)


@dataclass
class ExecutorResult:
    """Typed result from executor.execute().

    Instead of returning a raw dict, executors return this structured
    result. The engine extracts metrics from it automatically.
    """

    output: dict[str, Any]
    token_usage: dict[str, int] | None = None
    cost_usd: float | None = None


# ── Base Executor ────────────────────────────────────────────────────


class NodeExecutor(ABC):
    """Base class for all node executors.

    Contract:
      manifest()        → static metadata (classmethod)
      validate_config() → list of errors (empty = valid)
      execute()         → ExecutorResult with output + optional metrics
    """

    @classmethod
    @abstractmethod
    def manifest(cls) -> ConnectorManifest:
        """Return metadata about this connector."""
        ...

    def validate_config(self, config: dict[str, Any]) -> list[ConfigError]:
        """Validate config before execution. Override for custom validation.

        Default implementation checks that all required_fields from the
        manifest are present and non-empty in the config.
        """
        errors: list[ConfigError] = []
        for field_name in self.manifest().required_fields:
            value = config.get(field_name)
            if value is None or value == "":
                errors.append(
                    ConfigError(
                        field=field_name,
                        message=f"{field_name} is required",
                    )
                )
        return errors

    @abstractmethod
    def execute(self, config: dict[str, Any], input_data: Any) -> ExecutorResult:
        """Execute the node with given config and input from upstream."""
        ...

    def redact(self, output: dict[str, Any]) -> dict[str, Any]:
        """Strip sensitive fields before output enters the public event stream.

        Default returns output unchanged. Override per executor to mask
        fields like response headers (Authorization, Set-Cookie),
        credentials, or raw rows from privileged queries.

        Contract:
          - MUST NOT mutate the input dict; return a new dict.
          - The redacted result is what goes into SSE events and the
            run_events log (currently public per the foundation auth model).
          - Raw output is still passed as input to the next step and stored
            in step_results.output_data, which will be auth-gated when auth
            lands.
        """
        return output


# ── Stub Executors ───────────────────────────────────────────────────


REST_TIMEOUT_SECONDS = 30.0
VALID_AUTH_TYPES = {"none", "bearer", "basic", "api_key"}
VALID_HTTP_METHODS = {"GET", "POST", "PUT", "DELETE"}

# Headers we always mask before output reaches the public event stream.
# Comparison is lowercase since HTTP header names are case-insensitive.
SENSITIVE_HEADER_NAMES = frozenset(
    {"authorization", "cookie", "set-cookie", "x-api-key", "proxy-authorization"}
)


class DataSourceExecutor(NodeExecutor):
    """Routes by sourceType. REST is real (httpx); SQL/File still stub.

    SQL and File connectors will replace their stub branches in later phases.
    Keeping them here means existing pipelines using sourceType=sql/file keep
    working — they just continue to receive sample data rather than failing.
    """

    VALID_SOURCE_TYPES = {"rest", "sql", "file"}

    @classmethod
    def manifest(cls) -> ConnectorManifest:
        return ConnectorManifest(
            name="Data Source",
            description="Fetch data from REST APIs (SQL and File coming next)",
            node_type="datasource",
            required_fields=["sourceType"],
        )

    def validate_config(self, config: dict[str, Any]) -> list[ConfigError]:
        errors = super().validate_config(config)

        source_type = config.get("sourceType", "")
        if source_type and source_type not in self.VALID_SOURCE_TYPES:
            errors.append(
                ConfigError(
                    field="sourceType",
                    message=f"sourceType must be one of: {', '.join(sorted(self.VALID_SOURCE_TYPES))}",
                )
            )

        # URL is required for REST and SQL but not for file
        if source_type in ("rest", "sql"):
            url = config.get("url", "")
            if not url or not str(url).strip():
                label = "URL" if source_type == "rest" else "Connection string"
                errors.append(
                    ConfigError(
                        field="url",
                        message=f"{label} is required for {source_type} sources",
                    )
                )

        if source_type == "rest":
            method = config.get("method", "GET")
            if method and method not in VALID_HTTP_METHODS:
                errors.append(
                    ConfigError(
                        field="method",
                        message=f"method must be one of: {', '.join(sorted(VALID_HTTP_METHODS))}",
                    )
                )

            auth_type = config.get("authType", "none")
            if auth_type and auth_type not in VALID_AUTH_TYPES:
                errors.append(
                    ConfigError(
                        field="authType",
                        message=f"authType must be one of: {', '.join(sorted(VALID_AUTH_TYPES))}",
                    )
                )

            # Per-authType field requirements
            if auth_type == "bearer" and not config.get("bearerToken", "").strip():
                errors.append(
                    ConfigError(
                        field="bearerToken",
                        message="Bearer token is required when authType is bearer",
                    )
                )
            if auth_type == "basic":
                if not config.get("basicUsername", "").strip():
                    errors.append(
                        ConfigError(
                            field="basicUsername",
                            message="Username is required for basic auth",
                        )
                    )
                if not config.get("basicPassword", "").strip():
                    errors.append(
                        ConfigError(
                            field="basicPassword",
                            message="Password is required for basic auth",
                        )
                    )
            if auth_type == "api_key":
                if not config.get("apiKeyHeader", "").strip():
                    errors.append(
                        ConfigError(
                            field="apiKeyHeader",
                            message="Header name is required for API key auth",
                        )
                    )
                if not config.get("apiKeyValue", "").strip():
                    errors.append(
                        ConfigError(
                            field="apiKeyValue",
                            message="API key value is required for API key auth",
                        )
                    )

        return errors

    def execute(self, config: dict[str, Any], input_data: Any) -> ExecutorResult:
        source_type = config.get("sourceType", "rest")
        if source_type == "rest":
            return _execute_rest(config)
        # SQL/File still stubbed — replaced when those connectors land
        return ExecutorResult(
            output={
                "data": [
                    {"id": 1, "name": "Sample Item 1", "value": 42.5},
                    {"id": 2, "name": "Sample Item 2", "value": 18.3},
                    {"id": 3, "name": "Sample Item 3", "value": 95.1},
                ],
                "source": source_type,
                "record_count": 3,
            }
        )

    def redact(self, output: dict[str, Any]) -> dict[str, Any]:
        """Mask sensitive response headers before SSE / event log.

        REST responses can echo back credentials (Set-Cookie on auth flows,
        Authorization in proxied requests, vendor-specific X-API-Key headers).
        We mask values rather than dropping the keys so debugging can still
        confirm "an Authorization header was present" without revealing it.
        """
        if "headers" not in output or not isinstance(output["headers"], dict):
            return output
        redacted_headers = {
            k: ("[REDACTED]" if k.lower() in SENSITIVE_HEADER_NAMES else v)
            for k, v in output["headers"].items()
        }
        return {**output, "headers": redacted_headers}


def _build_headers(config: dict[str, Any]) -> dict[str, str]:
    """Combine user-defined headers with auth-derived header (bearer/api_key).

    Auth values overwrite same-named user headers — explicit auth config
    should win over a stale Authorization key the user might have left in.
    """
    headers: dict[str, str] = {}
    for key, value in (config.get("headers") or {}).items():
        headers[str(key)] = str(value)

    auth_type = config.get("authType", "none")
    if auth_type == "bearer":
        token = config.get("bearerToken", "")
        if token:
            headers["Authorization"] = f"Bearer {token}"
    elif auth_type == "api_key":
        header_name = config.get("apiKeyHeader") or "X-API-Key"
        api_key = config.get("apiKeyValue", "")
        if api_key:
            headers[str(header_name)] = str(api_key)
    return headers


def _build_auth(config: dict[str, Any]) -> httpx.Auth | None:
    """Return an httpx.Auth instance for basic auth, or None for header-based."""
    if config.get("authType") == "basic":
        return httpx.BasicAuth(
            username=config.get("basicUsername", ""),
            password=config.get("basicPassword", ""),
        )
    return None


def _parse_body(response: httpx.Response) -> Any:
    """Decode response body. JSON when content-type announces it; else text.

    Falls back to text on JSON parse failure rather than raising — clients
    benefit more from "here is what came back" than from an internal error.
    """
    content_type = response.headers.get("content-type", "").lower()
    if "application/json" in content_type or "+json" in content_type:
        try:
            return response.json()
        except ValueError:
            return response.text
    return response.text


def _execute_rest(config: dict[str, Any]) -> ExecutorResult:
    """Execute an HTTP request using the REST connector config.

    Maps httpx-level outcomes to structured ErrorCodes so the frontend can
    render specific messages for timeout, auth failure, rate-limiting and
    generic HTTP error. Auth failures intentionally never include the token
    in the error payload — only the status code is exposed.
    """
    url = config.get("url", "")
    method = config.get("method", "GET")
    body = config.get("body")
    headers = _build_headers(config)
    auth = _build_auth(config)

    try:
        with httpx.Client(timeout=REST_TIMEOUT_SECONDS) as client:
            response = client.request(
                method=method,
                url=url,
                headers=headers,
                auth=auth,
                content=body if body else None,
            )
    except httpx.TimeoutException:
        raise PipelineError(
            code=ErrorCode.CONNECTOR_TIMEOUT,
            message=f"Request to {url} timed out after {int(REST_TIMEOUT_SECONDS)}s",
            status_code=504,
        )
    except httpx.HTTPError as exc:
        raise PipelineError(
            code=ErrorCode.CONNECTOR_NETWORK_ERROR,
            message=f"Network error calling {url}: {exc}",
            status_code=502,
        )

    status = response.status_code
    if status in (401, 403):
        raise PipelineError(
            code=ErrorCode.CONNECTOR_AUTH_FAILED,
            message=f"Authentication failed (HTTP {status})",
            status_code=502,
            details={"status": status, "url": url},
        )
    if status == 429:
        raise PipelineError(
            code=ErrorCode.CONNECTOR_RATE_LIMITED,
            message="Rate limited by upstream",
            status_code=502,
            details={"status": status, "url": url},
        )
    if status >= 400:
        raise PipelineError(
            code=ErrorCode.CONNECTOR_HTTP_ERROR,
            message=f"HTTP {status} from {url}",
            status_code=502,
            details={"status": status, "url": url},
        )

    return ExecutorResult(
        output={
            "status_code": status,
            "headers": dict(response.headers),
            "body": _parse_body(response),
            "url": url,
            "method": method,
        }
    )


class StubAIExecutor(NodeExecutor):
    """Returns a simulated AI analysis with token metrics."""

    VALID_PROVIDERS = {"anthropic", "openai"}

    @classmethod
    def manifest(cls) -> ConnectorManifest:
        return ConnectorManifest(
            name="AI Analysis (Stub)",
            description="Returns simulated AI analysis with token metrics",
            node_type="ai",
            required_fields=["provider", "model", "prompt"],
        )

    def validate_config(self, config: dict[str, Any]) -> list[ConfigError]:
        errors = super().validate_config(config)

        provider = config.get("provider", "")
        if provider and provider not in self.VALID_PROVIDERS:
            errors.append(
                ConfigError(
                    field="provider",
                    message=f"provider must be one of: {', '.join(sorted(self.VALID_PROVIDERS))}",
                )
            )

        temperature = config.get("temperature")
        if temperature is not None:
            try:
                temp = float(temperature)
                if temp < 0 or temp > 2:
                    errors.append(
                        ConfigError(
                            field="temperature",
                            message="temperature must be between 0 and 2",
                        )
                    )
            except (TypeError, ValueError):
                errors.append(
                    ConfigError(
                        field="temperature", message="temperature must be a number"
                    )
                )

        max_tokens = config.get("maxTokens")
        if max_tokens is not None:
            try:
                tokens = int(max_tokens)
                if tokens < 1 or tokens > 100_000:
                    errors.append(
                        ConfigError(
                            field="maxTokens",
                            message="maxTokens must be between 1 and 100,000",
                        )
                    )
            except (TypeError, ValueError):
                errors.append(
                    ConfigError(
                        field="maxTokens", message="maxTokens must be a whole number"
                    )
                )

        return errors

    def execute(self, config: dict[str, Any], input_data: Any) -> ExecutorResult:
        provider = config.get("provider", "anthropic")
        model = config.get("model", "claude-sonnet-4-20250514")
        prompt = config.get("prompt", "Analyze the input data")

        return ExecutorResult(
            output={
                "analysis": (
                    f"[Stub {provider}/{model}] Based on the input data, "
                    f"here is the analysis for prompt: '{prompt[:50]}...'"
                ),
                "provider": provider,
                "model": model,
            },
            token_usage={
                "input_tokens": 150,
                "output_tokens": 89,
                "total_tokens": 239,
            },
            cost_usd=0.004,
        )


class StubActionExecutor(NodeExecutor):
    """Returns formatted output based on action config."""

    VALID_ACTION_TYPES = {"transform", "output"}
    VALID_OUTPUT_FORMATS = {"json", "csv", "text"}

    @classmethod
    def manifest(cls) -> ConnectorManifest:
        return ConnectorManifest(
            name="Action (Stub)",
            description="Passes input through with format metadata",
            node_type="action",
            required_fields=["actionType"],
        )

    def validate_config(self, config: dict[str, Any]) -> list[ConfigError]:
        errors = super().validate_config(config)

        action_type = config.get("actionType", "")
        if action_type and action_type not in self.VALID_ACTION_TYPES:
            errors.append(
                ConfigError(
                    field="actionType",
                    message=f"actionType must be one of: {', '.join(sorted(self.VALID_ACTION_TYPES))}",
                )
            )

        output_format = config.get("outputFormat")
        if output_format and output_format not in self.VALID_OUTPUT_FORMATS:
            errors.append(
                ConfigError(
                    field="outputFormat",
                    message=f"outputFormat must be one of: {', '.join(sorted(self.VALID_OUTPUT_FORMATS))}",
                )
            )

        return errors

    def execute(self, config: dict[str, Any], input_data: Any) -> ExecutorResult:
        output_format = config.get("outputFormat", "json")
        return ExecutorResult(
            output={
                "output": input_data,
                "format": output_format,
                "action": config.get("actionType", "transform"),
            }
        )


class StubHumanExecutor(NodeExecutor):
    """Auto-approves for US2. Real HUMAN step will pause execution."""

    @classmethod
    def manifest(cls) -> ConnectorManifest:
        return ConnectorManifest(
            name="Human Review (Stub)",
            description="Auto-approves for testing — real HUMAN step pauses execution",
            node_type="human",
            required_fields=[],
        )

    def execute(self, config: dict[str, Any], input_data: Any) -> ExecutorResult:
        return ExecutorResult(
            output={
                "approved": True,
                "decision": "auto-approved",
                "comment": "Stub: auto-approved for pipeline testing",
                "reviewed_data": input_data,
            }
        )


# ── Executor Registry ────────────────────────────────────────────────


_EXECUTORS: dict[str, type[NodeExecutor]] = {
    "datasource": DataSourceExecutor,
    "ai": StubAIExecutor,
    "action": StubActionExecutor,
    "human": StubHumanExecutor,
}


def get_executor(node_type: str) -> NodeExecutor:
    """Get the executor instance for a node type."""
    executor_class = _EXECUTORS.get(node_type)
    if executor_class is None:
        raise ValueError(f"Unknown node type: {node_type}")
    return executor_class()
