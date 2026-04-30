"use client";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { FieldError, fieldErrorClass } from "./field-error";
import type {
  DataSourceConfig,
  DataSourceType,
  HttpMethod,
  AuthType,
} from "@gridlane/shared";

interface DataSourceConfigFormProps {
  config: DataSourceConfig;
  onUpdate: (changes: Partial<DataSourceConfig>) => void;
  errors?: Record<string, string>;
}

const SOURCE_TYPES: { value: DataSourceType; label: string }[] = [
  { value: "rest", label: "REST API" },
  { value: "sql", label: "SQL Database" },
  { value: "file", label: "File (CSV/JSON)" },
];

const HTTP_METHODS: HttpMethod[] = ["GET", "POST", "PUT", "DELETE"];

const AUTH_TYPES: { value: AuthType; label: string }[] = [
  { value: "none", label: "None" },
  { value: "bearer", label: "Bearer Token" },
  { value: "basic", label: "Basic Auth" },
];

export function DataSourceConfigForm({
  config,
  onUpdate,
  errors,
}: DataSourceConfigFormProps) {
  return (
    <div className="flex flex-col gap-4">
      <div className="space-y-2">
        <Label htmlFor="sourceType">Source Type</Label>
        <Select
          value={config.sourceType}
          onValueChange={(value) =>
            onUpdate({ sourceType: value as DataSourceType })
          }
        >
          <SelectTrigger id="sourceType">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {SOURCE_TYPES.map((st) => (
              <SelectItem key={st.value} value={st.value}>
                {st.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {config.sourceType === "rest" && (
        <>
          <div className="space-y-2">
            <Label htmlFor="url">
              URL <span className="text-red-500">*</span>
            </Label>
            <Input
              id="url"
              placeholder="https://api.example.com/data"
              value={config.url}
              onChange={(e) => onUpdate({ url: e.target.value })}
              className={fieldErrorClass(errors, "url")}
            />
            <FieldError errors={errors} field="url" />
          </div>

          <div className="space-y-2">
            <Label htmlFor="method">HTTP Method</Label>
            <Select
              value={config.method}
              onValueChange={(value) =>
                onUpdate({ method: value as HttpMethod })
              }
            >
              <SelectTrigger id="method">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {HTTP_METHODS.map((m) => (
                  <SelectItem key={m} value={m}>
                    {m}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="authType">Authentication</Label>
            <Select
              value={config.authType}
              onValueChange={(value) =>
                onUpdate({ authType: value as AuthType })
              }
            >
              <SelectTrigger id="authType">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {AUTH_TYPES.map((at) => (
                  <SelectItem key={at.value} value={at.value}>
                    {at.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </>
      )}

      {config.sourceType === "sql" && (
        <div className="space-y-2">
          <Label htmlFor="url">
            Connection String <span className="text-red-500">*</span>
          </Label>
          <Input
            id="url"
            placeholder="postgresql://user:pass@host:5432/db"
            value={config.url}
            onChange={(e) => onUpdate({ url: e.target.value })}
            className={fieldErrorClass(errors, "url")}
          />
          <FieldError errors={errors} field="url" />
        </div>
      )}

      {config.sourceType === "file" && (
        <p className="text-xs text-gray-500">
          File upload will be available when connectors are implemented.
        </p>
      )}
    </div>
  );
}
