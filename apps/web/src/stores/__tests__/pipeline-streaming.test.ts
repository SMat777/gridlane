import { describe, it, expect, beforeEach } from "vitest";
import { usePipelineStore } from "../pipeline-store";

/**
 * Streaming-state actions: initRun / upsertStepResult / finalizeRun.
 *
 * These actions are wired to SSE events from the engine. We test them
 * here as pure state transitions — no network, no EventSource. The
 * integration with the SSE client lives in pipeline-toolbar.tsx and is
 * exercised manually + via end-to-end testing.
 */

describe("pipeline-store streaming actions", () => {
  beforeEach(() => {
    usePipelineStore.setState({
      nodes: [],
      edges: [],
      pipelineName: "Untitled Pipeline",
      pipelineId: null,
      pipelineCreatedAt: null,
      selectedNodeId: null,
      isDirty: false,
      isRunning: false,
      currentRun: null,
      activeRunId: null,
    });
  });

  describe("initRun", () => {
    it("creates an empty run with status=running", () => {
      usePipelineStore.getState().initRun({
        runId: "run-1",
        pipelineId: "pipe-1",
        pipelineName: "Demo Pipeline",
        startedAt: "2026-04-30T22:00:00Z",
      });

      const { currentRun, activeRunId } = usePipelineStore.getState();
      expect(activeRunId).toBe("run-1");
      expect(currentRun).not.toBeNull();
      expect(currentRun?.status).toBe("running");
      expect(currentRun?.steps).toEqual([]);
      expect(currentRun?.pipelineName).toBe("Demo Pipeline");
    });
  });

  describe("upsertStepResult", () => {
    beforeEach(() => {
      usePipelineStore.getState().initRun({
        runId: "run-1",
        pipelineId: "pipe-1",
        pipelineName: "Demo",
        startedAt: "2026-04-30T22:00:00Z",
      });
    });

    it("adds a new step on first event for a node", () => {
      usePipelineStore.getState().upsertStepResult({
        nodeId: "node_1",
        nodeType: "datasource",
        nodeLabel: "Source",
        status: "running",
        order: 0,
        startedAt: "2026-04-30T22:00:01Z",
      });

      const steps = usePipelineStore.getState().currentRun?.steps ?? [];
      expect(steps).toHaveLength(1);
      expect(steps[0].nodeId).toBe("node_1");
      expect(steps[0].status).toBe("running");
    });

    it("updates an existing step on subsequent events", () => {
      usePipelineStore.getState().upsertStepResult({
        nodeId: "node_1",
        nodeType: "datasource",
        nodeLabel: "Source",
        status: "running",
        order: 0,
        startedAt: "2026-04-30T22:00:01Z",
      });
      usePipelineStore.getState().upsertStepResult({
        nodeId: "node_1",
        status: "completed",
        completedAt: "2026-04-30T22:00:02Z",
        durationMs: 1000,
        output: { data: 42 },
      });

      const steps = usePipelineStore.getState().currentRun?.steps ?? [];
      expect(steps).toHaveLength(1);
      expect(steps[0].status).toBe("completed");
      expect(steps[0].durationMs).toBe(1000);
      expect(steps[0].output).toEqual({ data: 42 });
      // Preserved fields from first event
      expect(steps[0].nodeLabel).toBe("Source");
    });

    it("preserves order when multiple steps stream in", () => {
      usePipelineStore.getState().upsertStepResult({
        nodeId: "node_1",
        order: 0,
        status: "completed",
      });
      usePipelineStore.getState().upsertStepResult({
        nodeId: "node_2",
        order: 1,
        status: "running",
      });

      const steps = usePipelineStore.getState().currentRun?.steps ?? [];
      expect(steps.map((s) => s.nodeId)).toEqual(["node_1", "node_2"]);
    });

    it("is a no-op when no run is active", () => {
      usePipelineStore.setState({ currentRun: null });
      usePipelineStore.getState().upsertStepResult({
        nodeId: "ghost",
        status: "running",
      });
      expect(usePipelineStore.getState().currentRun).toBeNull();
    });
  });

  describe("finalizeRun", () => {
    beforeEach(() => {
      usePipelineStore.getState().initRun({
        runId: "run-1",
        pipelineId: "pipe-1",
        pipelineName: "Demo",
        startedAt: "2026-04-30T22:00:00Z",
      });
      usePipelineStore.setState({ isRunning: true });
    });

    it("sets terminal status and clears running flags", () => {
      usePipelineStore.getState().finalizeRun({
        status: "completed",
        totalDurationMs: 1500,
        totalCostUsd: 0.012,
        completedAt: "2026-04-30T22:00:03Z",
      });

      const state = usePipelineStore.getState();
      expect(state.currentRun?.status).toBe("completed");
      expect(state.currentRun?.totalDurationMs).toBe(1500);
      expect(state.currentRun?.totalCostUsd).toBe(0.012);
      expect(state.isRunning).toBe(false);
      expect(state.activeRunId).toBeNull();
    });

    it("supports failed and cancelled terminal states", () => {
      usePipelineStore.getState().finalizeRun({
        status: "cancelled",
        totalDurationMs: 500,
        completedAt: "2026-04-30T22:00:01Z",
      });
      expect(usePipelineStore.getState().currentRun?.status).toBe("cancelled");

      usePipelineStore.getState().initRun({
        runId: "run-2",
        pipelineId: "pipe-1",
        pipelineName: "Demo",
        startedAt: "2026-04-30T23:00:00Z",
      });
      usePipelineStore.getState().finalizeRun({
        status: "failed",
        totalDurationMs: 100,
      });
      expect(usePipelineStore.getState().currentRun?.status).toBe("failed");
    });

    it("is a no-op when no run is active", () => {
      usePipelineStore.setState({ currentRun: null, isRunning: false });
      usePipelineStore.getState().finalizeRun({ status: "completed" });
      expect(usePipelineStore.getState().currentRun).toBeNull();
    });
  });
});
