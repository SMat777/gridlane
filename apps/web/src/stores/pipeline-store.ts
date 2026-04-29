import { create } from "zustand";
import {
  applyNodeChanges,
  applyEdgeChanges,
  addEdge,
  type Node,
  type Edge,
  type OnNodesChange,
  type OnEdgesChange,
  type OnConnect,
} from "@xyflow/react";
import {
  NODE_TYPE_META,
  type PipelineNodeType,
  type PipelineNodeData,
  type PipelineValidationError,
  type PipelineDefinition,
} from "@gridlane/shared";

/**
 * Canvas node type — extends React Flow's Node with our PipelineNodeData.
 * This is what React Flow renders. The shared PipelineNode type is for
 * serialization/persistence — this type is for the live canvas.
 */
export type CanvasNode = Node<PipelineNodeData, PipelineNodeType>;
export type CanvasEdge = Edge;

interface PipelineState {
  // State
  nodes: CanvasNode[];
  edges: CanvasEdge[];
  pipelineName: string;

  // React Flow callbacks — these wire directly to <ReactFlow> props
  onNodesChange: OnNodesChange<CanvasNode>;
  onEdgesChange: OnEdgesChange<CanvasEdge>;
  onConnect: OnConnect;

  // Actions
  addNode: (type: PipelineNodeType, position: { x: number; y: number }) => void;
  validate: () => PipelineValidationError[];
  runValidation: () => PipelineValidationError[];
  toSerializable: () => PipelineDefinition;
  loadPipeline: (pipeline: PipelineDefinition) => void;
}

/** Counter for unique node IDs within a session */
let nodeIdCounter = 0;
const nextNodeId = () => `node_${++nodeIdCounter}`;

export const usePipelineStore = create<PipelineState>((set, get) => ({
  nodes: [],
  edges: [],
  pipelineName: "Untitled Pipeline",

  onNodesChange: (changes) => {
    const updatedNodes = applyNodeChanges(changes, get().nodes);

    // When nodes are removed, also remove their connected edges
    const removedIds = changes
      .filter((c) => c.type === "remove")
      .map((c) => c.id);

    if (removedIds.length > 0) {
      const updatedEdges = get().edges.filter(
        (e) => !removedIds.includes(e.source) && !removedIds.includes(e.target),
      );
      set({ nodes: updatedNodes, edges: updatedEdges });
    } else {
      set({ nodes: updatedNodes });
    }
  },

  onEdgesChange: (changes) => {
    set({ edges: applyEdgeChanges(changes, get().edges) });
  },

  onConnect: (connection) => {
    set({ edges: addEdge(connection, get().edges) });
  },

  addNode: (type, position) => {
    const meta = NODE_TYPE_META[type];
    const newNode: CanvasNode = {
      id: nextNodeId(),
      type,
      position,
      data: {
        label: meta.label,
        nodeType: type,
      },
    };
    set({ nodes: [...get().nodes, newNode] });
  },

  validate: () => {
    const { nodes, edges } = get();
    const errors: PipelineValidationError[] = [];

    // Empty pipeline — nothing to validate
    if (nodes.length === 0) {
      errors.push({
        type: "empty-pipeline",
        message: "Pipeline has no nodes",
      });
      return errors;
    }

    // Find orphan nodes — nodes with no connections at all
    const connectedNodeIds = new Set<string>();
    for (const edge of edges) {
      connectedNodeIds.add(edge.source);
      connectedNodeIds.add(edge.target);
    }

    for (const node of nodes) {
      if (!connectedNodeIds.has(node.id)) {
        errors.push({
          nodeId: node.id,
          type: "orphan-node",
          message: `Node "${node.data.label}" has no connections`,
        });
      }
    }

    return errors;
  },

  runValidation: () => {
    const errors = get().validate();

    // Mark invalid nodes visually by updating their data
    const invalidNodeIds = new Set(
      errors.filter((e) => e.nodeId).map((e) => e.nodeId!),
    );

    const updatedNodes = get().nodes.map((node) => ({
      ...node,
      data: {
        ...node.data,
        isValid: !invalidNodeIds.has(node.id),
      },
    }));

    set({ nodes: updatedNodes });
    return errors;
  },

  toSerializable: () => {
    const { nodes, edges, pipelineName } = get();
    const now = new Date().toISOString();
    return {
      id: crypto.randomUUID(),
      name: pipelineName,
      nodes: nodes.map((n) => ({
        id: n.id,
        type: n.type as PipelineNodeType,
        position: n.position,
        data: { label: n.data.label, nodeType: n.data.nodeType },
      })),
      edges: edges.map((e) => ({
        id: e.id,
        source: e.source,
        target: e.target,
      })),
      createdAt: now,
      updatedAt: now,
    };
  },

  loadPipeline: (pipeline) => {
    const canvasNodes: CanvasNode[] = pipeline.nodes.map((n) => ({
      id: n.id,
      type: n.type,
      position: n.position,
      data: { label: n.data.label, nodeType: n.data.nodeType },
    }));

    const canvasEdges: CanvasEdge[] = pipeline.edges.map((e) => ({
      id: e.id,
      source: e.source,
      target: e.target,
    }));

    set({
      nodes: canvasNodes,
      edges: canvasEdges,
      pipelineName: pipeline.name,
    });
  },
}));
