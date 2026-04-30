"use client";

import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import type { HumanConfig } from "@gridlane/shared";

interface HumanConfigFormProps {
  config: HumanConfig;
  onUpdate: (changes: Partial<HumanConfig>) => void;
  errors?: Record<string, string>;
}

export function HumanConfigForm({
  config,
  onUpdate,
  errors,
}: HumanConfigFormProps) {
  return (
    <div className="flex flex-col gap-4">
      <div className="space-y-2">
        <Label htmlFor="instructions">Instructions for Reviewer</Label>
        <Textarea
          id="instructions"
          placeholder="Review the AI analysis and approve or reject..."
          value={config.instructions}
          onChange={(e) => onUpdate({ instructions: e.target.value })}
          rows={4}
        />
        <p className="text-xs text-gray-500">
          Shown to the person who needs to approve/reject this step.
        </p>
      </div>

      <div className="flex items-center justify-between">
        <div>
          <Label htmlFor="requireComment">Require Comment</Label>
          <p className="text-xs text-gray-500">
            Reviewer must add a comment before approving or rejecting.
          </p>
        </div>
        <Switch
          id="requireComment"
          checked={config.requireComment}
          onCheckedChange={(checked) =>
            onUpdate({ requireComment: checked })
          }
        />
      </div>
    </div>
  );
}
