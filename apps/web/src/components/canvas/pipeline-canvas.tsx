"use client";

import { useCallback } from "react";
import {
  ReactFlow,
  ReactFlowProvider,
  Background,
  Controls,
  MiniMap,
  useReactFlow,
  type IsValidConnection,
  getOutgoers,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { usePipelineStore } from "@/stores/pipeline-store";
import type { CanvasNode } from "@/stores/pipeline-store";
import { nodeTypes } from "./nodes";
import { NodePalette } from "./node-palette";
import { PipelineToolbar } from "./pipeline-toolbar";
import type { PipelineNodeType } from "@gridlane/shared";

/**
 * Pipeline Canvas — the core visual editor.
 *
 * Architecture:
 * - State lives in Zustand store (pipeline-store.ts)
 * - React Flow is the "view" that renders that state
 * - Callbacks in the store handle all mutations
 * - This component only wires them together
 *
 * Drag-and-drop flow:
 * 1. User drags from NodePalette → sets dataTransfer type
 * 2. onDragOver → preventDefault (allows drop)
 * 3. onDrop → reads type → screenToFlowPosition → addNode in store
 */

function PipelineCanvasInner() {
  const { nodes, edges, onNodesChange, onEdgesChange, onConnect, addNode } =
    usePipelineStore();
  const { screenToFlowPosition, getNodes, getEdges } = useReactFlow();

  // Prevent cycles — a pipeline is a DAG (Directed Acyclic Graph)
  const isValidConnection: IsValidConnection = useCallback(
    (connection) => {
      const nodes = getNodes() as CanvasNode[];
      const edges = getEdges();
      const target = nodes.find((n) => n.id === connection.target);
      if (!target) return false;

      // No self-connections
      if (connection.source === connection.target) return false;

      // Check for cycles using DFS
      const hasCycle = (node: CanvasNode, visited = new Set<string>()): boolean => {
        if (visited.has(node.id)) return false;
        visited.add(node.id);
        const outgoers = getOutgoers(node, nodes, edges);
        for (const outgoer of outgoers) {
          if (outgoer.id === connection.source) return true;
          if (hasCycle(outgoer as CanvasNode, visited)) return true;
        }
        return false;
      };

      return !hasCycle(target);
    },
    [getNodes, getEdges],
  );

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();

      const type = event.dataTransfer.getData("application/reactflow") as PipelineNodeType;
      if (!type) return;

      // screenToFlowPosition accounts for viewport transform (zoom, pan)
      const position = screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });

      addNode(type, position);
    },
    [screenToFlowPosition, addNode],
  );

  return (
    <div className="flex h-full w-full">
      <NodePalette />
      <div className="relative flex flex-1 flex-col">
        <PipelineToolbar />
        <div className="flex-1">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onDrop={onDrop}
          onDragOver={onDragOver}
          nodeTypes={nodeTypes}
          isValidConnection={isValidConnection}
          fitView
          deleteKeyCode={["Backspace", "Delete"]}
          className="bg-gray-100 dark:bg-gray-900"
        >
          <Background />
          <Controls />
          <MiniMap
            nodeColor={(node) => {
              const colorMap: Record<string, string> = {
                datasource: "#60a5fa",
                ai: "#a78bfa",
                action: "#4ade80",
                human: "#fb923c",
              };
              return colorMap[node.type ?? ""] ?? "#94a3b8";
            }}
          />
        </ReactFlow>
        </div>
      </div>
    </div>
  );
}

/**
 * PipelineCanvas — wrapped in ReactFlowProvider.
 *
 * ReactFlowProvider is required for useReactFlow() hook to work.
 * It must wrap the component that USES the hook, not the one that
 * RENDERS <ReactFlow>. We keep them in the same file for clarity.
 */
export function PipelineCanvas() {
  return (
    <ReactFlowProvider>
      <PipelineCanvasInner />
    </ReactFlowProvider>
  );
}
