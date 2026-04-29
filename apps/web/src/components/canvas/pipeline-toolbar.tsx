"use client";

import { useState } from "react";
import { Save, FolderOpen, Plus, CheckCircle } from "lucide-react";
import { usePipelineStore } from "@/stores/pipeline-store";
import { savePipeline, listPipelines, loadPipeline } from "@/lib/pipeline-api";
import type { PipelineDefinition } from "@gridlane/shared";

/**
 * Pipeline toolbar — save, load, and new pipeline actions.
 *
 * Sits at the top of the canvas. Communicates with Supabase
 * through pipeline-api.ts and updates the Zustand store.
 */
export function PipelineToolbar() {
  const { pipelineName, toSerializable, runValidation } = usePipelineStore();
  const loadPipelineToStore = usePipelineStore((s) => s.loadPipeline);
  const [saving, setSaving] = useState(false);
  const [status, setStatus] = useState<string | null>(null);
  const [showLoadDialog, setShowLoadDialog] = useState(false);
  const [pipelines, setPipelines] = useState<
    Array<{ id: string; name: string; updatedAt: string }>
  >([]);
  const [loading, setLoading] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    setStatus(null);

    const pipeline = toSerializable();
    const result = await savePipeline(pipeline);

    if ("error" in result) {
      setStatus(`Error: ${result.error}`);
    } else {
      setStatus("Saved ✓");
      setTimeout(() => setStatus(null), 2000);
    }
    setSaving(false);
  };

  const handleLoadList = async () => {
    setLoading(true);
    const result = await listPipelines();

    if ("error" in result) {
      setStatus(`Error: ${result.error}`);
      setLoading(false);
      return;
    }

    setPipelines(result);
    setShowLoadDialog(true);
    setLoading(false);
  };

  const handleLoad = async (id: string) => {
    setLoading(true);
    const result = await loadPipeline(id);

    if ("error" in result) {
      setStatus(`Error: ${result.error}`);
    } else {
      loadPipelineToStore(result);
      setStatus("Loaded ✓");
      setTimeout(() => setStatus(null), 2000);
    }
    setShowLoadDialog(false);
    setLoading(false);
  };

  const handleValidate = () => {
    const errors = runValidation();
    if (errors.length === 0) {
      setStatus("Valid ✓");
      setTimeout(() => setStatus(null), 2000);
    } else {
      setStatus(`${errors.length} issue${errors.length > 1 ? "s" : ""} found`);
    }
  };

  const handleNew = () => {
    usePipelineStore.setState({
      nodes: [],
      edges: [],
      pipelineName: "Untitled Pipeline",
    });
    setStatus(null);
  };

  return (
    <>
      <div className="flex items-center gap-2 border-b border-gray-200 bg-white px-4 py-2 dark:border-gray-800 dark:bg-gray-950">
        <h1 className="text-sm font-semibold text-gray-700 dark:text-gray-300">
          {pipelineName}
        </h1>

        <div className="ml-auto flex items-center gap-2">
          {status && (
            <span
              className={`text-xs ${status.startsWith("Error") ? "text-red-500" : "text-green-600"}`}
            >
              {status}
            </span>
          )}

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
        </div>
      </div>

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
