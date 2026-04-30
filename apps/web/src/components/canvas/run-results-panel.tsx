"use client";

import {
  X,
  CheckCircle,
  XCircle,
  Ban,
  Clock,
  Coins,
  Zap,
  ChevronDown,
  ChevronRight,
} from "lucide-react";
import { useState } from "react";
import { usePipelineStore } from "@/stores/pipeline-store";
import type { StepResult, RunStatus } from "@gridlane/shared";

const STATUS_ICONS: Record<RunStatus, typeof CheckCircle> = {
  completed: CheckCircle,
  failed: XCircle,
  cancelled: Ban,
  pending: Clock,
  running: Clock,
};

const STATUS_COLORS: Record<RunStatus, string> = {
  completed: "text-green-600 dark:text-green-400",
  failed: "text-red-600 dark:text-red-400",
  cancelled: "text-gray-400",
  pending: "text-yellow-600 dark:text-yellow-400",
  running: "text-blue-600 dark:text-blue-400",
};

function StepRow({ step }: { step: StepResult }) {
  const [expanded, setExpanded] = useState(false);
  const StatusIcon = STATUS_ICONS[step.status];

  return (
    <li className="border-b border-gray-100 last:border-b-0 dark:border-gray-800">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center gap-2 px-4 py-2.5 text-left text-sm transition-colors hover:bg-gray-50 dark:hover:bg-gray-800/50"
      >
        {expanded ? (
          <ChevronDown className="h-3.5 w-3.5 text-gray-400" />
        ) : (
          <ChevronRight className="h-3.5 w-3.5 text-gray-400" />
        )}

        <StatusIcon className={`h-4 w-4 ${STATUS_COLORS[step.status]}`} />

        <span className="flex-1 font-medium text-gray-700 dark:text-gray-300">
          {step.nodeLabel}
        </span>

        <span className="text-xs text-gray-400">
          {step.durationMs !== undefined ? `${step.durationMs}ms` : "—"}
        </span>
      </button>

      {expanded && (
        <div className="space-y-2 bg-gray-50 px-4 py-3 text-xs dark:bg-gray-900/50">
          <div className="flex items-center gap-4 text-gray-500">
            <span>Type: {step.nodeType}</span>
            <span>Order: {step.order}</span>
          </div>

          {step.error && (
            <div className="rounded-md bg-red-50 px-3 py-2 text-red-700 dark:bg-red-950/50 dark:text-red-400">
              {step.error}
            </div>
          )}

          {step.tokenUsage && (
            <div className="flex items-center gap-3 text-gray-500">
              <Zap className="h-3 w-3" />
              <span>In: {step.tokenUsage.inputTokens}</span>
              <span>Out: {step.tokenUsage.outputTokens}</span>
              <span>Total: {step.tokenUsage.totalTokens}</span>
              {step.costUsd !== undefined && (
                <>
                  <Coins className="ml-1 h-3 w-3" />
                  <span>${step.costUsd.toFixed(4)}</span>
                </>
              )}
            </div>
          )}

          {step.output != null && (
            <details className="group">
              <summary className="cursor-pointer text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">
                Output
              </summary>
              <pre className="mt-1 max-h-40 overflow-auto rounded-md bg-white p-2 font-mono text-xs dark:bg-gray-900">
                {String(JSON.stringify(step.output, null, 2))}
              </pre>
            </details>
          )}

          {step.input != null && (
            <details className="group">
              <summary className="cursor-pointer text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">
                Input
              </summary>
              <pre className="mt-1 max-h-40 overflow-auto rounded-md bg-white p-2 font-mono text-xs dark:bg-gray-900">
                {String(JSON.stringify(step.input, null, 2))}
              </pre>
            </details>
          )}
        </div>
      )}
    </li>
  );
}

/**
 * Run Results Panel — shows after a pipeline is executed.
 *
 * Displays overall run status, timing, and cost at top.
 * Each step is expandable to show input/output/error details.
 */
export function RunResultsPanel() {
  // Individual selectors — functions are stable references, no useShallow needed
  const currentRun = usePipelineStore((s) => s.currentRun);
  const setCurrentRun = usePipelineStore((s) => s.setCurrentRun);

  if (!currentRun) return null;

  const isSuccess = currentRun.status === "completed";

  return (
    <aside
      className="flex w-96 flex-col border-l border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-950"
      role="complementary"
      aria-label="Run results"
    >
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-200 px-4 py-3 dark:border-gray-800">
        <div className="flex items-center gap-2">
          {isSuccess ? (
            <CheckCircle className="h-4 w-4 text-green-600 dark:text-green-400" />
          ) : (
            <XCircle className="h-4 w-4 text-red-600 dark:text-red-400" />
          )}
          <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">
            Run {isSuccess ? "Completed" : "Failed"}
          </span>
        </div>
        <button
          onClick={() => setCurrentRun(null)}
          className="rounded-md p-1 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-800 dark:hover:text-gray-300"
          aria-label="Close results panel"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      {/* Summary */}
      <div className="flex items-center gap-4 border-b border-gray-100 px-4 py-2 text-xs text-gray-500 dark:border-gray-800">
        <div className="flex items-center gap-1">
          <Clock className="h-3 w-3" />
          {currentRun.totalDurationMs !== undefined
            ? `${currentRun.totalDurationMs}ms`
            : "—"}
        </div>
        <div className="flex items-center gap-1">
          <Zap className="h-3 w-3" />
          {currentRun.steps.length} steps
        </div>
        {currentRun.totalCostUsd !== undefined && currentRun.totalCostUsd > 0 && (
          <div className="flex items-center gap-1">
            <Coins className="h-3 w-3" />
            ${currentRun.totalCostUsd.toFixed(4)}
          </div>
        )}
      </div>

      {/* Steps */}
      <ul className="flex-1 overflow-y-auto">
        {currentRun.steps.map((step) => (
          <StepRow key={step.nodeId} step={step} />
        ))}
      </ul>
    </aside>
  );
}
