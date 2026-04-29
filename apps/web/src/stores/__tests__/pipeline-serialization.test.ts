import { describe, it, expect, beforeEach } from "vitest";
import { usePipelineStore } from "../pipeline-store";

/**
 * Serialization tests — can we save and restore a pipeline?
 *
 * toSerializable() converts live canvas state → JSON-safe object.
 * loadPipeline() restores canvas state from a saved pipeline.
 *
 * This is the bridge between Zustand (runtime) and Supabase (persistence).
 * If serialization breaks, save/load breaks — that's an acceptance criteria.
 */

describe("pipeline serialization", () => {
  beforeEach(() => {
    usePipelineStore.setState({
      nodes: [],
      edges: [],
      pipelineName: "Untitled Pipeline",
    });
  });

  describe("toSerializable", () => {
    it("returns a valid pipeline definition", () => {
      const { addNode } = usePipelineStore.getState();
      addNode("datasource", { x: 100, y: 50 });
      addNode("ai", { x: 300, y: 50 });

      const { nodes, onConnect } = usePipelineStore.getState();
      onConnect({
        source: nodes[0].id,
        target: nodes[1].id,
        sourceHandle: null,
        targetHandle: null,
      });

      const pipeline = usePipelineStore.getState().toSerializable();

      expect(pipeline.name).toBe("Untitled Pipeline");
      expect(pipeline.nodes).toHaveLength(2);
      expect(pipeline.edges).toHaveLength(1);
      expect(pipeline.id).toBeDefined();
      expect(pipeline.createdAt).toBeDefined();
      expect(pipeline.updatedAt).toBeDefined();
    });

    it("serializes node positions and types", () => {
      const { addNode } = usePipelineStore.getState();
      addNode("human", { x: 42, y: 99 });

      const pipeline = usePipelineStore.getState().toSerializable();

      expect(pipeline.nodes[0].type).toBe("human");
      expect(pipeline.nodes[0].position).toEqual({ x: 42, y: 99 });
      expect(pipeline.nodes[0].data.label).toBe("Human Review");
    });

    it("produces valid JSON", () => {
      const { addNode } = usePipelineStore.getState();
      addNode("action", { x: 0, y: 0 });

      const pipeline = usePipelineStore.getState().toSerializable();
      const json = JSON.stringify(pipeline);
      const parsed = JSON.parse(json);

      expect(parsed.nodes).toHaveLength(1);
    });
  });

  describe("loadPipeline", () => {
    it("restores nodes and edges from a saved pipeline", () => {
      // First: build a pipeline
      const { addNode } = usePipelineStore.getState();
      addNode("datasource", { x: 100, y: 50 });
      addNode("ai", { x: 300, y: 50 });
      const { nodes, onConnect } = usePipelineStore.getState();
      onConnect({
        source: nodes[0].id,
        target: nodes[1].id,
        sourceHandle: null,
        targetHandle: null,
      });

      // Save it
      const saved = usePipelineStore.getState().toSerializable();

      // Clear state
      usePipelineStore.setState({ nodes: [], edges: [] });

      // Load it back
      usePipelineStore.getState().loadPipeline(saved);

      const restored = usePipelineStore.getState();
      expect(restored.nodes).toHaveLength(2);
      expect(restored.edges).toHaveLength(1);
      expect(restored.pipelineName).toBe(saved.name);
    });

    it("preserves node types after load", () => {
      const { addNode } = usePipelineStore.getState();
      addNode("datasource", { x: 0, y: 0 });
      addNode("human", { x: 200, y: 0 });

      const saved = usePipelineStore.getState().toSerializable();
      usePipelineStore.setState({ nodes: [], edges: [] });
      usePipelineStore.getState().loadPipeline(saved);

      const { nodes } = usePipelineStore.getState();
      expect(nodes[0].type).toBe("datasource");
      expect(nodes[1].type).toBe("human");
    });
  });
});
