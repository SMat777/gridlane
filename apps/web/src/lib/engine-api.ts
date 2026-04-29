/**
 * Engine API client — communicates with the FastAPI backend.
 *
 * Pipeline CRUD stays in pipeline-api.ts (Supabase).
 * Pipeline EXECUTION goes through this client (engine).
 */

import type { PipelineRun } from "@gridlane/shared";

const ENGINE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface RunPipelineParams {
  pipeline: {
    id: string;
    name: string;
    nodes: Array<{
      id: string;
      type: string;
      position: { x: number; y: number };
      data: {
        label: string;
        nodeType: string;
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

/**
 * Execute a pipeline via the engine API.
 *
 * Sends the pipeline definition to POST /api/v1/runs and
 * returns the run result with per-step details.
 */
export async function runPipeline(
  params: RunPipelineParams,
): Promise<{ run: PipelineRun } | { error: string }> {
  try {
    const response = await fetch(`${ENGINE_URL}/api/v1/runs`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(params),
    });

    if (!response.ok) {
      const errorBody = await response.text();
      return { error: `Engine error (${response.status}): ${errorBody}` };
    }

    const data = await response.json();

    // Map snake_case API response to camelCase TypeScript types
    const run: PipelineRun = {
      id: data.run.id,
      pipelineId: data.run.pipeline_id,
      pipelineName: data.run.pipeline_name,
      status: data.run.status,
      totalDurationMs: data.run.total_duration_ms,
      totalCostUsd: data.run.total_cost_usd,
      startedAt: data.run.started_at,
      completedAt: data.run.completed_at,
      steps: data.run.steps.map(
        (s: Record<string, unknown>) => ({
          nodeId: s.node_id,
          nodeType: s.node_type,
          nodeLabel: s.node_label,
          status: s.status,
          order: s.order,
          input: s.input,
          output: s.output,
          error: s.error,
          startedAt: s.started_at,
          completedAt: s.completed_at,
          durationMs: s.duration_ms,
          tokenUsage: s.token_usage
            ? {
                inputTokens: (s.token_usage as Record<string, number>).input_tokens,
                outputTokens: (s.token_usage as Record<string, number>).output_tokens,
                totalTokens: (s.token_usage as Record<string, number>).total_tokens,
              }
            : undefined,
          costUsd: s.cost_usd,
        }),
      ),
    };

    return { run };
  } catch (err) {
    return {
      error: err instanceof Error ? err.message : "Failed to connect to engine",
    };
  }
}
