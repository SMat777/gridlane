/**
 * Shared types and contracts between frontend and backend.
 * Node types, pipeline schemas, API response types.
 */

export const GRIDLANE_VERSION = "0.1.0";

export {
  PIPELINE_NODE_TYPES,
  NODE_TYPE_META,
  DEFAULT_NODE_CONFIGS,
  type PipelineNodeType,
  type PipelineNodeData,
  type PipelineNode,
  type PipelineEdge,
  type PipelineDefinition,
  type PipelineValidationError,
  type DataSourceConfig,
  type DataSourceType,
  type HttpMethod,
  type AuthType,
  type AIConfig,
  type AIProvider,
  type ActionConfig,
  type ActionType,
  type OutputFormat,
  type HumanConfig,
  type NodeConfigMap,
  type NodeConfig,
} from "./pipeline";

export {
  type RunStatus,
  type StepResult,
  type PipelineRun,
  type RunPipelineRequest,
  type RunPipelineResponse,
  type RunHistoryResponse,
  type RunDetailResponse,
} from "./execution";
