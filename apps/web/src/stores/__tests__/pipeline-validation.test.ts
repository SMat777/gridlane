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

  it("returns no errors for a valid connected pipeline with valid configs", () => {
    const { addNode, updateNodeConfig } = usePipelineStore.getState();
    addNode("datasource", { x: 0, y: 0 });
    addNode("ai", { x: 200, y: 0 });

    const { nodes, onConnect } = usePipelineStore.getState();

    // Fill in required config values so config validation passes
    updateNodeConfig(nodes[0].id, { url: "https://api.example.com/data" });
    updateNodeConfig(nodes[1].id, { prompt: "Analyze: {{ input }}" });

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

  it("detects a simple two-node cycle", () => {
    const { addNode } = usePipelineStore.getState();
    addNode("datasource", { x: 0, y: 0 });
    addNode("ai", { x: 200, y: 0 });

    const { nodes, onConnect } = usePipelineStore.getState();
    // Create cycle: A → B → A
    onConnect({ source: nodes[0].id, target: nodes[1].id, sourceHandle: null, targetHandle: null });
    onConnect({ source: nodes[1].id, target: nodes[0].id, sourceHandle: null, targetHandle: null });

    const errors = usePipelineStore.getState().validate();
    const cycleErrors = errors.filter((e) => e.type === "cycle-detected");

    expect(cycleErrors).toHaveLength(1);
    expect(cycleErrors[0].message).toContain("cycle");
  });

  it("detects a three-node cycle", () => {
    const { addNode } = usePipelineStore.getState();
    addNode("datasource", { x: 0, y: 0 });
    addNode("ai", { x: 200, y: 0 });
    addNode("action", { x: 400, y: 0 });

    const { nodes, onConnect } = usePipelineStore.getState();
    // Create cycle: A → B → C → A
    onConnect({ source: nodes[0].id, target: nodes[1].id, sourceHandle: null, targetHandle: null });
    onConnect({ source: nodes[1].id, target: nodes[2].id, sourceHandle: null, targetHandle: null });
    onConnect({ source: nodes[2].id, target: nodes[0].id, sourceHandle: null, targetHandle: null });

    const errors = usePipelineStore.getState().validate();
    const cycleErrors = errors.filter((e) => e.type === "cycle-detected");

    expect(cycleErrors).toHaveLength(1);
  });

  // ── Config validation ──────────────────────────────────────────────

  it("returns invalid-config errors for nodes with default (incomplete) configs", () => {
    const { addNode } = usePipelineStore.getState();
    addNode("datasource", { x: 0, y: 0 }); // default: empty URL
    addNode("ai", { x: 200, y: 0 }); // default: empty prompt

    const { nodes, onConnect } = usePipelineStore.getState();
    onConnect({
      source: nodes[0].id,
      target: nodes[1].id,
      sourceHandle: null,
      targetHandle: null,
    });

    const errors = usePipelineStore.getState().validate();
    const configErrors = errors.filter((e) => e.type === "invalid-config");

    // datasource needs URL, AI needs prompt
    expect(configErrors.length).toBeGreaterThanOrEqual(2);
    expect(configErrors.some((e) => e.nodeId === nodes[0].id)).toBe(true);
    expect(configErrors.some((e) => e.nodeId === nodes[1].id)).toBe(true);
  });

  it("returns field name in config validation errors", () => {
    const { addNode } = usePipelineStore.getState();
    addNode("ai", { x: 0, y: 0 });
    addNode("action", { x: 200, y: 0 });

    const { nodes, onConnect } = usePipelineStore.getState();
    onConnect({
      source: nodes[0].id,
      target: nodes[1].id,
      sourceHandle: null,
      targetHandle: null,
    });

    const errors = usePipelineStore.getState().validate();
    const promptError = errors.find(
      (e) => e.type === "invalid-config" && e.field === "prompt",
    );

    expect(promptError).toBeDefined();
    expect(promptError!.nodeId).toBe(nodes[0].id);
  });

  it("passes config validation for action and human nodes with defaults", () => {
    const { addNode, updateNodeConfig } = usePipelineStore.getState();
    addNode("action", { x: 0, y: 0 });
    addNode("human", { x: 200, y: 0 });

    const { nodes, onConnect } = usePipelineStore.getState();
    onConnect({
      source: nodes[0].id,
      target: nodes[1].id,
      sourceHandle: null,
      targetHandle: null,
    });

    const errors = usePipelineStore.getState().validate();
    const configErrors = errors.filter((e) => e.type === "invalid-config");

    // Action and Human defaults are valid — no required text fields
    expect(configErrors).toHaveLength(0);
  });

  it("does not flag a valid DAG as having cycles", () => {
    const { addNode } = usePipelineStore.getState();
    addNode("datasource", { x: 0, y: 0 });
    addNode("ai", { x: 200, y: 0 });
    addNode("action", { x: 400, y: 0 });

    const { nodes, onConnect } = usePipelineStore.getState();
    // Linear chain: A → B → C (no cycle)
    onConnect({ source: nodes[0].id, target: nodes[1].id, sourceHandle: null, targetHandle: null });
    onConnect({ source: nodes[1].id, target: nodes[2].id, sourceHandle: null, targetHandle: null });

    const errors = usePipelineStore.getState().validate();
    const cycleErrors = errors.filter((e) => e.type === "cycle-detected");

    expect(cycleErrors).toHaveLength(0);
  });
});
