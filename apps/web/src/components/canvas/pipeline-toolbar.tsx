"use client";

import { useRef, useState } from "react";
import {
  Save,
  FolderOpen,
  Plus,
  CheckCircle,
  Play,
  Square,
  History,
} from "lucide-react";
import { toast } from "sonner";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { ThemeToggle } from "@/components/theme-toggle";
import { usePipelineStore } from "@/stores/pipeline-store";
import { savePipeline, listPipelines, loadPipeline } from "@/lib/pipeline-api";
import { runPipelineStreaming, cancelRun } from "@/lib/engine-api";
import { RunHistoryPanel } from "./run-history-panel";

/**
 * Pipeline toolbar — save, load, validate, and new pipeline actions.
 *
 * Sits at the top of the canvas. Uses Sonner toast for user feedback
 * instead of inline status text — gives richer, dismissable messages.
 */
export function PipelineToolbar() {
  // Granular selectors for state — only re-render when these specific values change
  const pipelineName = usePipelineStore((s) => s.pipelineName);
  const isDirty = usePipelineStore((s) => s.isDirty);
  const isRunning = usePipelineStore((s) => s.isRunning);
  const activeRunId = usePipelineStore((s) => s.activeRunId);

  // Actions are stable references — safe to destructure from store directly
  const {
    toSerializable,
    runValidation,
    setRunning,
    setCurrentRun,
    loadPipeline: loadPipelineToStore,
    initRun,
    upsertStepResult,
    finalizeRun,
  } = usePipelineStore.getState();
  const [saving, setSaving] = useState(false);
  const streamAbortRef = useRef<AbortController | null>(null);
  const [showLoadDialog, setShowLoadDialog] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [confirmAction, setConfirmAction] = useState<(() => void) | null>(null);
  const [pipelines, setPipelines] = useState<
    Array<{ id: string; name: string; updatedAt: string }>
  >([]);
  const [loading, setLoading] = useState(false);

  /** Runs an action immediately if no unsaved changes, or shows confirmation dialog */
  const guardUnsavedChanges = (action: () => void) => {
    if (isDirty) {
      setConfirmAction(() => action);
    } else {
      action();
    }
  };

  const handleSave = async () => {
    setSaving(true);

    const pipeline = toSerializable();
    const result = await savePipeline(pipeline);

    if ("error" in result) {
      toast.error("Failed to save pipeline", {
        description: result.error,
      });
    } else {
      toast.success("Pipeline saved");
      usePipelineStore.setState({ isDirty: false });
    }
    setSaving(false);
  };

  const executeLoadList = async () => {
    setLoading(true);
    const result = await listPipelines();

    if ("error" in result) {
      toast.error("Failed to load pipelines", {
        description: result.error,
      });
      setLoading(false);
      return;
    }

    setPipelines(result);
    setShowLoadDialog(true);
    setLoading(false);
  };

  const handleLoadList = () => guardUnsavedChanges(() => { executeLoadList(); });

  const handleLoad = async (id: string) => {
    setLoading(true);
    const result = await loadPipeline(id);

    if ("error" in result) {
      toast.error("Failed to load pipeline", {
        description: result.error,
      });
    } else {
      loadPipelineToStore(result);
      toast.success("Pipeline loaded");
    }
    setShowLoadDialog(false);
    setLoading(false);
  };

  const handleRun = async () => {
    // Validate first
    const errors = runValidation();
    if (errors.length > 0) {
      toast.warning("Fix pipeline issues before running", {
        description: errors.map((e) => e.message).join("\n"),
      });
      return;
    }

    setRunning(true);
    setCurrentRun(null);

    const abortController = new AbortController();
    streamAbortRef.current = abortController;

    const pipeline = toSerializable();
    const result = await runPipelineStreaming(
      {
        pipeline: pipeline as unknown as Parameters<
          typeof runPipelineStreaming
        >[0]["pipeline"],
      },
      (event) => {
        const payload = event.payload as Record<string, unknown>;
        switch (event.type) {
          case "run_started":
            initRun({
              runId: String(payload.run_id ?? ""),
              pipelineId: String(payload.pipeline_id ?? ""),
              pipelineName: String(payload.pipeline_name ?? pipeline.name),
              startedAt: String(payload.started_at ?? new Date().toISOString()),
            });
            break;
          case "step_started":
          case "step_completed":
          case "step_failed":
            upsertStepResult({
              nodeId: String(payload.node_id ?? ""),
              nodeType: payload.node_type as
                | "datasource"
                | "ai"
                | "action"
                | "human"
                | undefined,
              nodeLabel:
                typeof payload.node_label === "string" ? payload.node_label : undefined,
              status:
                event.type === "step_started"
                  ? "running"
                  : event.type === "step_completed"
                    ? "completed"
                    : "failed",
              order:
                typeof payload.order === "number" ? payload.order : undefined,
              startedAt:
                typeof payload.started_at === "string"
                  ? payload.started_at
                  : undefined,
              completedAt:
                typeof payload.completed_at === "string"
                  ? payload.completed_at
                  : undefined,
              durationMs:
                typeof payload.duration_ms === "number"
                  ? payload.duration_ms
                  : undefined,
              output: "output" in payload ? payload.output : undefined,
              error:
                typeof payload.error === "string" ? payload.error : undefined,
            });
            break;
          case "run_completed":
          case "run_failed":
          case "run_cancelled":
            finalizeRun({
              status:
                event.type === "run_completed"
                  ? "completed"
                  : event.type === "run_failed"
                    ? "failed"
                    : "cancelled",
              totalDurationMs:
                typeof payload.total_duration_ms === "number"
                  ? payload.total_duration_ms
                  : undefined,
              totalCostUsd:
                typeof payload.total_cost_usd === "number"
                  ? payload.total_cost_usd
                  : undefined,
              completedAt:
                typeof payload.completed_at === "string"
                  ? payload.completed_at
                  : new Date().toISOString(),
            });
            if (event.type === "run_completed") {
              toast.success("Pipeline completed");
            } else if (event.type === "run_failed") {
              toast.error("Pipeline failed", {
                description:
                  typeof payload.error === "string" ? payload.error : undefined,
              });
            } else {
              toast.info("Pipeline cancelled");
            }
            break;
        }
      },
      abortController.signal,
    );

    if ("error" in result) {
      toast.error("Pipeline execution failed", { description: result.error });
      setRunning(false);
      streamAbortRef.current = null;
    }
    // On success the stream callbacks drive state until a terminal event
    // arrives, which calls finalizeRun() and resets isRunning + activeRunId.
  };

  const handleStop = async () => {
    if (!activeRunId) return;
    const result = await cancelRun(activeRunId);
    if ("error" in result) {
      toast.error("Cancel failed", { description: result.error });
    } else {
      toast.info("Cancellation requested — current step will finish first");
    }
  };

  const handleValidate = () => {
    const errors = runValidation();
    if (errors.length === 0) {
      toast.success("Pipeline is valid");
    } else {
      toast.warning(`${errors.length} issue${errors.length > 1 ? "s" : ""} found`, {
        description: errors.map((e) => e.message).join("\n"),
      });
    }
  };

  const executeNew = () => {
    usePipelineStore.setState({
      nodes: [],
      edges: [],
      pipelineName: "Untitled Pipeline",
      selectedNodeId: null,
      isDirty: false,
    });
  };

  const handleNew = () => guardUnsavedChanges(executeNew);

  return (
    <>
      <div className="flex items-center gap-2 border-b border-gray-200 bg-white px-4 py-2 dark:border-gray-800 dark:bg-gray-950">
        <h1 className="text-sm font-semibold text-gray-700 dark:text-gray-300">
          {pipelineName}
        </h1>

        <div className="ml-auto flex items-center gap-2">
          <ThemeToggle />

          <button
            onClick={handleNew}
            className="flex items-center gap-1 rounded-md border border-gray-200 px-3 py-1.5 text-xs text-gray-600 transition-colors hover:bg-gray-100 dark:border-gray-700 dark:text-gray-400 dark:hover:bg-gray-800"
            aria-label="New pipeline"
          >
            <Plus className="h-3.5 w-3.5" />
            New
          </button>

          <button
            onClick={handleLoadList}
            disabled={loading}
            className="flex items-center gap-1 rounded-md border border-gray-200 px-3 py-1.5 text-xs text-gray-600 transition-colors hover:bg-gray-100 disabled:opacity-50 dark:border-gray-700 dark:text-gray-400 dark:hover:bg-gray-800"
            aria-label="Load pipeline"
          >
            <FolderOpen className="h-3.5 w-3.5" />
            Load
          </button>

          <button
            onClick={() => setShowHistory(true)}
            className="flex items-center gap-1 rounded-md border border-gray-200 px-3 py-1.5 text-xs text-gray-600 transition-colors hover:bg-gray-100 dark:border-gray-700 dark:text-gray-400 dark:hover:bg-gray-800"
            aria-label="Show run history"
          >
            <History className="h-3.5 w-3.5" />
            History
          </button>

          <button
            onClick={handleValidate}
            className="flex items-center gap-1 rounded-md border border-gray-200 px-3 py-1.5 text-xs text-gray-600 transition-colors hover:bg-gray-100 dark:border-gray-700 dark:text-gray-400 dark:hover:bg-gray-800"
            aria-label="Validate pipeline"
          >
            <CheckCircle className="h-3.5 w-3.5" />
            Validate
          </button>

          <button
            onClick={handleSave}
            disabled={saving}
            className="flex items-center gap-1 rounded-md bg-blue-600 px-3 py-1.5 text-xs text-white transition-colors hover:bg-blue-700 disabled:opacity-50"
            aria-label="Save pipeline"
          >
            <Save className="h-3.5 w-3.5" />
            {saving ? "Saving..." : "Save"}
          </button>

          {isRunning ? (
            <button
              onClick={handleStop}
              className="flex items-center gap-1 rounded-md bg-red-600 px-3 py-1.5 text-xs text-white transition-colors hover:bg-red-700"
              aria-label="Stop pipeline"
            >
              <Square className="h-3.5 w-3.5" />
              Stop
            </button>
          ) : (
            <button
              onClick={handleRun}
              className="flex items-center gap-1 rounded-md bg-green-600 px-3 py-1.5 text-xs text-white transition-colors hover:bg-green-700"
              aria-label="Run pipeline"
            >
              <Play className="h-3.5 w-3.5" />
              Run
            </button>
          )}
        </div>
      </div>

      {/* Unsaved changes confirmation */}
      <AlertDialog open={confirmAction !== null} onOpenChange={(open) => { if (!open) setConfirmAction(null); }}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Unsaved changes</AlertDialogTitle>
            <AlertDialogDescription>
              You have unsaved changes that will be lost. Do you want to continue?
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => {
                confirmAction?.();
                setConfirmAction(null);
              }}
            >
              Discard changes
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <RunHistoryPanel open={showHistory} onOpenChange={setShowHistory} />

      {/* Simple load dialog */}
      {showLoadDialog && (
        <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-96 rounded-lg bg-white p-6 shadow-xl dark:bg-gray-900">
            <h2 className="mb-4 text-lg font-semibold">Load Pipeline</h2>
            {pipelines.length === 0 ? (
              <p className="text-sm text-gray-500">No saved pipelines found.</p>
            ) : (
              <ul className="max-h-64 space-y-2 overflow-y-auto">
                {pipelines.map((p) => (
                  <li key={p.id}>
                    <button
                      onClick={() => handleLoad(p.id)}
                      className="w-full rounded-md border border-gray-200 px-3 py-2 text-left text-sm transition-colors hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800"
                    >
                      <div className="font-medium">{p.name}</div>
                      <div className="text-xs text-gray-400">
                        {new Date(p.updatedAt).toLocaleString()}
                      </div>
                    </button>
                  </li>
                ))}
              </ul>
            )}
            <button
              onClick={() => setShowLoadDialog(false)}
              className="mt-4 w-full rounded-md border border-gray-200 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 dark:border-gray-700 dark:text-gray-400 dark:hover:bg-gray-800"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </>
  );
}
