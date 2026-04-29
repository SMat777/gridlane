import type { NodeTypes } from "@xyflow/react";
import { DataSourceNode } from "./datasource-node";
import { AINode } from "./ai-node";
import { ActionNode } from "./action-node";
import { HumanNode } from "./human-node";

/**
 * Node type registry — maps PipelineNodeType strings to React components.
 *
 * IMPORTANT: This object MUST be defined outside of any React component.
 * If defined inside a component, React Flow recreates it on every render,
 * which causes all nodes to unmount and remount — killing performance.
 */
export const nodeTypes: NodeTypes = {
  datasource: DataSourceNode,
  ai: AINode,
  action: ActionNode,
  human: HumanNode,
};

export { DataSourceNode, AINode, ActionNode, HumanNode };
