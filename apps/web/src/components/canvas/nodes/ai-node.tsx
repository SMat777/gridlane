"use client";

import { Handle, Position, type NodeProps } from "@xyflow/react";
import { Sparkles } from "lucide-react";
import type { CanvasNode } from "@/stores/pipeline-store";
import { BaseNode } from "./base-node";
import type { AIConfig } from "@gridlane/shared";

/**
 * AI node — processes data with an LLM.
 *
 * Has both TARGET (left, data in) and SOURCE (right, result out) handles.
 */

const MODEL_SHORT_NAMES: Record<string, string> = {
  "claude-sonnet-4-20250514": "Sonnet 4",
  "claude-haiku-4-20250514": "Haiku 4",
  "gpt-4o": "GPT-4o",
  "gpt-4o-mini": "GPT-4o Mini",
};

export function AINode({ data, selected }: NodeProps<CanvasNode>) {
  const config = data.config as AIConfig | undefined;
  const modelName = config?.model
    ? MODEL_SHORT_NAMES[config.model] ?? config.model
    : null;

  return (
    <BaseNode color="purple" selected={selected} isValid={data.isValid !== false}>
      <Handle
        type="target"
        position={Position.Left}
        className="!h-3 !w-3 !border-2 !border-purple-500 !bg-white dark:!bg-gray-800"
      />
      <div className="flex items-center gap-2">
        <Sparkles className="h-4 w-4 text-purple-600 dark:text-purple-400" />
        <span className="text-sm font-medium">{data.label}</span>
      </div>
      {modelName && (
        <div className="mt-1 text-xs text-gray-500 dark:text-gray-400">
          {modelName}
        </div>
      )}
      <Handle
        type="source"
        position={Position.Right}
        className="!h-3 !w-3 !border-2 !border-purple-500 !bg-white dark:!bg-gray-800"
      />
    </BaseNode>
  );
}
