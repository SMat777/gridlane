# Spec: REST API Connector + Retro Debt

> Status: draft → implementation
> Owner: Simon
> Sprint: 6B (Foundation)
> Phase: 1c (REST connector) + retro-debt fra Phase 1a

## Goal

Erstat første stub-executor med en rigtig connector, og pak fire højværdi-quick-wins
fra SSE-retrospektet ind i samme PR-bundle. Resultatet:

- Pipelines kan nu fetche data fra **rigtige REST API'er** end-to-end (engine →
  bus → DB → SSE → UI).
- `NodeExecutor` ABC udvides med `redact()` så connectors **eksplicit** styrer
  hvad der lækker til offentlige event-streams.
- Single-process SSE/cancel-arkitekturen får tre robusthedsfix der ikke kræver
  auth- eller multi-worker-arbejde.

## Non-Goals (dette PR-bundle)

- SQL- og File-connectors (stub-fallback bevares for `sourceType` ∈ `{sql, file}`)
- Auth på stream/cancel endpoints (afventer auth-feature)
- Redis pub/sub for multi-worker SSE (stadig single-worker antagelse)
- Connector retry-policy / circuit-breaker (én forsøg, fail-fast i denne phase)
- OAuth2 flow (auth-typer begrænset til static-credential-mønstre)
- Streaming af response body (hele body parses i RAM — fine for foundation)

## Scope-opdeling

Forslag: **1 PR med 3 logiske commits** (ingen stack-rebase nødvendig — alt rammer
samme files på en koordineret måde).

| Commit | Indhold | LOC est. |
|--------|---------|----------|
| 1 | `redact()` ABC + Last-Event-ID cap + heartbeat env-var + graceful shutdown | ~150 |
| 2 | `RestDataSourceExecutor` + auth-handlers + error mapping + tests | ~400 |
| 3 | E2E SSE integration test + manuel demo-script | ~100 |

Hvis commit 2 vokser >500 LOC, splittes auth-handlers ud i egen commit.

---

## Part A — REST Connector

### 1. Config-shape (uændret fra eksisterende `DataSourceConfig`)

`packages/shared/src/pipeline.ts` har allerede:

```ts
export interface DataSourceConfig {
  sourceType: "rest" | "sql" | "file";
  url: string;
  method: "GET" | "POST" | "PUT" | "DELETE";
  headers: Record<string, string>;
  authType: "none" | "bearer" | "basic";
}
```

**Ændring:** Tilføj `"api_key"` til `AuthType`, og tilføj felter til Zod-schema:

```ts
export type AuthType = "none" | "bearer" | "basic" | "api_key";

export interface DataSourceConfig {
  sourceType: DataSourceType;
  url: string;
  method: HttpMethod;
  headers: Record<string, string>;
  authType: AuthType;
  // NY — kun relevante for hver auth-type, valideret per-type
  body?: string;              // POST/PUT body (string, JSON-stringified af bruger)
  bearerToken?: string;       // authType=bearer
  basicUsername?: string;     // authType=basic
  basicPassword?: string;     // authType=basic
  apiKeyHeader?: string;      // authType=api_key (header navn, fx "X-API-Key")
  apiKeyValue?: string;       // authType=api_key
}
```

Zod-schema får `superRefine` der kræver de relevante felter pr. `authType`.

### 2. `RestDataSourceExecutor` (Python)

Erstatter `StubDataSourceExecutor` for `sourceType == "rest"`. SQL/File falder
tilbage til stub-data (med en `# TODO: replace when SQL/File connector lands`).

```python
class DataSourceExecutor(NodeExecutor):
    """Routes by sourceType. REST is real; SQL/File still stub."""

    @classmethod
    def manifest(cls) -> ConnectorManifest:
        return ConnectorManifest(
            name="Data Source",
            description="Fetch data from REST/SQL/File",
            node_type="datasource",
            required_fields=["sourceType"],
        )

    def validate_config(self, config: dict) -> list[ConfigError]:
        # Mirror Zod-rules: per-authType requirements + URL scheme check
        ...

    def execute(self, config: dict, input_data: Any) -> ExecutorResult:
        if config["sourceType"] == "rest":
            return _execute_rest(config)
        # Existing stub-data path
        return _execute_stub(config)

    def redact(self, output: dict) -> dict:
        # See Part B
        ...
```

### 3. HTTP-execution

Bruger `httpx.Client` (sync) med fixed 30s timeout — engine kører allerede i
`asyncio.to_thread`, så blocking-IO er fint.

```python
def _execute_rest(config: dict) -> ExecutorResult:
    headers = _build_headers(config)
    auth = _build_auth(config)
    body = config.get("body")

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.request(
                method=config["method"],
                url=config["url"],
                headers=headers,
                auth=auth,
                content=body if body else None,
            )
    except httpx.TimeoutException:
        raise PipelineError(
            code=ErrorCode.CONNECTOR_TIMEOUT,
            message=f"Request to {config['url']} timed out after 30s",
            status_code=504,
        )
    except httpx.HTTPError as e:
        raise PipelineError(
            code=ErrorCode.CONNECTOR_NETWORK_ERROR,
            message=f"Network error: {e}",
            status_code=502,
        )

    if response.status_code in (401, 403):
        raise PipelineError(
            code=ErrorCode.CONNECTOR_AUTH_FAILED,
            message=f"Authentication failed (HTTP {response.status_code})",
            status_code=502,
        )
    if response.status_code == 429:
        raise PipelineError(
            code=ErrorCode.CONNECTOR_RATE_LIMITED,
            message="Rate limited by upstream",
            status_code=502,
        )
    if response.status_code >= 400:
        raise PipelineError(
            code=ErrorCode.CONNECTOR_HTTP_ERROR,  # NY
            message=f"HTTP {response.status_code}: {response.reason_phrase}",
            status_code=502,
            details={"status": response.status_code, "url": config["url"]},
        )

    # Parse body — JSON if content-type is application/json, else raw text
    return ExecutorResult(
        output={
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": _parse_body(response),
            "url": config["url"],
        }
    )
```

**Ny `ErrorCode`:** `CONNECTOR_HTTP_ERROR` (4xx/5xx fra upstream der ikke er
auth/rate-limit). Tilføjes til enum'en i `app/core/errors.py`.

### 4. Auth-handlers

```python
def _build_auth(config: dict) -> httpx.Auth | None:
    auth_type = config.get("authType", "none")
    if auth_type == "basic":
        return httpx.BasicAuth(
            username=config.get("basicUsername", ""),
            password=config.get("basicPassword", ""),
        )
    return None  # bearer/api_key applied via headers

def _build_headers(config: dict) -> dict[str, str]:
    headers = dict(config.get("headers", {}))
    auth_type = config.get("authType", "none")
    if auth_type == "bearer":
        headers["Authorization"] = f"Bearer {config.get('bearerToken', '')}"
    elif auth_type == "api_key":
        key_header = config.get("apiKeyHeader", "X-API-Key")
        headers[key_header] = config.get("apiKeyValue", "")
    return headers
```

### 5. Tests (target ~15 nye tests)

| Test | Asserts |
|------|---------|
| `test_rest_get_returns_json_body` | mock'd 200 JSON → output.body er parsed dict |
| `test_rest_get_returns_text_body` | mock'd 200 text/plain → output.body er str |
| `test_rest_post_includes_body` | request mock asserter body-content |
| `test_rest_bearer_adds_authorization_header` | header asserts |
| `test_rest_basic_uses_httpx_basicauth` | BasicAuth(...) brugt |
| `test_rest_api_key_uses_custom_header` | apiKeyHeader respekteret |
| `test_rest_timeout_raises_connector_timeout` | TimeoutException → CONNECTOR_TIMEOUT |
| `test_rest_401_raises_auth_failed` | mock 401 → CONNECTOR_AUTH_FAILED |
| `test_rest_429_raises_rate_limited` | mock 429 → CONNECTOR_RATE_LIMITED |
| `test_rest_500_raises_http_error` | mock 500 → CONNECTOR_HTTP_ERROR |
| `test_rest_invalid_json_falls_back_to_text` | malformed JSON → str body |
| `test_rest_validate_config_requires_url` | validation |
| `test_rest_validate_config_bearer_requires_token` | validation |
| `test_rest_validate_config_api_key_requires_value` | validation |
| `test_datasource_routes_sql_to_stub` | sql/file stadig stub-path |

Mocking: `httpx.MockTransport` (built-in, ingen ny dep).

### 6. Manuel demo

```bash
# Lancér en pipeline der GET'er api.github.com/users/octocat
curl -X POST http://localhost:8000/api/v1/runs/async \
  -H "Content-Type: application/json" \
  -d '{
    "pipeline": {
      "id": "test", "name": "github-demo",
      "nodes": [{
        "id": "n1", "type": "datasource",
        "data": { "label": "GitHub", "nodeType": "datasource",
          "config": {
            "sourceType": "rest",
            "url": "https://api.github.com/users/octocat",
            "method": "GET",
            "headers": {"User-Agent": "gridlane-test"},
            "authType": "none"
          }
        }
      }],
      "edges": []
    }
  }'

# Se SSE-stream — body fra GitHub skal komme i step_completed.payload.output
curl -N http://localhost:8000/api/v1/runs/<RUN_ID>/stream
```

---

## Part B — `redact()` Contract i `NodeExecutor` ABC

### Problem

I dag emit'er coordinator `step_completed`-events med executor's rå `output` dict.
Hvis en REST-connector returnerer `Authorization`-headers eller en SQL-connector
returnerer rådata fra DB, ender det i:

1. `run_events` tabellen (læselig fra alle der har `run_id`)
2. SSE-streamen (publik per dagens auth-status)

### Threat Model

- **In scope:** Ufrivillig læk af credentials/PII via SSE og event log.
- **Out of scope:** Ondsindet executor (vi tillider connector-koden). RLS på
  `run_events` (afventer auth).

### Design

Tilføj abstract method med default identity-implementation:

```python
class NodeExecutor(ABC):
    ...
    def redact(self, output: dict[str, Any]) -> dict[str, Any]:
        """Strip sensitive fields before output enters the public event stream.

        Default returns output unchanged. Override per executor to mask fields
        like response headers (Authorization, Set-Cookie), credentials, raw DB
        rows from privileged queries, etc.

        Contract:
          - Must NOT mutate the input dict; return a new dict.
          - Output of redact() goes into SSE events + run_events.payload.
          - Raw output is still passed as input_data to the next step (and
            stored in step_results.output_data, which will be auth-gated when
            auth lands).
        """
        return output
```

### `DataSourceExecutor.redact()` (REST-specific)

```python
SENSITIVE_HEADER_NAMES = {"authorization", "cookie", "set-cookie", "x-api-key"}

def redact(self, output: dict) -> dict:
    redacted = dict(output)
    if "headers" in redacted and isinstance(redacted["headers"], dict):
        redacted["headers"] = {
            k: ("[REDACTED]" if k.lower() in SENSITIVE_HEADER_NAMES else v)
            for k, v in redacted["headers"].items()
        }
    return redacted
```

### Integration Point

I `RunCoordinator._run` → `pending_events`-pipeline og i `engine.execute`'s
emit-callback for `step_completed`. Konkret: engine'en holder allerede en
reference til hver step's executor for `validate_config` — gem den, og kald
`executor.redact(output)` *kun* for event-payloads.

```python
# I execution.py, hvor step_completed payload bygges:
emit("step_completed", {
    "node_id": node["id"],
    "output": executor.redact(result.output),  # NEW
    "duration_ms": ...,
    "token_usage": result.token_usage,
    "cost_usd": result.cost_usd,
})

# Men step_results.output_data persisteres som result.output (uændret)
```

### Tests

- `test_default_redact_is_identity` — base-klasse upåvirket
- `test_datasource_redact_strips_authorization_header` — header masked
- `test_datasource_redact_does_not_mutate_input` — input dict uændret
- `test_step_completed_event_uses_redacted_output` — integrationstest med fake executor der returnerer "secret"
- `test_step_results_table_stores_unredacted_output` — DB row har raw

---

## Part C — Retro Quick-Wins

### C1 — Last-Event-ID cap

`apps/engine/app/api/v1/endpoints/runs.py`:

```python
MAX_LAST_EVENT_ID = 100_000

def _parse_last_event_id(header_value: str | None) -> int:
    if not header_value:
        return -1
    try:
        value = int(header_value)
    except (TypeError, ValueError):
        return -1
    if value < -1 or value > MAX_LAST_EVENT_ID:
        return -1
    return value
```

Test: `test_parse_last_event_id_caps_unrealistic_values`.

### C2 — Heartbeat-interval via env

Flyt `HEARTBEAT_INTERVAL_SECONDS = 15` til `app/core/config.py`:

```python
class Settings(BaseSettings):
    ...
    sse_heartbeat_seconds: int = 15
    sse_heartbeat_seconds_test: int = 1  # used in test config override
```

Endpoint reader fra `settings.sse_heartbeat_seconds`. Test sets
`SSE_HEARTBEAT_SECONDS=1` for hurtige heartbeat-tests.

Test: `test_heartbeat_emitted_when_no_events_arrive` (med 1s interval, vent 1.5s,
asserter at en `comment`-event blev sendt).

### C3 — Graceful shutdown — orphaned runs cleanup

FastAPI lifespan event på app-startup:

```python
# apps/engine/app/main.py
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_session() as session:
        service = RunService(session)
        marked = await service.mark_orphaned_runs_failed(
            older_than=timedelta(hours=1)
        )
        if marked:
            logger.warning("Marked %d orphaned runs as failed on startup", marked)
        await session.commit()
    yield
```

Service-method:

```python
async def mark_orphaned_runs_failed(self, older_than: timedelta) -> int:
    cutoff = datetime.now(UTC) - older_than
    stmt = (
        update(PipelineRunModel)
        .where(
            PipelineRunModel.status == "running",
            PipelineRunModel.started_at < cutoff,
        )
        .values(
            status="failed",
            completed_at=datetime.now(UTC),
            # No error column; document via run_events instead
        )
        .returning(PipelineRunModel.id)
    )
    result = await self.session.execute(stmt)
    return len(result.fetchall())
```

Test: `test_mark_orphaned_runs_failed_marks_old_running_runs`,
`test_does_not_touch_recent_running_runs`,
`test_does_not_touch_already_terminal_runs`.

---

## Migrations

Ingen schema-ændringer.

## Backward Compat

- Sync `POST /runs` bevares (gør allerede).
- `DataSourceExecutor` afløser `StubDataSourceExecutor` i registry — eksisterende
  pipelines med `sourceType: "rest"` får nu *rigtigt* HTTP-kald i stedet for
  fake data. **Dette er et behavior-break for eksisterende test-pipelines** — vi
  noterer det i PR-beskrivelsen og opdaterer evt. seed-data hvis det breaker
  dev-flowet.
- `redact()` har default = identity, så eksisterende stub-executors uændrede.

## Risiko-register

| Risiko | Impact | Mitigation |
|--------|--------|------------|
| `httpx.Client` blocker event-loop | HIGH | Engine kører allerede i `to_thread`, så ok |
| Store response bodies fylder DB | MED | Cap output ved 1MB i C2-iteration hvis problem |
| Auth-fejl returnerer cleartext token i error-message | HIGH | Error-message må ALDRIG inkludere token-værdi (kun status code) |
| `redact()` overset i fremtidige connectors | MED | Default-implementation = no-op, så ingen runtime-fejl, men dokumentér i `NodeExecutor` docstring |
| Orphan-cleanup rammer en kørende run hvis startup-task race'er en igangværende run | LOW | Cutoff = 1 time, single-worker antagelse → ingen run kører >1 time uden checkpoint |

## Acceptance Criteria

- [ ] `pnpm test` grøn (frontend + backend)
- [ ] Manuel demo: REST-pipeline mod `api.github.com/users/octocat` viser body i UI
- [ ] SSE-stream viser `[REDACTED]` for `Authorization`-header (manuel verifikation)
- [ ] E2E test passes: real ASGI server + httpx.AsyncClient.stream() ser
      `step_started` → `step_completed` → `run_completed`
- [ ] Startup-log viser "Marked 0 orphaned runs" på frisk DB
- [ ] PR-beskrivelse linker til denne spec
