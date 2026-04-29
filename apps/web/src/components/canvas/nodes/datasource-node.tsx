"use client";

import { Handle, Position, type NodeProps } from "@xyflow/react";
import { Database } from "lucide-react";
import type { CanvasNode } from "@/stores/pipeline-store";
import { BaseNode } from "./base-node";

/**
 * DataSource node — entry point of a pipeline.
 *
 * Only has a SOURCE handle (right side) because data flows OUT.
 * No target handle — nothing feeds into a data source.
 */
export function DataSourceNode({ data, selected }: NodeProps<CanvasNode>) {
  return (
    <BaseNode color="blue" selected={selected} isValid={data.isValid !== false}>
      <div className="flex items-center gap-2">
        <Database className="h-4 w-4 text-blue-600 dark:text-blue-400" />
        <span className="text-sm font-medium">{data.label}</span>
      </div>
      <Handle
        type="source"
        position={Position.Right}
        className="!h-3 !w-3 !border-2 !border-blue-500 !bg-white dark:!bg-gray-800"
      />
    </BaseNode>
  );
}
