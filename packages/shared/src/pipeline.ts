/**
 * Pipeline type definitions — source of truth for the entire monorepo.
 *
 * These types define what a pipeline IS (structure),
 * not what it DOES (execution). Execution types come later.
 */

/** The four core node types in Gridlane */
export const PIPELINE_NODE_TYPES = [
  "datasource",
  "ai",
  "action",
  "human",
] as const;

export type PipelineNodeType = (typeof PIPELINE_NODE_TYPES)[number];

/** Data carried by each node on the canvas.
 *
 * The index signature [key: string]: unknown is required by React Flow v12
 * which expects node data to extend Record<string, unknown>.
 */
export interface PipelineNodeData {
  label: string;
  nodeType: PipelineNodeType;
  /** Configuration is intentionally minimal for US1.
   *  US2/US3 will add connector config, prompt templates, etc. */
  [key: string]: unknown;
}

/** A positioned node on the canvas (matches React Flow's Node shape) */
export interface PipelineNode {
  id: string;
  type: PipelineNodeType;
  position: { x: number; y: number };
  data: PipelineNodeData;
}

/** A directed edge between two nodes */
export interface PipelineEdge {
  id: string;
  source: string;
  target: string;
}

/** A complete pipeline definition — what gets saved/loaded */
export interface PipelineDefinition {
  id: string;
  name: string;
  nodes: PipelineNode[];
  edges: PipelineEdge[];
  createdAt: string;
  updatedAt: string;
}

/** Validation error for pipeline completeness checks */
export interface PipelineValidationError {
  nodeId?: string;
  type: "orphan-node" | "empty-pipeline" | "cycle-detected";
  message: string;
}

/** Display metadata for each node type */
export const NODE_TYPE_META: Record<
  PipelineNodeType,
  { label: string; color: string; icon: string; description: string }
> = {
  datasource: {
    label: "Data Source",
    color: "blue",
    icon: "database",
    description: "Fetch data from an external source",
  },
  ai: {
    label: "AI Analysis",
    color: "purple",
    icon: "sparkles",
    description: "Process data with an LLM",
  },
  action: {
    label: "Action",
    color: "green",
    icon: "zap",
    description: "Transform or output data",
  },
  human: {
    label: "Human Review",
    color: "orange",
    icon: "user",
    description: "Pause for human approval",
  },
};
