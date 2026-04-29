"use client";

import { Database, Sparkles, Zap, User } from "lucide-react";
import {
  PIPELINE_NODE_TYPES,
  NODE_TYPE_META,
  type PipelineNodeType,
} from "@gridlane/shared";
import type { ComponentType } from "react";
import type { LucideProps } from "lucide-react";

/**
 * Node palette — sidebar with draggable node types.
 *
 * Uses the native HTML Drag and Drop API:
 * 1. User drags an item from the palette
 * 2. onDragStart stores the node type in dataTransfer
 * 3. Canvas catches it in onDrop → reads the type → creates a node
 *
 * This is the same pattern React Flow's official docs recommend.
 */

const iconMap: Record<PipelineNodeType, ComponentType<LucideProps>> = {
  datasource: Database,
  ai: Sparkles,
  action: Zap,
  human: User,
};

const colorMap: Record<PipelineNodeType, string> = {
  datasource: "border-blue-300 bg-blue-50 hover:bg-blue-100 dark:border-blue-700 dark:bg-blue-950 dark:hover:bg-blue-900",
  ai: "border-purple-300 bg-purple-50 hover:bg-purple-100 dark:border-purple-700 dark:bg-purple-950 dark:hover:bg-purple-900",
  action: "border-green-300 bg-green-50 hover:bg-green-100 dark:border-green-700 dark:bg-green-950 dark:hover:bg-green-900",
  human: "border-orange-300 bg-orange-50 hover:bg-orange-100 dark:border-orange-700 dark:bg-orange-950 dark:hover:bg-orange-900",
};

function onDragStart(event: React.DragEvent, nodeType: PipelineNodeType) {
  event.dataTransfer.setData("application/reactflow", nodeType);
  event.dataTransfer.effectAllowed = "move";
}

export function NodePalette() {
  return (
    <aside className="flex w-56 flex-col gap-2 border-r border-gray-200 bg-gray-50 p-4 dark:border-gray-800 dark:bg-gray-950">
      <h2 className="mb-2 text-xs font-semibold uppercase tracking-wider text-gray-500">
        Nodes
      </h2>
      {PIPELINE_NODE_TYPES.map((type) => {
        const meta = NODE_TYPE_META[type];
        const Icon = iconMap[type];
        return (
          <div
            key={type}
            draggable
            onDragStart={(e) => onDragStart(e, type)}
            className={`flex cursor-grab items-center gap-2 rounded-md border px-3 py-2 text-sm transition-colors active:cursor-grabbing ${colorMap[type]}`}
            role="button"
            aria-label={`Drag ${meta.label} node to canvas`}
          >
            <Icon className="h-4 w-4 shrink-0" />
            <div>
              <div className="font-medium">{meta.label}</div>
              <div className="text-xs text-gray-500 dark:text-gray-400">
                {meta.description}
              </div>
            </div>
          </div>
        );
      })}
    </aside>
  );
}
