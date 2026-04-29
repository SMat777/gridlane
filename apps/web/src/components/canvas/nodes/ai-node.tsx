"use client";

import { Handle, Position, type NodeProps } from "@xyflow/react";
import { Sparkles } from "lucide-react";
import type { CanvasNode } from "@/stores/pipeline-store";
import { BaseNode } from "./base-node";

/**
 * AI node — processes data with an LLM.
 *
 * Has both TARGET (left, data in) and SOURCE (right, result out) handles.
 */
export function AINode({ data, selected }: NodeProps<CanvasNode>) {
  return (
    <BaseNode color="purple" selected={selected}>
      <Handle
        type="target"
        position={Position.Left}
        className="!h-3 !w-3 !border-2 !border-purple-500 !bg-white dark:!bg-gray-800"
      />
      <div className="flex items-center gap-2">
        <Sparkles className="h-4 w-4 text-purple-600 dark:text-purple-400" />
        <span className="text-sm font-medium">{data.label}</span>
      </div>
      <Handle
        type="source"
        position={Position.Right}
        className="!h-3 !w-3 !border-2 !border-purple-500 !bg-white dark:!bg-gray-800"
      />
    </BaseNode>
  );
}
