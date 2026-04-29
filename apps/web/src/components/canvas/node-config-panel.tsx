"use client";

import { useEffect } from "react";
import { X, Database, Sparkles, Zap, User } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { usePipelineStore } from "@/stores/pipeline-store";
import {
  DataSourceConfigForm,
  AIConfigForm,
  ActionConfigForm,
  HumanConfigForm,
} from "./config-forms";
import type {
  PipelineNodeType,
  DataSourceConfig,
  AIConfig,
  ActionConfig,
  HumanConfig,
  NodeConfig,
} from "@gridlane/shared";

/**
 * NodeConfigPanel — slides in from the right when a node is selected.
 *
 * Shows a header with the node icon + editable label, then the
 * node-type-specific configuration form. Changes are saved to the
 * Zustand store in real-time (no explicit save button needed).
 */

const ICONS: Record<PipelineNodeType, typeof Database> = {
  datasource: Database,
  ai: Sparkles,
  action: Zap,
  human: User,
};

const ICON_COLORS: Record<PipelineNodeType, string> = {
  datasource: "text-blue-600 dark:text-blue-400",
  ai: "text-purple-600 dark:text-purple-400",
  action: "text-green-600 dark:text-green-400",
  human: "text-orange-600 dark:text-orange-400",
};

const TYPE_LABELS: Record<PipelineNodeType, string> = {
  datasource: "Data Source",
  ai: "AI Analysis",
  action: "Action",
  human: "Human Review",
};

export function NodeConfigPanel() {
  const { nodes, selectedNodeId, selectNode, updateNodeConfig, updateNodeLabel } =
    usePipelineStore();

  // Close panel on Escape key
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        selectNode(null);
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [selectNode]);

  const selectedNode = nodes.find((n) => n.id === selectedNodeId);
  if (!selectedNode || !selectedNodeId) return null;

  const nodeType = selectedNode.data.nodeType;
  const config = selectedNode.data.config;
  const Icon = ICONS[nodeType];

  const handleConfigUpdate = (changes: Partial<NodeConfig>) => {
    updateNodeConfig(selectedNodeId, changes);
  };

  return (
    <aside
      className="flex w-80 flex-col border-l border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-950"
      role="complementary"
      aria-label="Node configuration"
    >
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-200 px-4 py-3 dark:border-gray-800">
        <div className="flex items-center gap-2">
          <Icon className={`h-4 w-4 ${ICON_COLORS[nodeType]}`} />
          <span className="text-sm font-semibold text-gray-500">
            {TYPE_LABELS[nodeType]}
          </span>
        </div>
        <button
          onClick={() => selectNode(null)}
          className="rounded-md p-1 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-800 dark:hover:text-gray-300"
          aria-label="Close configuration panel"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {/* Label — shared across all node types */}
        <div className="space-y-2">
          <Label htmlFor="nodeLabel">Label</Label>
          <Input
            id="nodeLabel"
            value={selectedNode.data.label}
            onChange={(e) => updateNodeLabel(selectedNodeId, e.target.value)}
          />
        </div>

        <Separator className="my-4" />

        {/* Node-type-specific config form */}
        {nodeType === "datasource" && config && (
          <DataSourceConfigForm
            config={config as DataSourceConfig}
            onUpdate={handleConfigUpdate}
          />
        )}

        {nodeType === "ai" && config && (
          <AIConfigForm
            config={config as AIConfig}
            onUpdate={handleConfigUpdate}
          />
        )}

        {nodeType === "action" && config && (
          <ActionConfigForm
            config={config as ActionConfig}
            onUpdate={handleConfigUpdate}
          />
        )}

        {nodeType === "human" && config && (
          <HumanConfigForm
            config={config as HumanConfig}
            onUpdate={handleConfigUpdate}
          />
        )}
      </div>
    </aside>
  );
}
