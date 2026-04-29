/**
 * Shared types and contracts between frontend and backend.
 * Node types, pipeline schemas, API response types.
 */

export const GRIDLANE_VERSION = "0.1.0";

export {
  PIPELINE_NODE_TYPES,
  NODE_TYPE_META,
  type PipelineNodeType,
  type PipelineNodeData,
  type PipelineNode,
  type PipelineEdge,
  type PipelineDefinition,
  type PipelineValidationError,
} from "./pipeline";
