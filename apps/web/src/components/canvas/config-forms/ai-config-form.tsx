"use client";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { FieldError, fieldErrorClass } from "./field-error";
import type { AIConfig, AIProvider } from "@gridlane/shared";

interface AIConfigFormProps {
  config: AIConfig;
  onUpdate: (changes: Partial<AIConfig>) => void;
  errors?: Record<string, string>;
}

const PROVIDERS: { value: AIProvider; label: string }[] = [
  { value: "anthropic", label: "Anthropic" },
  { value: "openai", label: "OpenAI" },
];

const MODELS: Record<AIProvider, { value: string; label: string }[]> = {
  anthropic: [
    { value: "claude-sonnet-4-20250514", label: "Claude Sonnet 4" },
    { value: "claude-haiku-4-20250514", label: "Claude Haiku 4" },
  ],
  openai: [
    { value: "gpt-4o", label: "GPT-4o" },
    { value: "gpt-4o-mini", label: "GPT-4o Mini" },
  ],
};

export function AIConfigForm({ config, onUpdate, errors }: AIConfigFormProps) {
  const availableModels = MODELS[config.provider] ?? [];

  return (
    <div className="flex flex-col gap-4">
      <div className="space-y-2">
        <Label htmlFor="provider">Provider</Label>
        <Select
          value={config.provider}
          onValueChange={(value) => {
            const provider = value as AIProvider;
            const firstModel = MODELS[provider]?.[0]?.value ?? "";
            onUpdate({ provider, model: firstModel });
          }}
        >
          <SelectTrigger id="provider">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {PROVIDERS.map((p) => (
              <SelectItem key={p.value} value={p.value}>
                {p.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <Label htmlFor="model">Model</Label>
        <Select
          value={config.model}
          onValueChange={(value) => { if (value) onUpdate({ model: value }); }}
        >
          <SelectTrigger id="model">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {availableModels.map((m) => (
              <SelectItem key={m.value} value={m.value}>
                {m.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <Label htmlFor="prompt">
          Prompt Template <span className="text-red-500">*</span>
        </Label>
        <Textarea
          id="prompt"
          placeholder="Analyze the following data: {{ input }}"
          value={config.prompt}
          onChange={(e) => onUpdate({ prompt: e.target.value })}
          rows={4}
          className={`font-mono text-sm ${fieldErrorClass(errors, "prompt")}`}
        />
        <FieldError errors={errors} field="prompt" />
        <p className="text-xs text-gray-500">
          Use <code className="rounded bg-gray-100 px-1 dark:bg-gray-800">{"{{ input }}"}</code> to reference data from the previous step.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="temperature">Temperature</Label>
          <Input
            id="temperature"
            type="number"
            min={0}
            max={2}
            step={0.1}
            value={config.temperature}
            onChange={(e) =>
              onUpdate({ temperature: parseFloat(e.target.value) || 0 })
            }
            className={fieldErrorClass(errors, "temperature")}
          />
          <FieldError errors={errors} field="temperature" />
        </div>

        <div className="space-y-2">
          <Label htmlFor="maxTokens">Max Tokens</Label>
          <Input
            id="maxTokens"
            type="number"
            min={1}
            max={100000}
            step={256}
            value={config.maxTokens}
            onChange={(e) =>
              onUpdate({ maxTokens: parseInt(e.target.value) || 1024 })
            }
            className={fieldErrorClass(errors, "maxTokens")}
          />
          <FieldError errors={errors} field="maxTokens" />
        </div>
      </div>
    </div>
  );
}
