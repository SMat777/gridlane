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


# ── Stub Executors ───────────────────────────────────────────────────


class StubDataSourceExecutor(NodeExecutor):
    """Returns sample data as if fetched from an API or database."""

    VALID_SOURCE_TYPES = {"rest", "sql", "file"}

    @classmethod
    def manifest(cls) -> ConnectorManifest:
        return ConnectorManifest(
            name="Data Source (Stub)",
            description="Returns sample data for testing",
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
                    ConfigError(field="url", message=f"{label} is required for {source_type} sources")
                )

        return errors

    def execute(self, config: dict[str, Any], input_data: Any) -> ExecutorResult:
        source_type = config.get("sourceType", "rest")
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
                        ConfigError(field="temperature", message="temperature must be between 0 and 2")
                    )
            except (TypeError, ValueError):
                errors.append(
                    ConfigError(field="temperature", message="temperature must be a number")
                )

        max_tokens = config.get("maxTokens")
        if max_tokens is not None:
            try:
                tokens = int(max_tokens)
                if tokens < 1 or tokens > 100_000:
                    errors.append(
                        ConfigError(field="maxTokens", message="maxTokens must be between 1 and 100,000")
                    )
            except (TypeError, ValueError):
                errors.append(
                    ConfigError(field="maxTokens", message="maxTokens must be a whole number")
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
    "datasource": StubDataSourceExecutor,
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
