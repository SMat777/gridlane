"use client";

import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { ActionConfig, ActionType, OutputFormat } from "@gridlane/shared";

interface ActionConfigFormProps {
  config: ActionConfig;
  onUpdate: (changes: Partial<ActionConfig>) => void;
  errors?: Record<string, string>;
}

const ACTION_TYPES: { value: ActionType; label: string }[] = [
  { value: "transform", label: "Transform Data" },
  { value: "output", label: "Output / Export" },
];

const OUTPUT_FORMATS: { value: OutputFormat; label: string }[] = [
  { value: "json", label: "JSON" },
  { value: "csv", label: "CSV" },
  { value: "text", label: "Plain Text" },
];

export function ActionConfigForm({
  config,
  onUpdate,
  errors,
}: ActionConfigFormProps) {
  return (
    <div className="flex flex-col gap-4">
      <div className="space-y-2">
        <Label htmlFor="actionType">Action Type</Label>
        <Select
          value={config.actionType}
          onValueChange={(value) =>
            onUpdate({ actionType: value as ActionType })
          }
        >
          <SelectTrigger id="actionType">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {ACTION_TYPES.map((at) => (
              <SelectItem key={at.value} value={at.value}>
                {at.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <Label htmlFor="outputFormat">Output Format</Label>
        <Select
          value={config.outputFormat}
          onValueChange={(value) =>
            onUpdate({ outputFormat: value as OutputFormat })
          }
        >
          <SelectTrigger id="outputFormat">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {OUTPUT_FORMATS.map((of) => (
              <SelectItem key={of.value} value={of.value}>
                {of.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    </div>
  );
}
