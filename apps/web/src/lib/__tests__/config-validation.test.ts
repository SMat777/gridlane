import { describe, it, expect } from "vitest";
import {
  validateNodeConfig,
  dataSourceConfigSchema,
  aiConfigSchema,
  actionConfigSchema,
  humanConfigSchema,
  DEFAULT_NODE_CONFIGS,
} from "@gridlane/shared";

// ── DataSource Config ────────────────────────────────────────────────

describe("dataSourceConfigSchema", () => {
  it("accepts valid REST config with URL", () => {
    const config = {
      ...DEFAULT_NODE_CONFIGS.datasource,
      url: "https://api.example.com/data",
    };
    const result = dataSourceConfigSchema.safeParse(config);
    expect(result.success).toBe(true);
  });

  it("rejects REST config with empty URL", () => {
    const config = { ...DEFAULT_NODE_CONFIGS.datasource, url: "" };
    const result = dataSourceConfigSchema.safeParse(config);
    expect(result.success).toBe(false);
    if (!result.success) {
      const urlError = result.error.issues.find((i) =>
        i.path.includes("url"),
      );
      expect(urlError).toBeDefined();
      expect(urlError!.message).toContain("URL is required");
    }
  });

  it("rejects SQL config with empty connection string", () => {
    const config = {
      ...DEFAULT_NODE_CONFIGS.datasource,
      sourceType: "sql" as const,
      url: "",
    };
    const result = dataSourceConfigSchema.safeParse(config);
    expect(result.success).toBe(false);
    if (!result.success) {
      const urlError = result.error.issues.find((i) =>
        i.path.includes("url"),
      );
      expect(urlError).toBeDefined();
      expect(urlError!.message).toContain("Connection string is required");
    }
  });

  it("accepts file config without URL (URL not required for file)", () => {
    const config = {
      ...DEFAULT_NODE_CONFIGS.datasource,
      sourceType: "file" as const,
    };
    const result = dataSourceConfigSchema.safeParse(config);
    expect(result.success).toBe(true);
  });

  it("rejects invalid sourceType", () => {
    const config = { ...DEFAULT_NODE_CONFIGS.datasource, sourceType: "ftp" };
    const result = dataSourceConfigSchema.safeParse(config);
    expect(result.success).toBe(false);
  });

  it("rejects invalid HTTP method", () => {
    const config = {
      ...DEFAULT_NODE_CONFIGS.datasource,
      url: "https://example.com",
      method: "PATCH",
    };
    const result = dataSourceConfigSchema.safeParse(config);
    expect(result.success).toBe(false);
  });

  // ── Per-authType field requirements ───────────────────────────────

  it("rejects bearer auth without a token", () => {
    const config = {
      ...DEFAULT_NODE_CONFIGS.datasource,
      url: "https://x.test",
      authType: "bearer" as const,
    };
    const result = dataSourceConfigSchema.safeParse(config);
    expect(result.success).toBe(false);
    if (!result.success) {
      const err = result.error.issues.find((i) =>
        i.path.includes("bearerToken"),
      );
      expect(err).toBeDefined();
    }
  });

  it("accepts bearer auth with a token", () => {
    const config = {
      ...DEFAULT_NODE_CONFIGS.datasource,
      url: "https://x.test",
      authType: "bearer" as const,
      bearerToken: "abc123",
    };
    const result = dataSourceConfigSchema.safeParse(config);
    expect(result.success).toBe(true);
  });

  it("rejects basic auth missing username and password", () => {
    const config = {
      ...DEFAULT_NODE_CONFIGS.datasource,
      url: "https://x.test",
      authType: "basic" as const,
    };
    const result = dataSourceConfigSchema.safeParse(config);
    expect(result.success).toBe(false);
    if (!result.success) {
      const fields = result.error.issues.map((i) => i.path.join("."));
      expect(fields).toContain("basicUsername");
      expect(fields).toContain("basicPassword");
    }
  });

  it("rejects api_key auth missing header name and value", () => {
    const config = {
      ...DEFAULT_NODE_CONFIGS.datasource,
      url: "https://x.test",
      authType: "api_key" as const,
    };
    const result = dataSourceConfigSchema.safeParse(config);
    expect(result.success).toBe(false);
    if (!result.success) {
      const fields = result.error.issues.map((i) => i.path.join("."));
      expect(fields).toContain("apiKeyHeader");
      expect(fields).toContain("apiKeyValue");
    }
  });

  it("accepts api_key auth with header and value", () => {
    const config = {
      ...DEFAULT_NODE_CONFIGS.datasource,
      url: "https://x.test",
      authType: "api_key" as const,
      apiKeyHeader: "X-API-Key",
      apiKeyValue: "secret",
    };
    const result = dataSourceConfigSchema.safeParse(config);
    expect(result.success).toBe(true);
  });

  it("does not enforce auth fields for non-rest sources", () => {
    // SQL ignores authType entirely — no per-type field check
    const config = {
      ...DEFAULT_NODE_CONFIGS.datasource,
      sourceType: "sql" as const,
      url: "postgresql://localhost/db",
      authType: "bearer" as const,
    };
    const result = dataSourceConfigSchema.safeParse(config);
    expect(result.success).toBe(true);
  });
});

// ── AI Config ────────────────────────────────────────────────────────

describe("aiConfigSchema", () => {
  it("accepts valid AI config", () => {
    const result = aiConfigSchema.safeParse(DEFAULT_NODE_CONFIGS.ai);
    // Default has empty prompt — should fail
    expect(result.success).toBe(false);
  });

  it("accepts AI config with prompt filled", () => {
    const config = {
      ...DEFAULT_NODE_CONFIGS.ai,
      prompt: "Analyze this data: {{ input }}",
    };
    const result = aiConfigSchema.safeParse(config);
    expect(result.success).toBe(true);
  });

  it("rejects empty prompt", () => {
    const config = { ...DEFAULT_NODE_CONFIGS.ai, prompt: "" };
    const result = aiConfigSchema.safeParse(config);
    expect(result.success).toBe(false);
    if (!result.success) {
      const promptError = result.error.issues.find((i) =>
        i.path.includes("prompt"),
      );
      expect(promptError).toBeDefined();
    }
  });

  it("rejects empty model", () => {
    const config = {
      ...DEFAULT_NODE_CONFIGS.ai,
      model: "",
      prompt: "test",
    };
    const result = aiConfigSchema.safeParse(config);
    expect(result.success).toBe(false);
  });

  it("rejects temperature below 0", () => {
    const config = {
      ...DEFAULT_NODE_CONFIGS.ai,
      prompt: "test",
      temperature: -0.5,
    };
    const result = aiConfigSchema.safeParse(config);
    expect(result.success).toBe(false);
  });

  it("rejects temperature above 2", () => {
    const config = {
      ...DEFAULT_NODE_CONFIGS.ai,
      prompt: "test",
      temperature: 2.5,
    };
    const result = aiConfigSchema.safeParse(config);
    expect(result.success).toBe(false);
  });

  it("rejects maxTokens below 1", () => {
    const config = {
      ...DEFAULT_NODE_CONFIGS.ai,
      prompt: "test",
      maxTokens: 0,
    };
    const result = aiConfigSchema.safeParse(config);
    expect(result.success).toBe(false);
  });

  it("rejects maxTokens above 100000", () => {
    const config = {
      ...DEFAULT_NODE_CONFIGS.ai,
      prompt: "test",
      maxTokens: 200_000,
    };
    const result = aiConfigSchema.safeParse(config);
    expect(result.success).toBe(false);
  });

  it("rejects non-integer maxTokens", () => {
    const config = {
      ...DEFAULT_NODE_CONFIGS.ai,
      prompt: "test",
      maxTokens: 1024.5,
    };
    const result = aiConfigSchema.safeParse(config);
    expect(result.success).toBe(false);
  });

  it("rejects invalid provider", () => {
    const config = {
      ...DEFAULT_NODE_CONFIGS.ai,
      prompt: "test",
      provider: "google",
    };
    const result = aiConfigSchema.safeParse(config);
    expect(result.success).toBe(false);
  });
});

// ── Action Config ────────────────────────────────────────────────────

describe("actionConfigSchema", () => {
  it("accepts valid action config", () => {
    const result = actionConfigSchema.safeParse(DEFAULT_NODE_CONFIGS.action);
    expect(result.success).toBe(true);
  });

  it("rejects invalid actionType", () => {
    const config = { ...DEFAULT_NODE_CONFIGS.action, actionType: "delete" };
    const result = actionConfigSchema.safeParse(config);
    expect(result.success).toBe(false);
  });

  it("rejects invalid outputFormat", () => {
    const config = { ...DEFAULT_NODE_CONFIGS.action, outputFormat: "xml" };
    const result = actionConfigSchema.safeParse(config);
    expect(result.success).toBe(false);
  });
});

// ── Human Config ─────────────────────────────────────────────────────

describe("humanConfigSchema", () => {
  it("accepts valid human config", () => {
    const result = humanConfigSchema.safeParse(DEFAULT_NODE_CONFIGS.human);
    expect(result.success).toBe(true);
  });

  it("accepts human config with instructions", () => {
    const config = {
      instructions: "Please review the output",
      requireComment: true,
    };
    const result = humanConfigSchema.safeParse(config);
    expect(result.success).toBe(true);
  });

  it("accepts human config with empty instructions", () => {
    const config = { instructions: "", requireComment: false };
    const result = humanConfigSchema.safeParse(config);
    expect(result.success).toBe(true);
  });
});

// ── validateNodeConfig() ─────────────────────────────────────────────

describe("validateNodeConfig", () => {
  it("returns valid for correct datasource config", () => {
    const config = {
      ...DEFAULT_NODE_CONFIGS.datasource,
      url: "https://example.com",
    };
    const result = validateNodeConfig("datasource", config);
    expect(result.valid).toBe(true);
    expect(result.errors).toHaveLength(0);
  });

  it("returns errors for invalid AI config", () => {
    const result = validateNodeConfig("ai", DEFAULT_NODE_CONFIGS.ai);
    expect(result.valid).toBe(false);
    expect(result.errors.length).toBeGreaterThan(0);
    expect(result.errors.some((e) => e.field === "prompt")).toBe(true);
  });

  it("returns error for missing config", () => {
    const result = validateNodeConfig("ai", undefined);
    expect(result.valid).toBe(false);
    expect(result.errors[0].field).toBe("_root");
  });

  it("returns valid for correct action config", () => {
    const result = validateNodeConfig("action", DEFAULT_NODE_CONFIGS.action);
    expect(result.valid).toBe(true);
  });

  it("returns valid for correct human config", () => {
    const result = validateNodeConfig("human", DEFAULT_NODE_CONFIGS.human);
    expect(result.valid).toBe(true);
  });

  it("returns field-level errors with messages", () => {
    const config = {
      ...DEFAULT_NODE_CONFIGS.ai,
      prompt: "",
      model: "",
      temperature: 5,
    };
    const result = validateNodeConfig("ai", config);
    expect(result.valid).toBe(false);

    // Should have errors for prompt, model, and temperature
    const fields = result.errors.map((e) => e.field);
    expect(fields).toContain("prompt");
    expect(fields).toContain("model");
    expect(fields).toContain("temperature");

    // Each error should have a meaningful message
    for (const error of result.errors) {
      expect(error.message.length).toBeGreaterThan(0);
    }
  });
});
