import { describe, it, expect, beforeEach } from "vitest";
import { usePipelineStore } from "../pipeline-store";

/**
 * Pipeline validation tests.
 *
 * Validation answers: "Is this pipeline complete enough to run?"
 * It catches structural problems BEFORE execution — the user sees
 * visual feedback on the canvas instead of a runtime error.
 */

describe("pipeline validation", () => {
  beforeEach(() => {
    usePipelineStore.setState({
      nodes: [],
      edges: [],
      pipelineName: "Untitled Pipeline",
    });
  });

  it("returns empty-pipeline error when no nodes exist", () => {
    const errors = usePipelineStore.getState().validate();

    expect(errors).toHaveLength(1);
    expect(errors[0].type).toBe("empty-pipeline");
  });

  it("returns orphan-node error for unconnected nodes", () => {
    const { addNode } = usePipelineStore.getState();
    addNode("datasource", { x: 0, y: 0 });
    addNode("ai", { x: 200, y: 0 });
    // No edges — both nodes are orphans

    const errors = usePipelineStore.getState().validate();
    const orphanErrors = errors.filter((e) => e.type === "orphan-node");

    expect(orphanErrors).toHaveLength(2);
  });

  it("returns no errors for a valid connected pipeline", () => {
    const { addNode } = usePipelineStore.getState();
    addNode("datasource", { x: 0, y: 0 });
    addNode("ai", { x: 200, y: 0 });

    const { nodes, onConnect } = usePipelineStore.getState();
    onConnect({
      source: nodes[0].id,
      target: nodes[1].id,
      sourceHandle: null,
      targetHandle: null,
    });

    const errors = usePipelineStore.getState().validate();
    expect(errors).toHaveLength(0);
  });

  it("does not flag nodes that have at least one connection", () => {
    const { addNode } = usePipelineStore.getState();
    addNode("datasource", { x: 0, y: 0 });
    addNode("ai", { x: 200, y: 0 });
    addNode("action", { x: 400, y: 0 });

    const { nodes, onConnect } = usePipelineStore.getState();
    // Connect first two, leave third disconnected
    onConnect({
      source: nodes[0].id,
      target: nodes[1].id,
      sourceHandle: null,
      targetHandle: null,
    });

    const errors = usePipelineStore.getState().validate();
    const orphanErrors = errors.filter((e) => e.type === "orphan-node");

    // Only the action node is orphaned
    expect(orphanErrors).toHaveLength(1);
    expect(orphanErrors[0].nodeId).toBe(nodes[2].id);
  });

  it("includes node ID in orphan errors for UI highlighting", () => {
    const { addNode } = usePipelineStore.getState();
    addNode("human", { x: 0, y: 0 });

    const { nodes } = usePipelineStore.getState();
    const errors = usePipelineStore.getState().validate();

    expect(errors[0].nodeId).toBe(nodes[0].id);
  });
});
