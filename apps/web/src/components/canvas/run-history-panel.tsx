"use client";

import { useEffect, useState } from "react";
import {
  CheckCircle,
  XCircle,
  Ban,
  Clock,
  Coins,
  Loader2,
  History,
} from "lucide-react";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "@/components/ui/sheet";
import { listRuns, getRun } from "@/lib/engine-api";
import { usePipelineStore } from "@/stores/pipeline-store";
import type { RunStatus, RunSummary } from "@gridlane/shared";
import { toast } from "sonner";

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

function formatRelativeTime(iso: string): string {
  if (!iso) return "—";
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return iso;
  const diffSec = Math.round((Date.now() - then) / 1000);
  if (diffSec < 60) return `${diffSec}s ago`;
  if (diffSec < 3600) return `${Math.round(diffSec / 60)}m ago`;
  if (diffSec < 86400) return `${Math.round(diffSec / 3600)}h ago`;
  return new Date(iso).toLocaleDateString();
}

interface RunHistoryPanelProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function RunHistoryPanel({ open, onOpenChange }: RunHistoryPanelProps) {
  const setCurrentRun = usePipelineStore((s) => s.setCurrentRun);
  // null = never loaded yet; [] = loaded but empty. Stale data is kept on
  // close → reopen so the user sees something immediately while refresh runs.
  const [runs, setRuns] = useState<RunSummary[] | null>(null);
  const [openingId, setOpeningId] = useState<string | null>(null);
  const loading = open && runs === null;

  useEffect(() => {
    if (!open) return;

    let cancelled = false;
    listRuns({ limit: 50 }).then((result) => {
      if (cancelled) return;
      if ("error" in result) {
        toast.error("Failed to load run history", { description: result.error });
        setRuns((prev) => prev ?? []);
      } else {
        setRuns(result.runs);
      }
    });

    return () => {
      cancelled = true;
    };
  }, [open]);

  const handleOpen = async (run: RunSummary) => {
    setOpeningId(run.id);
    const result = await getRun(run.id);
    setOpeningId(null);
    if ("error" in result) {
      toast.error("Failed to load run", { description: result.error });
      return;
    }
    setCurrentRun(result.run);
    onOpenChange(false);
  };

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="right" className="w-full sm:max-w-md">
        <SheetHeader>
          <SheetTitle className="flex items-center gap-2">
            <History className="h-4 w-4" />
            Run History
          </SheetTitle>
          <SheetDescription>
            Last 50 pipeline runs across all pipelines
          </SheetDescription>
        </SheetHeader>

        <div className="flex-1 overflow-y-auto px-2 pb-4">
          {loading && (
            <div className="flex items-center justify-center gap-2 py-12 text-sm text-gray-500">
              <Loader2 className="h-4 w-4 animate-spin" />
              Loading runs…
            </div>
          )}

          {!loading && runs?.length === 0 && (
            <div className="px-4 py-12 text-center text-sm text-gray-500">
              No runs yet. Run a pipeline to see it here.
            </div>
          )}

          {!loading && runs && runs.length > 0 && (
            <ul className="space-y-1">
              {runs.map((run) => {
                const StatusIcon = STATUS_ICONS[run.status] ?? Clock;
                const isOpening = openingId === run.id;
                return (
                  <li key={run.id}>
                    <button
                      onClick={() => handleOpen(run)}
                      disabled={isOpening}
                      className="flex w-full items-start gap-3 rounded-md px-3 py-2.5 text-left transition-colors hover:bg-gray-100 disabled:opacity-60 dark:hover:bg-gray-800"
                    >
                      <StatusIcon
                        className={`mt-0.5 h-4 w-4 shrink-0 ${STATUS_COLORS[run.status] ?? ""}`}
                      />
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center justify-between gap-2">
                          <span className="truncate text-sm font-medium text-gray-700 dark:text-gray-200">
                            {run.pipelineName || "Untitled"}
                          </span>
                          <span className="shrink-0 text-xs text-gray-400">
                            {formatRelativeTime(run.startedAt)}
                          </span>
                        </div>
                        <div className="mt-1 flex items-center gap-3 text-xs text-gray-500">
                          <span className="capitalize">{run.status}</span>
                          <span className="flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            {run.totalDurationMs !== undefined
                              ? `${run.totalDurationMs}ms`
                              : "—"}
                          </span>
                          <span>
                            {run.stepCount} step{run.stepCount === 1 ? "" : "s"}
                          </span>
                          {run.totalCostUsd !== undefined &&
                            run.totalCostUsd > 0 && (
                              <span className="flex items-center gap-1">
                                <Coins className="h-3 w-3" />
                                ${run.totalCostUsd.toFixed(4)}
                              </span>
                            )}
                        </div>
                      </div>
                      {isOpening && (
                        <Loader2 className="h-4 w-4 animate-spin text-gray-400" />
                      )}
                    </button>
                  </li>
                );
              })}
            </ul>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}
