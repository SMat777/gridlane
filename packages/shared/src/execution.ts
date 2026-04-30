/**
 * Pipeline execution types — what happens when a pipeline RUNS.
 *
 * pipeline.ts defines what a pipeline IS (structure).
 * This file defines what happens when it EXECUTES.
 *
 * Key concepts:
 * - PipelineRun: a single execution of a pipeline
 * - StepResult: what happened at one node during a run
 * - RunStatus: the lifecycle state of a run or step
 */

import type { PipelineNodeType } from "./pipeline";

// ── Run Status ───────────────────────────────────────────────────────

/** Lifecycle states for runs and steps */
export type RunStatus =
  | "pending"    // Queued, not yet started
  | "running"    // Currently executing
  | "completed"  // Finished successfully
  | "failed"     // Finished with error
  | "cancelled"; // Stopped by user

// ── Step Result ──────────────────────────────────────────────────────

/** Result of executing a single node in the pipeline */
export interface StepResult {
  /** Which node this step corresponds to */
  nodeId: string;
  /** Node type for display purposes */
  nodeType: PipelineNodeType;
  /** Node label at time of execution */
  nodeLabel: string;
  /** Execution status */
  status: RunStatus;
  /** Step execution order (0-indexed) */
  order: number;

  /** Input data received from upstream node(s) */
  input: unknown;
  /** Output data produced by this step */
  output: unknown;
  /** Error message if status is "failed" */
  error?: string;

  /** When this step started (ISO 8601) */
  startedAt: string;
  /** When this step finished (ISO 8601) */
  completedAt?: string;
  /** Duration in milliseconds */
  durationMs?: number;

  /** Token usage for AI nodes */
  tokenUsage?: {
    inputTokens: number;
    outputTokens: number;
    totalTokens: number;
  };
  /** Estimated cost in USD for AI nodes */
  costUsd?: number;
}

// ── Pipeline Run ─────────────────────────────────────────────────────

/** A single execution of a pipeline */
export interface PipelineRun {
  /** Unique run ID */
  id: string;
  /** Which pipeline was executed */
  pipelineId: string;
  /** Pipeline name at time of execution */
  pipelineName: string;
  /** Overall run status */
  status: RunStatus;

  /** Results for each step, ordered by execution sequence */
  steps: StepResult[];

  /** Total execution time in milliseconds */
  totalDurationMs?: number;
  /** Total cost in USD (sum of all step costs) */
  totalCostUsd?: number;

  /** When the run was triggered (ISO 8601) */
  startedAt: string;
  /** When the run finished (ISO 8601) */
  completedAt?: string;
}

// ── API Request/Response Types ───────────────────────────────────────

/** Request body for POST /api/v1/pipelines/run */
export interface RunPipelineRequest {
  /** The pipeline definition to execute */
  pipeline: {
    id: string;
    name: string;
    nodes: Array<{
      id: string;
      type: PipelineNodeType;
      position: { x: number; y: number };
      data: {
        label: string;
        nodeType: PipelineNodeType;
        config?: Record<string, unknown>;
      };
    }>;
    edges: Array<{
      id: string;
      source: string;
      target: string;
    }>;
  };
}

/** Response body for POST /api/v1/pipelines/run */
export interface RunPipelineResponse {
  run: PipelineRun;
}

/** Response body for GET /api/v1/runs */
export interface RunHistoryResponse {
  runs: PipelineRun[];
}

/** Response body for GET /api/v1/runs/:id */
export interface RunDetailResponse {
  run: PipelineRun;
}

// ── SSE Event Types ──────────────────────────────────────────────────

/** Event names emitted on the SSE stream */
export type RunEventType =
  | "run_started"
  | "step_started"
  | "step_completed"
  | "step_failed"
  | "run_completed"
  | "run_failed"
  | "run_cancelled";

/** A single decoded SSE event from the run stream */
export interface RunStreamEvent {
  /** Per-run sequence id (used for Last-Event-ID resume) */
  id: number;
  type: RunEventType;
  /** Type-specific JSON payload — see docs/specs/sse-progress.md */
  payload: Record<string, unknown>;
}

/** Response body for POST /api/v1/runs/async */
export interface RunAsyncResponse {
  run_id: string;
  status: RunStatus;
  stream_url: string;
}

/** Response body for POST /api/v1/runs/:id/cancel */
export interface CancelRunResponse {
  run_id: string;
  status: RunStatus | "cancelling";
}
