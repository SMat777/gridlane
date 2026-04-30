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

// ── Node Configuration Types ─────────────────────────────────────────
// Each node type has its own config shape. These are what the user
// fills in when clicking a node on the canvas.

export type DataSourceType = "rest" | "sql" | "file";
export type HttpMethod = "GET" | "POST" | "PUT" | "DELETE";
export type AuthType = "none" | "bearer" | "basic";

export interface DataSourceConfig {
  sourceType: DataSourceType;
  url: string;
  method: HttpMethod;
  headers: Record<string, string>;
  authType: AuthType;
}

export type AIProvider = "anthropic" | "openai";

export interface AIConfig {
  provider: AIProvider;
  model: string;
  prompt: string;
  temperature: number;
  maxTokens: number;
}

export type ActionType = "transform" | "output";
export type OutputFormat = "json" | "csv" | "text";

export interface ActionConfig {
  actionType: ActionType;
  outputFormat: OutputFormat;
}

export interface HumanConfig {
  instructions: string;
  requireComment: boolean;
}

/** Maps each node type to its config shape */
export interface NodeConfigMap {
  datasource: DataSourceConfig;
  ai: AIConfig;
  action: ActionConfig;
  human: HumanConfig;
}

/** Union of all config types */
export type NodeConfig = DataSourceConfig | AIConfig | ActionConfig | HumanConfig;

/** Default configs — used when a new node is created */
export const DEFAULT_NODE_CONFIGS: NodeConfigMap = {
  datasource: {
    sourceType: "rest",
    url: "",
    method: "GET",
    headers: {},
    authType: "none",
  },
  ai: {
    provider: "anthropic",
    model: "claude-sonnet-4-20250514",
    prompt: "",
    temperature: 0.7,
    maxTokens: 1024,
  },
  action: {
    actionType: "transform",
    outputFormat: "json",
  },
  human: {
    instructions: "",
    requireComment: false,
  },
};

/** Data carried by each node on the canvas.
 *
 * The index signature [key: string]: unknown is required by React Flow v12
 * which expects node data to extend Record<string, unknown>.
 */
export interface PipelineNodeData {
  label: string;
  nodeType: PipelineNodeType;
  /** Node-specific configuration. Populated with defaults on creation. */
  config?: NodeConfig;
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
  type: "orphan-node" | "empty-pipeline" | "cycle-detected" | "invalid-config";
  /** The specific config field that failed (for invalid-config errors) */
  field?: string;
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
