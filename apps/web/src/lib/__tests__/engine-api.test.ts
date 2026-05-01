import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { runPipeline, listRuns, getRun } from "../engine-api";

/** Minimal valid pipeline for testing — structure matters, not content */
const TEST_PIPELINE = {
  id: "pipe-1",
  name: "Test",
  nodes: [
    {
      id: "node_1",
      type: "datasource",
      position: { x: 0, y: 0 },
      data: { label: "Source", nodeType: "datasource" },
    },
  ],
  edges: [],
};

describe("engine-api", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  describe("timeout and abort", () => {
    it("aborts the request after timeout and returns an error", async () => {
      // Mock fetch that hangs forever but respects the AbortSignal —
      // just like a real browser fetch would reject when aborted.
      vi.stubGlobal(
        "fetch",
        vi.fn(
          (_url: string, options?: RequestInit) =>
            new Promise((_resolve, reject) => {
              options?.signal?.addEventListener("abort", () => {
                reject(new DOMException("The operation was aborted.", "AbortError"));
              });
            }),
        ),
      );

      const resultPromise = runPipeline({ pipeline: TEST_PIPELINE });

      // Advance past the 30s timeout
      await vi.advanceTimersByTimeAsync(31_000);

      const result = await resultPromise;
      expect(result).toHaveProperty("error");
      expect((result as { error: string }).error).toMatch(/timeout/i);
    });

    it("returns run result when engine responds before timeout", async () => {
      const mockResponse = {
        run: {
          id: "run-1",
          pipeline_id: "pipe-1",
          pipeline_name: "Test",
          status: "completed",
          steps: [],
          total_duration_ms: 50,
          started_at: new Date().toISOString(),
          completed_at: new Date().toISOString(),
        },
      };

      vi.stubGlobal(
        "fetch",
        vi.fn(() =>
          Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockResponse),
          }),
        ),
      );

      const result = await runPipeline({ pipeline: TEST_PIPELINE });
      expect(result).toHaveProperty("run");
      expect((result as { run: { id: string } }).run.id).toBe("run-1");
    });

    it("passes an AbortSignal to fetch", async () => {
      vi.stubGlobal(
        "fetch",
        vi.fn(() =>
          Promise.resolve({
            ok: true,
            json: () =>
              Promise.resolve({
                run: {
                  id: "run-1",
                  pipeline_id: "pipe-1",
                  pipeline_name: "Test",
                  status: "completed",
                  steps: [],
                  started_at: new Date().toISOString(),
                },
              }),
          }),
        ),
      );

      await runPipeline({ pipeline: TEST_PIPELINE });

      const fetchCall = (fetch as ReturnType<typeof vi.fn>).mock.calls[0];
      const options = fetchCall[1];
      expect(options).toHaveProperty("signal");
      expect(options.signal).toBeInstanceOf(AbortSignal);
    });
  });

  describe("listRuns", () => {
    beforeEach(() => {
      vi.useRealTimers();
    });

    it("maps snake_case API response to camelCase RunSummary", async () => {
      vi.stubGlobal(
        "fetch",
        vi.fn(() =>
          Promise.resolve({
            ok: true,
            json: () =>
              Promise.resolve({
                runs: [
                  {
                    id: "run-1",
                    pipeline_id: "pipe-1",
                    pipeline_name: "Test",
                    status: "completed",
                    total_duration_ms: 120,
                    total_cost_usd: 0.0042,
                    started_at: "2026-04-30T10:00:00Z",
                    completed_at: "2026-04-30T10:00:01Z",
                    step_count: 3,
                  },
                ],
              }),
          }),
        ),
      );

      const result = await listRuns();
      expect(result).toHaveProperty("runs");
      const runs = (result as { runs: unknown[] }).runs;
      expect(runs).toHaveLength(1);
      expect(runs[0]).toMatchObject({
        id: "run-1",
        pipelineId: "pipe-1",
        pipelineName: "Test",
        status: "completed",
        totalDurationMs: 120,
        totalCostUsd: 0.0042,
        stepCount: 3,
      });
    });

    it("forwards pagination params as query string", async () => {
      const fetchMock = vi.fn((_url: string) =>
        Promise.resolve({ ok: true, json: () => Promise.resolve({ runs: [] }) }),
      );
      vi.stubGlobal("fetch", fetchMock);

      await listRuns({ pipelineId: "pipe-1", limit: 25, offset: 50 });

      const url = new URL(fetchMock.mock.calls[0][0]);
      expect(url.searchParams.get("pipeline_id")).toBe("pipe-1");
      expect(url.searchParams.get("limit")).toBe("25");
      expect(url.searchParams.get("offset")).toBe("50");
    });

    it("returns an error when the engine responds non-OK", async () => {
      vi.stubGlobal(
        "fetch",
        vi.fn(() =>
          Promise.resolve({
            ok: false,
            status: 503,
            text: () => Promise.resolve("Service unavailable"),
          }),
        ),
      );

      const result = await listRuns();
      expect(result).toHaveProperty("error");
      expect((result as { error: string }).error).toMatch(/503/);
    });

    it("returns an empty list when the engine sends no runs key", async () => {
      vi.stubGlobal(
        "fetch",
        vi.fn(() =>
          Promise.resolve({ ok: true, json: () => Promise.resolve({}) }),
        ),
      );

      const result = await listRuns();
      expect(result).toEqual({ runs: [] });
    });
  });

  describe("getRun", () => {
    beforeEach(() => {
      vi.useRealTimers();
    });

    it("maps a full run with steps to camelCase PipelineRun", async () => {
      vi.stubGlobal(
        "fetch",
        vi.fn(() =>
          Promise.resolve({
            ok: true,
            json: () =>
              Promise.resolve({
                run: {
                  id: "run-1",
                  pipeline_id: "pipe-1",
                  pipeline_name: "Test",
                  status: "completed",
                  total_duration_ms: 50,
                  total_cost_usd: null,
                  started_at: "2026-04-30T10:00:00Z",
                  completed_at: "2026-04-30T10:00:01Z",
                  steps: [
                    {
                      node_id: "n1",
                      node_type: "datasource",
                      node_label: "Source",
                      status: "completed",
                      order: 0,
                      input: null,
                      output: { rows: 3 },
                      error: null,
                      started_at: "2026-04-30T10:00:00Z",
                      completed_at: "2026-04-30T10:00:00.5Z",
                      duration_ms: 500,
                      token_usage: null,
                      cost_usd: null,
                    },
                  ],
                },
              }),
          }),
        ),
      );

      const result = await getRun("run-1");
      expect(result).toHaveProperty("run");
      const run = (result as { run: { steps: unknown[] } }).run;
      expect(run).toMatchObject({
        id: "run-1",
        pipelineName: "Test",
        status: "completed",
        totalCostUsd: undefined,
      });
      expect(run.steps).toHaveLength(1);
      expect(run.steps[0]).toMatchObject({
        nodeId: "n1",
        nodeLabel: "Source",
        durationMs: 500,
        output: { rows: 3 },
      });
    });

    it("returns an error on 404", async () => {
      vi.stubGlobal(
        "fetch",
        vi.fn(() =>
          Promise.resolve({
            ok: false,
            status: 404,
            text: () => Promise.resolve("Run not found"),
          }),
        ),
      );

      const result = await getRun("missing");
      expect(result).toHaveProperty("error");
      expect((result as { error: string }).error).toMatch(/404/);
    });

    it("returns an error when fetch rejects", async () => {
      vi.stubGlobal(
        "fetch",
        vi.fn(() => Promise.reject(new Error("network down"))),
      );

      const result = await getRun("run-1");
      expect(result).toEqual({ error: "network down" });
    });
  });
});
