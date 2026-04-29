"use client";

import type { ReactNode } from "react";

/**
 * BaseNode — shared wrapper for all custom pipeline nodes.
 *
 * Provides consistent sizing, border, shadow, and slot for
 * the node-type-specific content. Each concrete node (DataSourceNode,
 * AINode, etc.) wraps this and adds its own color + icon.
 */
interface BaseNodeProps {
  children: ReactNode;
  color: string;
  selected?: boolean;
  isValid?: boolean;
}

const colorMap: Record<string, { border: string; bg: string; ring: string }> = {
  blue: {
    border: "border-blue-400",
    bg: "bg-blue-50 dark:bg-blue-950",
    ring: "ring-blue-400",
  },
  purple: {
    border: "border-purple-400",
    bg: "bg-purple-50 dark:bg-purple-950",
    ring: "ring-purple-400",
  },
  green: {
    border: "border-green-400",
    bg: "bg-green-50 dark:bg-green-950",
    ring: "ring-green-400",
  },
  orange: {
    border: "border-orange-400",
    bg: "bg-orange-50 dark:bg-orange-950",
    ring: "ring-orange-400",
  },
};

export function BaseNode({ children, color, selected, isValid = true }: BaseNodeProps) {
  const colors = colorMap[color] ?? colorMap.blue;

  return (
    <div
      className={`
        rounded-lg border-2 px-4 py-3 shadow-sm min-w-[160px]
        transition-all duration-150
        ${colors.border} ${colors.bg}
        ${selected ? `ring-2 ${colors.ring} ring-offset-1` : ""}
        ${!isValid ? "border-red-500 ring-2 ring-red-300" : ""}
      `}
    >
      {children}
    </div>
  );
}
