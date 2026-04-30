/**
 * Runtime validation schemas for node configs.
 *
 * Uses Zod to validate at runtime what TypeScript only checks at compile time.
 * Each schema mirrors the interfaces in pipeline.ts — single source of truth
 * for what constitutes a VALID config, not just a type-correct one.
 */

import { z } from "zod";

// ── DataSource Config ────────────────────────────────────────────────

export const dataSourceConfigSchema = z
  .object({
    sourceType: z.enum(["rest", "sql", "file"]),
    url: z.string().default(""),
    method: z.enum(["GET", "POST", "PUT", "DELETE"]).default("GET"),
    headers: z.record(z.string(), z.string()).default({}),
    authType: z.enum(["none", "bearer", "basic"]).default("none"),
  })
  .superRefine((data, ctx) => {
    if (data.sourceType === "rest" && !data.url.trim()) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["url"],
        message: "URL is required for REST sources",
      });
    }
    if (data.sourceType === "sql" && !data.url.trim()) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["url"],
        message: "Connection string is required for SQL sources",
      });
    }
  });

// ── AI Config ────────────────────────────────────────────────────────

export const aiConfigSchema = z.object({
  provider: z.enum(["anthropic", "openai"]),
  model: z.string().min(1, "Model is required"),
  prompt: z.string().min(1, "Prompt is required"),
  temperature: z
    .number()
    .min(0, "Temperature must be between 0 and 2")
    .max(2, "Temperature must be between 0 and 2"),
  maxTokens: z
    .number()
    .int("Max tokens must be a whole number")
    .min(1, "Max tokens must be at least 1")
    .max(100_000, "Max tokens cannot exceed 100,000"),
});

// ── Action Config ────────────────────────────────────────────────────

export const actionConfigSchema = z.object({
  actionType: z.enum(["transform", "output"]),
  outputFormat: z.enum(["json", "csv", "text"]),
});

// ── Human Config ─────────────────────────────────────────────────────

export const humanConfigSchema = z.object({
  instructions: z.string().default(""),
  requireComment: z.boolean().default(false),
});

// ── Schema Map + Validation Function ─────────────────────────────────

import type { PipelineNodeType, NodeConfig } from "./pipeline";

const CONFIG_SCHEMAS: Record<PipelineNodeType, z.ZodType> = {
  datasource: dataSourceConfigSchema,
  ai: aiConfigSchema,
  action: actionConfigSchema,
  human: humanConfigSchema,
};

/** Field-level error: which field failed and why */
export interface ConfigFieldError {
  field: string;
  message: string;
}

/** Result of validating a node's config */
export interface ConfigValidationResult {
  valid: boolean;
  errors: ConfigFieldError[];
}

/**
 * Validate a node's config against its Zod schema.
 *
 * Returns field-level errors that can be displayed inline in forms.
 * An empty errors array means the config is valid.
 */
export function validateNodeConfig(
  nodeType: PipelineNodeType,
  config: NodeConfig | undefined,
): ConfigValidationResult {
  if (!config) {
    return {
      valid: false,
      errors: [{ field: "_root", message: "Configuration is missing" }],
    };
  }

  const schema = CONFIG_SCHEMAS[nodeType];
  const result = schema.safeParse(config);

  if (result.success) {
    return { valid: true, errors: [] };
  }

  const errors: ConfigFieldError[] = result.error.issues.map((issue) => ({
    field: issue.path.join(".") || "_root",
    message: issue.message,
  }));

  return { valid: false, errors };
}
