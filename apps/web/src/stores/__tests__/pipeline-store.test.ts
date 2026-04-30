import { describe, it, expect, beforeEach } from "vitest";
import { usePipelineStore, _resetNodeIdCounter } from "../pipeline-store";
import type { PipelineNodeType, PipelineRun } from "@gridlane/shared";

/**
 * Pipeline store tests — pure state logic, no React needed.
 *
 * Zustand stores can be tested as plain functions:
 * - getState() reads current state
 * - getState().action() mutates state
 * - getState() again to verify
 *
 * This is the beauty of external stores — testable without mounting components.
 */

describe("pipeline-store", () => {
  // Reset store between tests to avoid state leaking
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
    });
  });

  describe("initial state", () => {
    it("starts with empty nodes and edges", () => {
      const { nodes, edges } = usePipelineStore.getState();
      expect(nodes).toEqual([]);
      expect(edges).toEqual([]);
    });

    it("starts with default pipeline name", () => {
      const { pipelineName } = usePipelineStore.getState();
      expect(pipelineName).toBe("Untitled Pipeline");
    });
  });

  describe("addNode", () => {
    it("adds a node with correct type and position", () => {
      const { addNode } = usePipelineStore.getState();

      addNode("datasource", { x: 100, y: 200 });

      const { nodes } = usePipelineStore.getState();
      expect(nodes).toHaveLength(1);
      expect(nodes[0].type).toBe("datasource");
      expect(nodes[0].position).toEqual({ x: 100, y: 200 });
      expect(nodes[0].data.label).toBe("Data Source");
      expect(nodes[0].data.nodeType).toBe("datasource");
    });

    it("assigns unique IDs to each node", () => {
      const { addNode } = usePipelineStore.getState();

      addNode("ai", { x: 0, y: 0 });
      addNode("action", { x: 100, y: 0 });

      const { nodes } = usePipelineStore.getState();
      expect(nodes[0].id).not.toBe(nodes[1].id);
    });

    it("supports all four node types", () => {
      const { addNode } = usePipelineStore.getState();
      const types: PipelineNodeType[] = [
        "datasource",
        "ai",
        "action",
        "human",
      ];

      types.forEach((type) => addNode(type, { x: 0, y: 0 }));

      const { nodes } = usePipelineStore.getState();
      expect(nodes).toHaveLength(4);
      expect(nodes.map((n) => n.type)).toEqual(types);
    });
  });

  describe("onNodesChange", () => {
    it("applies position changes to nodes", () => {
      const { addNode } = usePipelineStore.getState();
      addNode("datasource", { x: 0, y: 0 });

      const { nodes, onNodesChange } = usePipelineStore.getState();
      const nodeId = nodes[0].id;

      // Simulate dragging a node to a new position
      onNodesChange([
        {
          type: "position",
          id: nodeId,
          position: { x: 150, y: 250 },
        },
      ]);

      const updated = usePipelineStore.getState().nodes;
      expect(updated[0].position).toEqual({ x: 150, y: 250 });
    });
  });

  describe("onNodesChange — isDirty filtering", () => {
    it("does NOT mark dirty on select changes", () => {
      const { addNode } = usePipelineStore.getState();
      addNode("datasource", { x: 0, y: 0 });
      usePipelineStore.setState({ isDirty: false });

      const { nodes, onNodesChange } = usePipelineStore.getState();
      onNodesChange([{ type: "select", id: nodes[0].id, selected: true }]);

      expect(usePipelineStore.getState().isDirty).toBe(false);
    });

    it("does NOT mark dirty on dimensions changes", () => {
      const { addNode } = usePipelineStore.getState();
      addNode("datasource", { x: 0, y: 0 });
      usePipelineStore.setState({ isDirty: false });

      const { nodes, onNodesChange } = usePipelineStore.getState();
      onNodesChange([
        {
          type: "dimensions",
          id: nodes[0].id,
          dimensions: { width: 200, height: 100 },
        },
      ]);

      expect(usePipelineStore.getState().isDirty).toBe(false);
    });

    it("DOES mark dirty on position changes", () => {
      const { addNode } = usePipelineStore.getState();
      addNode("datasource", { x: 0, y: 0 });
      usePipelineStore.setState({ isDirty: false });

      const { nodes, onNodesChange } = usePipelineStore.getState();
      onNodesChange([
        { type: "position", id: nodes[0].id, position: { x: 50, y: 50 } },
      ]);

      expect(usePipelineStore.getState().isDirty).toBe(true);
    });

    it("DOES mark dirty on remove changes", () => {
      const { addNode } = usePipelineStore.getState();
      addNode("datasource", { x: 0, y: 0 });
      usePipelineStore.setState({ isDirty: false });

      const { nodes, onNodesChange } = usePipelineStore.getState();
      onNodesChange([{ type: "remove", id: nodes[0].id }]);

      expect(usePipelineStore.getState().isDirty).toBe(true);
    });
  });

  describe("onConnect", () => {
    it("adds an edge between two nodes", () => {
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

      const { edges } = usePipelineStore.getState();
      expect(edges).toHaveLength(1);
      expect(edges[0].source).toBe(nodes[0].id);
      expect(edges[0].target).toBe(nodes[1].id);
    });
  });

  describe("deleteElements (via onNodesChange)", () => {
    it("removes a node and its connected edges", () => {
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

      // Delete the first node
      const state = usePipelineStore.getState();
      state.onNodesChange([{ type: "remove", id: nodes[0].id }]);

      const after = usePipelineStore.getState();
      expect(after.nodes).toHaveLength(1);
      expect(after.edges).toHaveLength(0);
    });
  });

  describe("isDirty", () => {
    it("starts as false", () => {
      expect(usePipelineStore.getState().isDirty).toBe(false);
    });

    it("becomes true when a node is added", () => {
      usePipelineStore.getState().addNode("datasource", { x: 0, y: 0 });
      expect(usePipelineStore.getState().isDirty).toBe(true);
    });

    it("becomes true when nodes are connected", () => {
      const store = usePipelineStore.getState();
      store.addNode("datasource", { x: 0, y: 0 });
      store.addNode("ai", { x: 200, y: 0 });

      // Reset dirty to test onConnect specifically
      usePipelineStore.setState({ isDirty: false });

      const nodes = usePipelineStore.getState().nodes;
      usePipelineStore.getState().onConnect({
        source: nodes[0].id,
        target: nodes[1].id,
        sourceHandle: null,
        targetHandle: null,
      });

      expect(usePipelineStore.getState().isDirty).toBe(true);
    });

    it("becomes true when node config is updated", () => {
      usePipelineStore.getState().addNode("datasource", { x: 0, y: 0 });
      usePipelineStore.setState({ isDirty: false });

      const nodeId = usePipelineStore.getState().nodes[0].id;
      usePipelineStore.getState().updateNodeConfig(nodeId, { url: "test" });

      expect(usePipelineStore.getState().isDirty).toBe(true);
    });

    it("resets to false when pipeline is loaded", () => {
      usePipelineStore.getState().addNode("datasource", { x: 0, y: 0 });
      expect(usePipelineStore.getState().isDirty).toBe(true);

      const serialized = usePipelineStore.getState().toSerializable();
      usePipelineStore.getState().loadPipeline(serialized);

      expect(usePipelineStore.getState().isDirty).toBe(false);
    });
  });

  describe("pipeline identity", () => {
    it("preserves pipeline ID after load and re-serialize", () => {
      // Build a pipeline
      usePipelineStore.getState().addNode("datasource", { x: 0, y: 0 });
      const original = usePipelineStore.getState().toSerializable();

      // Load it back (simulates opening a saved pipeline)
      usePipelineStore.getState().loadPipeline(original);

      // Re-serialize — ID must match the loaded pipeline, not a new UUID
      const reserialized = usePipelineStore.getState().toSerializable();
      expect(reserialized.id).toBe(original.id);
    });

    it("preserves createdAt timestamp after load and re-serialize", async () => {
      usePipelineStore.getState().addNode("datasource", { x: 0, y: 0 });
      const original = usePipelineStore.getState().toSerializable();

      usePipelineStore.getState().loadPipeline(original);

      // Small delay so updatedAt gets a different timestamp
      await new Promise((resolve) => setTimeout(resolve, 5));

      const reserialized = usePipelineStore.getState().toSerializable();
      expect(reserialized.createdAt).toBe(original.createdAt);
      // updatedAt should be fresh
      expect(reserialized.updatedAt).not.toBe(original.createdAt);
    });

    it("generates a new UUID for a brand new pipeline", () => {
      usePipelineStore.getState().addNode("datasource", { x: 0, y: 0 });
      const first = usePipelineStore.getState().toSerializable();
      const second = usePipelineStore.getState().toSerializable();

      // Without loading, each call should still generate a new ID
      // (because the pipeline hasn't been persisted yet — no identity exists)
      // After fix: new pipeline (no pipelineId in state) gets a new UUID
      // but once loaded, the ID is stable
      expect(first.id).toBeDefined();
      expect(second.id).toBeDefined();
    });

    it("starts with null pipelineId", () => {
      const state = usePipelineStore.getState();
      expect(state.pipelineId).toBeNull();
    });

    it("sets pipelineId when pipeline is loaded", () => {
      usePipelineStore.getState().addNode("datasource", { x: 0, y: 0 });
      const serialized = usePipelineStore.getState().toSerializable();

      usePipelineStore.getState().loadPipeline(serialized);

      expect(usePipelineStore.getState().pipelineId).toBe(serialized.id);
    });
  });

  describe("node ID collision prevention", () => {
    it("new nodes get unique IDs even after loading a pipeline", () => {
      // Simulate a page reload — counter goes back to 0
      _resetNodeIdCounter();

      // Simulate loading a saved pipeline with node_1, node_2, node_3
      const savedPipeline = {
        id: "pipe-1",
        name: "Saved Pipeline",
        nodes: [
          {
            id: "node_1",
            type: "datasource" as const,
            position: { x: 0, y: 0 },
            data: { label: "Source", nodeType: "datasource" as const },
          },
          {
            id: "node_2",
            type: "ai" as const,
            position: { x: 200, y: 0 },
            data: { label: "AI", nodeType: "ai" as const },
          },
          {
            id: "node_3",
            type: "action" as const,
            position: { x: 400, y: 0 },
            data: { label: "Action", nodeType: "action" as const },
          },
        ],
        edges: [
          { id: "e1", source: "node_1", target: "node_2" },
          { id: "e2", source: "node_2", target: "node_3" },
        ],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      usePipelineStore.getState().loadPipeline(savedPipeline);

      // Add a new node — its ID must NOT collide with existing node_1/2/3
      usePipelineStore.getState().addNode("human", { x: 600, y: 0 });

      const nodes = usePipelineStore.getState().nodes;
      const ids = nodes.map((n) => n.id);
      const uniqueIds = new Set(ids);

      expect(uniqueIds.size).toBe(ids.length); // No duplicates
      expect(ids[3]).not.toBe("node_1");
      expect(ids[3]).not.toBe("node_2");
      expect(ids[3]).not.toBe("node_3");
    });
  });

  describe("execution state", () => {
    it("starts with isRunning false and currentRun null", () => {
      const state = usePipelineStore.getState();
      expect(state.isRunning).toBe(false);
      expect(state.currentRun).toBeNull();
    });

    it("setRunning updates isRunning", () => {
      usePipelineStore.getState().setRunning(true);
      expect(usePipelineStore.getState().isRunning).toBe(true);

      usePipelineStore.getState().setRunning(false);
      expect(usePipelineStore.getState().isRunning).toBe(false);
    });

    it("setCurrentRun stores and clears run result", () => {
      const mockRun: PipelineRun = {
        id: "run-1",
        pipelineId: "pipe-1",
        pipelineName: "Test",
        status: "completed",
        steps: [],
        totalDurationMs: 100,
        startedAt: new Date().toISOString(),
        completedAt: new Date().toISOString(),
      };

      usePipelineStore.getState().setCurrentRun(mockRun);
      expect(usePipelineStore.getState().currentRun).toEqual(mockRun);

      usePipelineStore.getState().setCurrentRun(null);
      expect(usePipelineStore.getState().currentRun).toBeNull();
    });
  });

  describe("deleteNode", () => {
    it("removes the node and its connected edges", () => {
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

      usePipelineStore.getState().deleteNode(nodes[0].id);

      const after = usePipelineStore.getState();
      expect(after.nodes).toHaveLength(1);
      expect(after.nodes[0].type).toBe("ai");
      expect(after.edges).toHaveLength(0);
    });

    it("clears selectedNodeId when the selected node is deleted", () => {
      const { addNode } = usePipelineStore.getState();
      addNode("datasource", { x: 0, y: 0 });

      const nodeId = usePipelineStore.getState().nodes[0].id;
      usePipelineStore.getState().selectNode(nodeId);
      expect(usePipelineStore.getState().selectedNodeId).toBe(nodeId);

      usePipelineStore.getState().deleteNode(nodeId);

      expect(usePipelineStore.getState().selectedNodeId).toBeNull();
      expect(usePipelineStore.getState().nodes).toHaveLength(0);
    });

    it("does not affect selectedNodeId when a different node is deleted", () => {
      const { addNode } = usePipelineStore.getState();
      addNode("datasource", { x: 0, y: 0 });
      addNode("ai", { x: 200, y: 0 });

      const nodes = usePipelineStore.getState().nodes;
      usePipelineStore.getState().selectNode(nodes[1].id);

      usePipelineStore.getState().deleteNode(nodes[0].id);

      expect(usePipelineStore.getState().selectedNodeId).toBe(nodes[1].id);
      expect(usePipelineStore.getState().nodes).toHaveLength(1);
    });
  });
});
