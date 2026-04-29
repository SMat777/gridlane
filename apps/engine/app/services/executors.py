"""
Node executors — one per node type.

US2 uses stub executors that return predictable dummy data.
US3 will replace these with real connectors (REST, SQL, LLM, etc.).

Each executor has the same interface:
  execute(config, input_data) → output_data

This makes them swappable — the execution engine doesn't care
whether it's a stub or a real connector.
"""

from abc import ABC, abstractmethod
from typing import Any


class NodeExecutor(ABC):
    """Base class for all node executors."""

    @abstractmethod
    def execute(self, config: dict[str, Any], input_data: Any) -> dict[str, Any]:
        """Execute the node with given config and input from upstream."""
        ...


class StubDataSourceExecutor(NodeExecutor):
    """Returns sample data as if fetched from an API or database."""

    def execute(self, config: dict[str, Any], input_data: Any) -> dict[str, Any]:
        source_type = config.get("sourceType", "rest")
        return {
            "data": [
                {"id": 1, "name": "Sample Item 1", "value": 42.5},
                {"id": 2, "name": "Sample Item 2", "value": 18.3},
                {"id": 3, "name": "Sample Item 3", "value": 95.1},
            ],
            "source": source_type,
            "record_count": 3,
        }


class StubAIExecutor(NodeExecutor):
    """Returns a simulated AI analysis with token metrics."""

    def execute(self, config: dict[str, Any], input_data: Any) -> dict[str, Any]:
        provider = config.get("provider", "anthropic")
        model = config.get("model", "claude-sonnet-4-20250514")
        prompt = config.get("prompt", "Analyze the input data")

        return {
            "analysis": (
                f"[Stub {provider}/{model}] Based on the input data, "
                f"here is the analysis for prompt: '{prompt[:50]}...'"
            ),
            "provider": provider,
            "model": model,
            "token_usage": {
                "input_tokens": 150,
                "output_tokens": 89,
                "total_tokens": 239,
            },
            "cost_usd": 0.004,
        }


class StubActionExecutor(NodeExecutor):
    """Returns formatted output based on action config."""

    def execute(self, config: dict[str, Any], input_data: Any) -> dict[str, Any]:
        output_format = config.get("outputFormat", "json")
        return {
            "output": input_data,
            "format": output_format,
            "action": config.get("actionType", "transform"),
        }


class StubHumanExecutor(NodeExecutor):
    """Auto-approves for US2. Real HUMAN step will pause execution."""

    def execute(self, config: dict[str, Any], input_data: Any) -> dict[str, Any]:
        return {
            "approved": True,
            "decision": "auto-approved",
            "comment": "Stub: auto-approved for pipeline testing",
            "reviewed_data": input_data,
        }


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
