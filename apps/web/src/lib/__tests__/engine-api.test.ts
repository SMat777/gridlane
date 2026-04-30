import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { runPipeline } from "../engine-api";

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
});
