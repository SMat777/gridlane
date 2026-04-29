import { describe, it, expect, beforeEach } from "vitest";
import { usePipelineStore } from "../pipeline-store";
import type { PipelineNodeType } from "@gridlane/shared";

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

  describe("deleteElements", () => {
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
});
