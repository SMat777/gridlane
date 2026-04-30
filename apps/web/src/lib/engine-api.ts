/**
 * Engine API client — communicates with the FastAPI backend.
 *
 * Pipeline CRUD stays in pipeline-api.ts (Supabase).
 * Pipeline EXECUTION goes through this client (engine).
 */

import type {
  CancelRunResponse,
  PipelineRun,
  RunAsyncResponse,
  RunStreamEvent,
} from "@gridlane/shared";

const ENGINE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/** SSE event types we expect from the engine */
const RUN_EVENT_TYPES = [
  "run_started",
  "step_started",
  "step_completed",
  "step_failed",
  "run_completed",
  "run_failed",
  "run_cancelled",
] as const;

const TERMINAL_EVENT_TYPES = new Set<string>([
  "run_completed",
  "run_failed",
  "run_cancelled",
]);

/** Request timeout in milliseconds. Engine has a 120s execution timeout,
 *  so 30s for the HTTP round-trip is generous for normal operations. */
const REQUEST_TIMEOUT_MS = 30_000;

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
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const response = await fetch(`${ENGINE_URL}/api/v1/runs`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(params),
      signal: controller.signal,
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
    if (err instanceof DOMException && err.name === "AbortError") {
      return { error: "Request timeout — engine did not respond in time" };
    }
    return {
      error: err instanceof Error ? err.message : "Failed to connect to engine",
    };
  } finally {
    clearTimeout(timeoutId);
  }
}

/**
 * Launch a pipeline run asynchronously and stream live progress events.
 *
 * Returns immediately after the launch request resolves with the run_id,
 * then opens an EventSource that calls onEvent for each progress event
 * until a terminal event arrives or the caller signals abort.
 *
 * EventSource handles auto-reconnect on transient network failure. We
 * pass Last-Event-ID via the URL query string (browser EventSource can't
 * set arbitrary headers) so resume works on reconnect.
 */
export async function runPipelineStreaming(
  params: RunPipelineParams,
  onEvent: (event: RunStreamEvent) => void,
  signal?: AbortSignal,
): Promise<{ runId: string } | { error: string }> {
  // Step 1: launch the run
  const launchController = new AbortController();
  const timeoutId = setTimeout(() => launchController.abort(), REQUEST_TIMEOUT_MS);

  let launchResponse: RunAsyncResponse;
  try {
    const response = await fetch(`${ENGINE_URL}/api/v1/runs/async`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(params),
      signal: launchController.signal,
    });
    if (!response.ok) {
      return { error: `Engine error (${response.status}): ${await response.text()}` };
    }
    launchResponse = await response.json();
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
      return { error: "Request timeout — engine did not respond in time" };
    }
    return {
      error: err instanceof Error ? err.message : "Failed to launch run",
    };
  } finally {
    clearTimeout(timeoutId);
  }

  const runId = launchResponse.run_id;
  let lastEventId = -1;

  // Step 2: open EventSource and forward events
  const openStream = (resumeFrom: number): EventSource => {
    const url = new URL(`${ENGINE_URL}${launchResponse.stream_url}`);
    if (resumeFrom >= 0) {
      url.searchParams.set("after", String(resumeFrom));
    }
    const source = new EventSource(url.toString());
    for (const eventType of RUN_EVENT_TYPES) {
      source.addEventListener(eventType, (e) => {
        const messageEvent = e as MessageEvent;
        const sequence = Number(messageEvent.lastEventId);
        if (Number.isFinite(sequence)) lastEventId = sequence;
        let payload: Record<string, unknown> = {};
        try {
          payload = JSON.parse(messageEvent.data);
        } catch {
          // Defensive: malformed payload — skip rather than crash UI
        }
        onEvent({ id: lastEventId, type: eventType, payload });
        if (TERMINAL_EVENT_TYPES.has(eventType)) {
          source.close();
        }
      });
    }
    source.addEventListener("error", () => {
      // Browser auto-reconnects unless the connection is intentionally closed.
      // If we hit a hard error after terminal, there's nothing to resume.
    });
    return source;
  };

  const source = openStream(lastEventId);

  signal?.addEventListener("abort", () => {
    source.close();
  });

  // Caller resolves immediately; events flow through onEvent
  void source;
  return { runId };
}

/**
 * Request cancellation of a running pipeline.
 *
 * Returns the post-call status. Cancellation is cooperative — the current
 * step is allowed to finish before the run terminates.
 */
export async function cancelRun(
  runId: string,
): Promise<{ status: string } | { error: string }> {
  try {
    const response = await fetch(`${ENGINE_URL}/api/v1/runs/${runId}/cancel`, {
      method: "POST",
    });
    if (!response.ok) {
      return { error: `Engine error (${response.status}): ${await response.text()}` };
    }
    const data: CancelRunResponse = await response.json();
    return { status: data.status };
  } catch (err) {
    return {
      error: err instanceof Error ? err.message : "Failed to cancel run",
    };
  }
}
