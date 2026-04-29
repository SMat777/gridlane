import { describe, it, expect, beforeEach } from "vitest";
import { usePipelineStore } from "../pipeline-store";
import { DEFAULT_NODE_CONFIGS, type DataSourceConfig, type AIConfig } from "@gridlane/shared";

describe("Node Configuration", () => {
  beforeEach(() => {
    // Reset store between tests
    usePipelineStore.setState({
      nodes: [],
      edges: [],
      pipelineName: "Untitled Pipeline",
      selectedNodeId: null,
    });
  });

  describe("addNode with default config", () => {
    it("creates a datasource node with default config", () => {
      const store = usePipelineStore.getState();
      store.addNode("datasource", { x: 100, y: 100 });

      const nodes = usePipelineStore.getState().nodes;
      expect(nodes).toHaveLength(1);
      expect(nodes[0].data.config).toEqual(DEFAULT_NODE_CONFIGS.datasource);
    });

    it("creates an AI node with default config", () => {
      const store = usePipelineStore.getState();
      store.addNode("ai", { x: 100, y: 100 });

      const nodes = usePipelineStore.getState().nodes;
      expect(nodes[0].data.config).toEqual(DEFAULT_NODE_CONFIGS.ai);
    });

    it("creates an action node with default config", () => {
      const store = usePipelineStore.getState();
      store.addNode("action", { x: 100, y: 100 });

      const nodes = usePipelineStore.getState().nodes;
      expect(nodes[0].data.config).toEqual(DEFAULT_NODE_CONFIGS.action);
    });

    it("creates a human node with default config", () => {
      const store = usePipelineStore.getState();
      store.addNode("human", { x: 100, y: 100 });

      const nodes = usePipelineStore.getState().nodes;
      expect(nodes[0].data.config).toEqual(DEFAULT_NODE_CONFIGS.human);
    });
  });

  describe("selectNode", () => {
    it("sets selectedNodeId when a node is selected", () => {
      const store = usePipelineStore.getState();
      store.addNode("datasource", { x: 100, y: 100 });
      const nodeId = usePipelineStore.getState().nodes[0].id;

      store.selectNode(nodeId);
      expect(usePipelineStore.getState().selectedNodeId).toBe(nodeId);
    });

    it("clears selectedNodeId when null is passed", () => {
      const store = usePipelineStore.getState();
      store.addNode("datasource", { x: 100, y: 100 });
      const nodeId = usePipelineStore.getState().nodes[0].id;

      store.selectNode(nodeId);
      store.selectNode(null);
      expect(usePipelineStore.getState().selectedNodeId).toBeNull();
    });

    it("returns null for selectedNodeId when no node is selected", () => {
      expect(usePipelineStore.getState().selectedNodeId).toBeNull();
    });
  });

  describe("updateNodeConfig", () => {
    it("updates datasource config fields", () => {
      const store = usePipelineStore.getState();
      store.addNode("datasource", { x: 100, y: 100 });
      const nodeId = usePipelineStore.getState().nodes[0].id;

      store.updateNodeConfig(nodeId, {
        url: "https://api.example.com/data",
        method: "POST",
      });

      const config = usePipelineStore.getState().nodes[0].data
        .config as DataSourceConfig;
      expect(config.url).toBe("https://api.example.com/data");
      expect(config.method).toBe("POST");
      // Unchanged fields should remain at defaults
      expect(config.sourceType).toBe("rest");
      expect(config.authType).toBe("none");
    });

    it("updates AI config fields", () => {
      const store = usePipelineStore.getState();
      store.addNode("ai", { x: 100, y: 100 });
      const nodeId = usePipelineStore.getState().nodes[0].id;

      store.updateNodeConfig(nodeId, {
        prompt: "Analyze this data: {{ input }}",
        temperature: 0.3,
      });

      const config = usePipelineStore.getState().nodes[0].data
        .config as AIConfig;
      expect(config.prompt).toBe("Analyze this data: {{ input }}");
      expect(config.temperature).toBe(0.3);
      expect(config.provider).toBe("anthropic"); // unchanged default
    });

    it("updates node label", () => {
      const store = usePipelineStore.getState();
      store.addNode("datasource", { x: 100, y: 100 });
      const nodeId = usePipelineStore.getState().nodes[0].id;

      store.updateNodeLabel(nodeId, "My API Source");

      expect(usePipelineStore.getState().nodes[0].data.label).toBe(
        "My API Source",
      );
    });

    it("does nothing for a non-existent node", () => {
      const store = usePipelineStore.getState();
      store.addNode("datasource", { x: 100, y: 100 });

      // Should not throw
      store.updateNodeConfig("non-existent", { url: "test" });

      // Original node unchanged
      const config = usePipelineStore.getState().nodes[0].data
        .config as DataSourceConfig;
      expect(config.url).toBe("");
    });
  });

  describe("serialization with config", () => {
    it("toSerializable includes node config", () => {
      const store = usePipelineStore.getState();
      store.addNode("ai", { x: 100, y: 100 });
      const nodeId = usePipelineStore.getState().nodes[0].id;

      store.updateNodeConfig(nodeId, {
        prompt: "Summarize: {{ input }}",
      });

      const serialized = usePipelineStore.getState().toSerializable();
      const config = serialized.nodes[0].data.config as AIConfig;
      expect(config.prompt).toBe("Summarize: {{ input }}");
      expect(config.provider).toBe("anthropic");
    });

    it("loadPipeline restores node config", () => {
      const store = usePipelineStore.getState();
      store.addNode("datasource", { x: 200, y: 300 });
      const nodeId = usePipelineStore.getState().nodes[0].id;

      store.updateNodeConfig(nodeId, {
        url: "https://api.example.com",
        method: "POST",
      });

      const serialized = usePipelineStore.getState().toSerializable();

      // Reset and reload
      usePipelineStore.setState({ nodes: [], edges: [] });
      usePipelineStore.getState().loadPipeline(serialized);

      const config = usePipelineStore.getState().nodes[0].data
        .config as DataSourceConfig;
      expect(config.url).toBe("https://api.example.com");
      expect(config.method).toBe("POST");
    });
  });
});
