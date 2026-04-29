"""
Pipeline execution engine.

Takes a pipeline definition (nodes + edges), sorts topologically,
and executes each step in sequence. Output from step N flows as
input to step N+1.

This is the core logic — no HTTP, no database. The API layer
wraps this with persistence and request/response handling.
"""

import uuid
from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Any

from app.services.executors import get_executor


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

    def execute(self, pipeline: dict[str, Any]) -> dict[str, Any]:
        """
        Execute a pipeline and return the run result.

        Args:
            pipeline: Pipeline definition with nodes and edges.

        Returns:
            Run result dict matching the PipelineRun shape.
        """
        run_id = str(uuid.uuid4())
        run_started = datetime.now(timezone.utc)
        steps: list[dict[str, Any]] = []

        sorted_nodes = topological_sort(
            pipeline.get("nodes", []),
            pipeline.get("edges", []),
        )

        # Build a map of node outputs for data flow
        node_outputs: dict[str, Any] = {}
        # Build edge map: target_id → [source_ids]
        incoming: dict[str, list[str]] = defaultdict(list)
        for edge in pipeline.get("edges", []):
            incoming[edge["target"]].append(edge["source"])

        for order, node in enumerate(sorted_nodes):
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

            try:
                executor = get_executor(node_type)
                output = executor.execute(config, input_data)

                step_completed = datetime.now(timezone.utc)
                duration_ms = int(
                    (step_completed - step_started).total_seconds() * 1000
                )

                step_result.update(
                    {
                        "status": "completed",
                        "output": output,
                        "completed_at": step_completed.isoformat(),
                        "duration_ms": duration_ms,
                    }
                )

                # Extract AI metrics if present
                if "token_usage" in output:
                    step_result["token_usage"] = output["token_usage"]
                if "cost_usd" in output:
                    step_result["cost_usd"] = output["cost_usd"]

                node_outputs[node_id] = output

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
                return {
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

            steps.append(step_result)

        run_completed = datetime.now(timezone.utc)
        return {
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
