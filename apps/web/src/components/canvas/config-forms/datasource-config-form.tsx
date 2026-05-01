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
  { value: "api_key", label: "API Key" },
];

const METHODS_WITH_BODY: HttpMethod[] = ["POST", "PUT", "DELETE"];

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

          {config.authType === "bearer" && (
            <div className="space-y-2">
              <Label htmlFor="bearerToken">
                Bearer Token <span className="text-red-500">*</span>
              </Label>
              <Input
                id="bearerToken"
                type="password"
                placeholder="eyJhbGciOi…"
                value={config.bearerToken ?? ""}
                onChange={(e) => onUpdate({ bearerToken: e.target.value })}
                className={fieldErrorClass(errors, "bearerToken")}
              />
              <FieldError errors={errors} field="bearerToken" />
            </div>
          )}

          {config.authType === "basic" && (
            <>
              <div className="space-y-2">
                <Label htmlFor="basicUsername">
                  Username <span className="text-red-500">*</span>
                </Label>
                <Input
                  id="basicUsername"
                  value={config.basicUsername ?? ""}
                  onChange={(e) => onUpdate({ basicUsername: e.target.value })}
                  className={fieldErrorClass(errors, "basicUsername")}
                />
                <FieldError errors={errors} field="basicUsername" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="basicPassword">
                  Password <span className="text-red-500">*</span>
                </Label>
                <Input
                  id="basicPassword"
                  type="password"
                  value={config.basicPassword ?? ""}
                  onChange={(e) => onUpdate({ basicPassword: e.target.value })}
                  className={fieldErrorClass(errors, "basicPassword")}
                />
                <FieldError errors={errors} field="basicPassword" />
              </div>
            </>
          )}

          {config.authType === "api_key" && (
            <>
              <div className="space-y-2">
                <Label htmlFor="apiKeyHeader">
                  Header Name <span className="text-red-500">*</span>
                </Label>
                <Input
                  id="apiKeyHeader"
                  placeholder="X-API-Key"
                  value={config.apiKeyHeader ?? ""}
                  onChange={(e) => onUpdate({ apiKeyHeader: e.target.value })}
                  className={fieldErrorClass(errors, "apiKeyHeader")}
                />
                <FieldError errors={errors} field="apiKeyHeader" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="apiKeyValue">
                  API Key <span className="text-red-500">*</span>
                </Label>
                <Input
                  id="apiKeyValue"
                  type="password"
                  value={config.apiKeyValue ?? ""}
                  onChange={(e) => onUpdate({ apiKeyValue: e.target.value })}
                  className={fieldErrorClass(errors, "apiKeyValue")}
                />
                <FieldError errors={errors} field="apiKeyValue" />
              </div>
            </>
          )}

          {METHODS_WITH_BODY.includes(config.method) && (
            <div className="space-y-2">
              <Label htmlFor="body">Request Body</Label>
              <textarea
                id="body"
                rows={4}
                placeholder='{"key": "value"}'
                value={config.body ?? ""}
                onChange={(e) => onUpdate({ body: e.target.value })}
                className="flex w-full rounded-md border border-input bg-background px-3 py-2 font-mono text-xs ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              />
              <p className="text-xs text-gray-500">
                Sent as the request body for {config.method} requests.
              </p>
            </div>
          )}
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
