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
}));
