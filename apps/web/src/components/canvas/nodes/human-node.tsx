"use client";

import { Handle, Position, type NodeProps } from "@xyflow/react";
import { User } from "lucide-react";
import type { CanvasNode } from "@/stores/pipeline-store";
import { BaseNode } from "./base-node";

/**
 * Human node — approval gate that pauses pipeline execution.
 *
 * Has both TARGET (left) and SOURCE (right) handles.
 * Visual distinction: orange color signals "human required here".
 */
export function HumanNode({ data, selected }: NodeProps<CanvasNode>) {
  return (
    <BaseNode color="orange" selected={selected} isValid={data.isValid !== false}>
      <Handle
        type="target"
        position={Position.Left}
        className="!h-3 !w-3 !border-2 !border-orange-500 !bg-white dark:!bg-gray-800"
      />
      <div className="flex items-center gap-2">
        <User className="h-4 w-4 text-orange-600 dark:text-orange-400" />
        <span className="text-sm font-medium">{data.label}</span>
      </div>
      <Handle
        type="source"
        position={Position.Right}
        className="!h-3 !w-3 !border-2 !border-orange-500 !bg-white dark:!bg-gray-800"
      />
    </BaseNode>
  );
}
