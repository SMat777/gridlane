"""
Pipeline execution engine.

Takes a pipeline definition (nodes + edges), sorts topologically,
and executes each step in sequence. Output from step N flows as
input to step N+1.

This is the core logic — no HTTP, no database. The API layer
wraps this with persistence and request/response handling.
"""

import asyncio
import uuid
from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Any, Callable

from app.core.errors import ErrorCode, PipelineError
from app.services.executors import get_executor

# Emit callback signature: (event_type: str, payload: dict) -> None
# Synchronous because it's called from inside the engine's sync execute() loop,
# which itself runs inside asyncio.to_thread(). Implementations should be quick
# (the bus.publish + DB append happens via thread-safe coro scheduled on the loop).
EmitCallback = Callable[[str, dict[str, Any]], None]


def topological_sort(
    nodes: list[dict[str, Any]], edges: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Sort nodes in execution order using Kahn's algorithm.

    Returns nodes ordered so that every node comes after its dependencies.
    For nodes at the same level, order is stable (preserves input order).
    """
    if not nodes:
        return []

    # Build adjacency list and in-degree count
    node_map = {n["id"]: n for n in nodes}
    node_ids = set(node_map.keys())
    in_degree: dict[str, int] = {node_id: 0 for node_id in node_ids}
    adjacency: dict[str, list[str]] = defaultdict(list)

    # Validate edges reference existing nodes before building the graph
    for edge in edges:
        invalid_ids = []
        if edge["source"] not in node_ids:
            invalid_ids.append(edge["source"])
        if edge["target"] not in node_ids:
            invalid_ids.append(edge["target"])
        if invalid_ids:
            raise ValueError(
                f"Edge references non-existent node(s): {', '.join(invalid_ids)}"
            )
        adjacency[edge["source"]].append(edge["target"])
        in_degree[edge["target"]] += 1

    # Start with nodes that have no incoming edges
    queue = deque(
        node_id for node_id in [n["id"] for n in nodes] if in_degree[node_id] == 0
    )

    sorted_nodes: list[dict[str, Any]] = []
    while queue:
        node_id = queue.popleft()
        sorted_nodes.append(node_map[node_id])

        for neighbor in adjacency[node_id]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # Cycle detection: if not all nodes were sorted, there's a cycle
    if len(sorted_nodes) != len(nodes):
        unsorted = node_ids - {n["id"] for n in sorted_nodes}
        raise ValueError(
            f"Pipeline contains a cycle involving node(s): {', '.join(sorted(unsorted))}"
        )

    return sorted_nodes


class ExecutionEngine:
    """
    Executes a pipeline definition synchronously.

    Each node is executed in topological order. The output of a node
    is passed as input to the next node in the chain.
    """

    def execute(
        self,
        pipeline: dict[str, Any],
        cancel_event: asyncio.Event | None = None,
        run_id: str | None = None,
        emit: EmitCallback | None = None,
    ) -> dict[str, Any]:
        """
        Execute a pipeline and return the run result.

        Args:
            pipeline: Pipeline definition with nodes and edges.
            cancel_event: Optional event polled between steps. If set, the
                current step finishes (so connector side-effects don't get
                left half-applied), then remaining steps are marked
                cancelled and the run finalizes with status='cancelled'.
            run_id: Optional pre-assigned run ID. The async launch flow
                creates a DB row first and passes the ID in so the engine
                writes step results against the correct run.
            emit: Optional callback for progress events. Called with
                (event_type, payload). Event types: run_started,
                step_started, step_completed, step_failed,
                run_completed, run_failed, run_cancelled. The async
                launch + SSE flow wires this through the event bus.

        Returns:
            Run result dict matching the PipelineRun shape.
        """
        if run_id is None:
            run_id = str(uuid.uuid4())
        run_started = datetime.now(timezone.utc)
        steps: list[dict[str, Any]] = []

        def _emit(event_type: str, payload: dict[str, Any]) -> None:
            """Internal emit wrapper — silently no-op if no callback provided."""
            if emit is not None:
                try:
                    emit(event_type, payload)
                except Exception:
                    # Never let event emission failure crash the run.
                    # Persistence is the source of truth; events are best-effort.
                    pass

        sorted_nodes = topological_sort(
            pipeline.get("nodes", []),
            pipeline.get("edges", []),
        )

        _emit(
            "run_started",
            {
                "run_id": run_id,
                "pipeline_id": pipeline.get("id", ""),
                "pipeline_name": pipeline.get("name", ""),
                "total_steps": len(sorted_nodes),
                "started_at": run_started.isoformat(),
            },
        )

        # ── Preflight: validate all configs before executing any step ──
        # Fail fast with ALL errors at once so the user can fix everything
        # in one pass, rather than discovering errors one step at a time.
        all_validation_errors = []
        for node in sorted_nodes:
            node_id = node["id"]
            node_type = node.get("type", node.get("data", {}).get("nodeType", ""))
            config = node.get("data", {}).get("config", {})

            try:
                executor = get_executor(node_type)
                errors = executor.validate_config(config)
                for error in errors:
                    all_validation_errors.append(
                        {
                            "node_id": node_id,
                            "field": error.field,
                            "message": error.message,
                            "severity": error.severity,
                        }
                    )
            except ValueError:
                # Unknown node type — will fail during execution anyway
                pass

        if all_validation_errors:
            raise PipelineError(
                code=ErrorCode.VALIDATION_ERROR,
                message=f"Config validation failed for {len(all_validation_errors)} field(s)",
                details={"validation_errors": all_validation_errors},
            )

        # Build a map of node outputs for data flow
        node_outputs: dict[str, Any] = {}
        # Build edge map: target_id → [source_ids]
        incoming: dict[str, list[str]] = defaultdict(list)
        for edge in pipeline.get("edges", []):
            incoming[edge["target"]].append(edge["source"])

        for order, node in enumerate(sorted_nodes):
            # ── Cooperative cancellation check ──────────────────────────
            # We check BEFORE starting the step (not mid-step) so connectors
            # don't get aborted halfway through writing to an external system.
            # The current step gets to run to completion if it was already
            # in flight; cancellation only stops what hasn't started yet.
            if cancel_event is not None and cancel_event.is_set():
                cancelled_at = datetime.now(timezone.utc)
                for remaining in sorted_nodes[order:]:
                    steps.append(
                        {
                            "node_id": remaining["id"],
                            "node_type": remaining.get(
                                "type",
                                remaining.get("data", {}).get("nodeType", ""),
                            ),
                            "node_label": remaining.get("data", {}).get("label", ""),
                            "order": sorted_nodes.index(remaining),
                            "status": "cancelled",
                            "input": None,
                            "output": None,
                            "started_at": cancelled_at.isoformat(),
                            "completed_at": cancelled_at.isoformat(),
                            "duration_ms": 0,
                        }
                    )
                run_completed = cancelled_at
                final = {
                    "id": run_id,
                    "pipeline_id": pipeline.get("id", ""),
                    "pipeline_name": pipeline.get("name", ""),
                    "status": "cancelled",
                    "steps": steps,
                    "total_duration_ms": int(
                        (run_completed - run_started).total_seconds() * 1000
                    ),
                    "total_cost_usd": sum(
                        s.get("cost_usd", 0) for s in steps if s.get("cost_usd")
                    ),
                    "started_at": run_started.isoformat(),
                    "completed_at": run_completed.isoformat(),
                }
                _emit(
                    "run_cancelled",
                    {
                        "run_id": run_id,
                        "status": "cancelled",
                        "total_duration_ms": final["total_duration_ms"],
                        "completed_at": final["completed_at"],
                    },
                )
                return final

            node_id = node["id"]
            node_type = node.get("type", node.get("data", {}).get("nodeType", ""))
            node_label = node.get("data", {}).get("label", node_type)
            config = node.get("data", {}).get("config", {})

            # Gather input from upstream nodes
            sources = incoming.get(node_id, [])
            if len(sources) == 1:
                input_data = node_outputs.get(sources[0])
            elif len(sources) > 1:
                input_data = {src_id: node_outputs.get(src_id) for src_id in sources}
            else:
                input_data = None

            step_started = datetime.now(timezone.utc)
            step_result: dict[str, Any] = {
                "node_id": node_id,
                "node_type": node_type,
                "node_label": node_label,
                "order": order,
                "input": input_data,
                "started_at": step_started.isoformat(),
            }

            _emit(
                "step_started",
                {
                    "node_id": node_id,
                    "node_type": node_type,
                    "node_label": node_label,
                    "order": order,
                    "started_at": step_started.isoformat(),
                },
            )

            try:
                executor = get_executor(node_type)
                result = executor.execute(config, input_data)

                step_completed = datetime.now(timezone.utc)
                duration_ms = int(
                    (step_completed - step_started).total_seconds() * 1000
                )

                step_result.update(
                    {
                        "status": "completed",
                        "output": result.output,
                        "completed_at": step_completed.isoformat(),
                        "duration_ms": duration_ms,
                    }
                )

                # Extract metrics from ExecutorResult
                if result.token_usage is not None:
                    step_result["token_usage"] = result.token_usage
                if result.cost_usd is not None:
                    step_result["cost_usd"] = result.cost_usd

                node_outputs[node_id] = result.output

                cumulative_cost = sum(
                    s.get("cost_usd", 0)
                    for s in [*steps, step_result]
                    if s.get("cost_usd")
                )
                _emit(
                    "step_completed",
                    {
                        "node_id": node_id,
                        "status": "completed",
                        "duration_ms": duration_ms,
                        "output": result.output,
                        "completed_at": step_completed.isoformat(),
                        "cumulative_cost_usd": cumulative_cost,
                    },
                )

            except Exception as e:
                step_completed = datetime.now(timezone.utc)
                duration_ms = int(
                    (step_completed - step_started).total_seconds() * 1000
                )
                step_result.update(
                    {
                        "status": "failed",
                        "output": None,
                        "error": str(e),
                        "completed_at": step_completed.isoformat(),
                        "duration_ms": duration_ms,
                    }
                )

                _emit(
                    "step_failed",
                    {
                        "node_id": node_id,
                        "status": "failed",
                        "error": str(e),
                        "duration_ms": duration_ms,
                        "completed_at": step_completed.isoformat(),
                    },
                )

                # Record remaining steps as cancelled
                steps.append(step_result)
                for remaining_node in sorted_nodes[order + 1 :]:
                    steps.append(
                        {
                            "node_id": remaining_node["id"],
                            "node_type": remaining_node.get(
                                "type",
                                remaining_node.get("data", {}).get("nodeType", ""),
                            ),
                            "node_label": remaining_node.get("data", {}).get(
                                "label", ""
                            ),
                            "order": sorted_nodes.index(remaining_node),
                            "status": "cancelled",
                            "input": None,
                            "output": None,
                            "started_at": step_completed.isoformat(),
                            "completed_at": step_completed.isoformat(),
                            "duration_ms": 0,
                        }
                    )

                run_completed = datetime.now(timezone.utc)
                final = {
                    "id": run_id,
                    "pipeline_id": pipeline.get("id", ""),
                    "pipeline_name": pipeline.get("name", ""),
                    "status": "failed",
                    "steps": steps,
                    "total_duration_ms": int(
                        (run_completed - run_started).total_seconds() * 1000
                    ),
                    "total_cost_usd": sum(
                        s.get("cost_usd", 0) for s in steps if s.get("cost_usd")
                    ),
                    "started_at": run_started.isoformat(),
                    "completed_at": run_completed.isoformat(),
                }
                _emit(
                    "run_failed",
                    {
                        "run_id": run_id,
                        "status": "failed",
                        "error": str(e),
                        "total_duration_ms": final["total_duration_ms"],
                        "total_cost_usd": final["total_cost_usd"],
                        "completed_at": final["completed_at"],
                    },
                )
                return final

            steps.append(step_result)

        run_completed = datetime.now(timezone.utc)
        final = {
            "id": run_id,
            "pipeline_id": pipeline.get("id", ""),
            "pipeline_name": pipeline.get("name", ""),
            "status": "completed",
            "steps": steps,
            "total_duration_ms": int(
                (run_completed - run_started).total_seconds() * 1000
            ),
            "total_cost_usd": sum(
                s.get("cost_usd", 0) for s in steps if s.get("cost_usd")
            ),
            "started_at": run_started.isoformat(),
            "completed_at": run_completed.isoformat(),
        }
        _emit(
            "run_completed",
            {
                "run_id": run_id,
                "status": "completed",
                "total_duration_ms": final["total_duration_ms"],
                "total_cost_usd": final["total_cost_usd"],
                "completed_at": final["completed_at"],
            },
        )
        return final
