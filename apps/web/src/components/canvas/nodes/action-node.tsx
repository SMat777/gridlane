"use client";

import { Handle, Position, type NodeProps } from "@xyflow/react";
import { Zap } from "lucide-react";
import type { CanvasNode } from "@/stores/pipeline-store";
import { BaseNode } from "./base-node";

/**
 * Action node — transforms or outputs data.
 *
 * Has both TARGET (left) and SOURCE (right) handles.
 */
export function ActionNode({ data, selected }: NodeProps<CanvasNode>) {
  return (
    <BaseNode color="green" selected={selected}>
      <Handle
        type="target"
        position={Position.Left}
        className="!h-3 !w-3 !border-2 !border-green-500 !bg-white dark:!bg-gray-800"
      />
      <div className="flex items-center gap-2">
        <Zap className="h-4 w-4 text-green-600 dark:text-green-400" />
        <span className="text-sm font-medium">{data.label}</span>
      </div>
      <Handle
        type="source"
        position={Position.Right}
        className="!h-3 !w-3 !border-2 !border-green-500 !bg-white dark:!bg-gray-800"
      />
    </BaseNode>
  );
}
