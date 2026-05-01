# Retrospective: REST Connector + Debt Bundle (Sprint 6B Phase 1b + 1c)

> Dato: 2026-05-01
> Scope: 4 commits across 2 stacked branches — Phase 1b (run history UI) and Phase 1c (REST connector, redact contract, retro debt-fixes)
> Resultat: 253 tests grønne (143 BE + 110 FE), CI ikke kørt endnu

## Hvad blev shipped

End-to-end "rigtig connector"-oplevelse + tre SSE-retro quick-wins i samme PR-bundle:

- **Phase 1b** — Run history sheet, ny `RunSummary` shared type (fix af PipelineRun-mismatch), `listRuns` + `getRun` engine-api helpers, History-knap i toolbar, genbrug af eksisterende `RunResultsPanel` til historiske runs
- **Phase 1c — debt-fixes** — Last-Event-ID cap (MAX 100k), heartbeat-interval via `sse_heartbeat_seconds` env, lifespan handler der marker orphaned runs failed på startup
- **Phase 1c — REST connector** — `DataSourceExecutor` der router by `sourceType` (rest → httpx, sql/file → stub), 4 auth-typer (none/bearer/basic/api_key), strukturerede errors (`CONNECTOR_TIMEOUT`/`AUTH_FAILED`/`RATE_LIMITED`/`HTTP_ERROR`), auth-credentials lækker aldrig i error-payloads
- **Phase 1c — redact()-kontrakt** — `NodeExecutor.redact()` ABC method (default identity), `DataSourceExecutor`-override masker 5 sensitive headers, engine fail-safe (redact-fejl → `{"_redact_failed": True}` i stedet for crash eller leak)
- **Phase 1c — frontend** — `AuthType += "api_key"`, nye optional config-fields, Zod superRefine per-authType validation, datasource-config-form viser de relevante input baseret på auth-valg
- **Phase 1c — e2e SSE test** — første test der eksercerer SSE-wireformat over rigtig ASGI transport. Fangede en bug: `\r\n` line endings ville få naive `\n\n` split til at miste events

## Hvad gik godt

### Arkitektur
1. **`redact()` som default-identity ABC** — backwards-compatible by design. Alle eksisterende stub-executors fungerer uændret, kun connectors med ægte sensitive output behøver override.
2. **Engine fail-safe pattern** — hvis custom `redact()` raiser, payload bliver `{"_redact_failed": True}` snarere end at lække data eller crash run. Sikkerheden vinder over UX i grænse-cases.
3. **`DataSourceExecutor` router by `sourceType`** — REST kan være rigtig nu, SQL/File bevarer stub-data indtil de er færdige. Ingen breaking change for pipelines med SQL/File configs.
4. **httpx.MockTransport** — 12 connector-tests uden ægte netværk. Mock kører på samme path som rigtig httpx.Client, så vi tester real auth-encoding (BasicAuth base64 osv.).
5. **3-lags DB-mock for e2e SSE-test** — get_db dependency override + async_session factory patch + RunService method patches. Komplekst, men tillod e2e-test uden Postgres.

### Process
1. **Spec-først betalte sig igen** — `redact()`-design var aftalt før første linje kode. Frontend og backend mirror hinanden uden iteration.
2. **Stacked branches (1b → 1c)** holdt main rent. 1b kunne reviewes selvstændigt mens 1c blev bygget.
3. **3 commits i 1c branch** (debt → connector → e2e) gør git log selvdokumenterende. Bedre end stacked PRs når commits rammer samme files.
4. **Type-mismatch fundet under 1b** (RunHistoryResponse skulle returnere RunListItem, ikke PipelineRun) blev fikset inline i samme commit i stedet for at blive hængende som tech-debt.
5. **TDD red→green for executor + redact** fangede en initial bug: jeg glemte at `_build_headers` skulle merge user headers først *før* auth headers — testen failed instantly fordi en custom Authorization-header overskrev bearer-tokenet.

## Hvad kunne være bedre

### Testdækning
1. **Heartbeat-test mangler aktiv verifikation** — settings er konfigurerbare nu, men ingen test sender en idle stream gennem 1.5 × heartbeat-interval og asserter at en `: keepalive`-frame ankom. **Action:** Pytest test der sætter `sse_heartbeat_seconds=0.5` og venter på keepalive.
2. **Lifespan handler ikke e2e-testet** — `mark_orphaned_runs_failed` er unit-testet, men ikke at lifespan kalder den korrekt. **Action:** Brug `LifespanManager` (asgi-lifespan) eller `httpx.AsyncClient` med lifespan="on" for at trigge startup.
3. **`RunHistoryPanel` komponent ikke DOM-testet** — alle store/api tests, men ingen verifikation af "klik histurow → setCurrentRun called". **Action:** testing-library tests for open → list → click flow.
4. **Ingen test for store-response bodies** — REST connector parser hele body i RAM. Test med 10MB response ville fange en regression hvis vi nogensinde skifter til streaming.

### Robusthed
1. **`redact()` kører i engine-thread** — for store outputs (MB) blokerer det step-progressen. **Action:** Flyt redact til coordinator emit-callback hvis det bliver problem.
2. **REST timeout er hardcoded 30s** — bør være per-pipeline eller per-step config. **Action:** Tilføj `timeoutSeconds?: number` til `DataSourceConfig`.
3. **Ingen retry på connector-failures** — første 5xx eller timeout fra upstream = run failer instant. For flaky APIs er det too aggressive. **Action:** Tilføj retry-policy til config (max 3 retries med exponential backoff, default off).
4. **Body parsing antager text/json** — binær response (image/octet-stream) ville crash ved `.text`. **Action:** Content-type sniffing → base64-encode binær.
5. **Orphaned-cleanup checker `status='running'`, ikke `completed_at IS NULL`** — hvis en run nogensinde sætter status='running' uden completed_at, vil de blive ramt to gange. Lavt risk men skift til kombineret check.

### Sikkerhed
1. **`SENSITIVE_HEADER_NAMES` er hardcoded liste på 5 entries** — vendor-specifikke headers (X-Vault-Token, X-Atlassian-Token, X-Datadog-API-Key) lækker. **Action:** Gør konfigurerbar via env eller per-pipeline override.
2. **REST request body sendes uden mask** — hvis bruger lægger secret i body-feltet (fx OAuth client_secret i en token-request), kan vi ikke mask det. **Action:** Dokumentér i form-help text at sensitive secrets skal i auth-fields, ikke body.
3. **Run history Sheet er publik** — alle med UI-adgang ser ALLE pipelines' runs. Samme situation som SSE — afventer auth/RLS.
4. **Frontend gemmer bearer/api_key/basic-credentials i localStorage** (via Zustand persist hvis aktiveret) — vi har ikke aktiveret persist for pipeline-store endnu, men når vi gør, skal credentials *eksplicit ekskluderes*. **Action:** Skriv en partialize-funktion til Zustand persist.
5. **`_redact_failed: True`-marker leaker ingen data, men tæller heller ikke som metric** — kunne dække en buggy custom redact i månedsvis uden vi opdager det. **Action:** Log warning + prometheus counter når sentinel'en sættes.

### Observability
1. **Ingen counter for redact-failures, connector-timeouts, eller orphaned-cleanup hits** — vi har structured errors i payload, men ikke aggregated metrics. **Action:** Tilføj `prometheus-fastapi-instrumentator` + custom counters for connector-fejltyper.
2. **REST connector tracker ikke separat HTTP-duration** — `step.duration_ms` inkluderer både engine-overhead og HTTP RTT. **Action:** Tilføj `request_duration_ms` i output dict.
3. **Lifespan cleanup logger antal**, men ikke hvilke run_ids. Debugging produktion bliver svært. **Action:** Log run_ids på debug-niveau (ikke warning, så vi ikke spammer ved store cleanups).

### UX-mangler
1. **Run history mangler filter** — backend understøtter `pipelineId` query param, frontend ignorerer det. **Action:** Dropdown øverst i sheet for at filtrere.
2. **Klik på historisk run viser detail, men ingen "load pipeline" eller "rerun"** — bruger kan ikke nemt re-eksekvere den gamle pipeline. **Action:** Knap der loader `pipeline_snapshot` ind i canvas.
3. **REST body har ingen JSON-validering** — bruger kan skrive invalid JSON, fejlen kommer først runtime. **Action:** JSON.parse-precheck i form, vis inline error.
4. **Password-fields mangler "show password"-toggle** — ergonomisk gap når bruger debugger.
5. **Bearer/api_key inputs får browser-autofill** — kan irritere brugere med credential managers. **Action:** `autocomplete="off"` (eller `autocomplete="new-password"`).
6. **`run_history_panel` viser stale data ved close → reopen** — bevidst trade-off (skip lint-rule om setState i effect) men kunne vises bedre med en discrete "refreshing" badge i headeren.

## Feature-muligheder for next phase

### Foundation-relevant (kort sigt, 1-2 sessions hver)
1. **Auth + RLS** — login/signup UI, RLS på `pipelines`, `pipeline_runs`, `run_events`. Gør stream/cancel/history private. Lægger fundament for at "redact" kun gælder publik path; auth-gated detail view kan vise raw output.
2. **AI Executor med streaming** — udnyt SSE-bussen til Anthropic/OpenAI tokens. Beviser at arkitekturen skalerer til fine-grained sub-step events. Cost-tracking pr. step (felter er allerede der).
3. **SQL connector** — efter REST er mønsteret klart. Primært asyncpg/sqlalchemy + redact for query results. Sandsynligvis kortere end REST.
4. **File connector** (CSV/JSON lokalt; S3 senere) — adskilt fra SQL pga forskellig auth-model.
5. **Run history filter + replay** — color det ovenstående UX-debt i én session.

### B2B-grade (mellem sigt, 3-5 sessions hver)
1. **Per-pipeline secrets vault** — credentials ud af `DataSourceConfig`, ind i en encrypted store, refereret via `${secrets.github_token}` syntax.
2. **Connector retry-policy** — config-level med exponential backoff og circuit breaker.
3. **Webhook trigger** — pipeline kan udløses fra ekstern HTTP-call.
4. **Schedule trigger** — cron-baseret pipeline execution.
5. **HUMAN approval step** — pause → review-link → approve/reject → resume. Bruger SSE til at signalere "venter på approval".
6. **Conditional edges** — if-baseret flow på output-content.

### Enterprise-grade (lang sigt)
1. **Audit log** — alle bruger-actions i append-only log
2. **Role-based access** — owner/editor/viewer per pipeline
3. **Workspace/team-isolation** — multi-tenant med RLS pr workspace_id
4. **Cost budgets** — månedlig OpenAI/Anthropic-cost cap
5. **SOC2/GDPR mode** — DPIA-kompatibel, EU-region deploy, BYOK encryption-at-rest

## Anbefalet næste fase

**Top 3 prioriteret efter foundation-værdi vs. effort:**

1. **Auth + RLS** (Sprint 6C foreslag)
   - Blokerer ALT andet i prod-readiness
   - Supabase-infrastrukturen er allerede der
   - Bagefter kan vi træde tilbage på `redact()`s aggressivitet (auth-gated detail view kan vise raw output)
   - Estimat: 2-3 sessions

2. **AI Executor med streaming** (Sprint 6D foreslag)
   - Mest produktværdi pr. udvikler-time
   - Eksercerer hele SSE + redact stakken vi netop har bygget
   - Anthropic + OpenAI BYOK
   - Estimat: 2-3 sessions

3. **SQL connector** (Sprint 6E foreslag)
   - Følger REST-pattern direkte
   - Lavt risk efter REST har bevist arkitekturen
   - Estimat: 1-2 sessions

## Læring til mig selv (Simon)

- **Stacked branches er ikke automatisk det rigtige valg** — hvis 3 commits rammer samme filer i koordineret mønster, giver én branch + 3 commits samme reviewability uden rebase-friction. Stacking giver først value når commits er fagligt distinct og kan merges hver for sig.
- **Type-mismatch mellem TS og Python schema er sin egen kategori af debt** — ikke "generel tech debt", men specifikt "schema drift". Værd at lave en periodisk sweep — fanger problemer før de kommer i prod.
- **`redact()` med default identity er bevidst valg, men det er "open by default"** — i en multi-tenant verden bør default være "deny by default" og connectors opt-in via en allow-list. Worth revisiting når auth lander og threat model skifter.
- **Mocking på 3 lag for én test = signal om mangelfuld test-infrastruktur** — værd at investere i SQLite eller pytest-postgres setup næste gang vi har behov for ægte integration tests.
- **`httpx.MockTransport`** kan også bruges til e2e — ikke kun unit. Hele REST → SSE → frontend kan testes uden netværk eller ægte server.
- **CQRS-light separation fra session 7 betalte sig igen** — at tilføje `redact()` mellem engine.execute → emit() krævede ZERO ændring i bus eller stream-endpoint. Ren add, ingen refactor. Det er signal på god arkitektur.
- **Sweep "kør existing tests først" efter refactor** — at omdøbe `StubDataSourceExecutor` → `DataSourceExecutor` brød 5 testfiler. Heldigvis fanget i første test-run. Gør altid en bare-rename-commit først (men det gjorde jeg ikke her — gør det næste gang).

## Strategisk overblik (status efter Sprint 6B)

Foundation-sprintet er nu **5/5 done** på den oprindelige plan:
- ✅ Pipeline canvas + 4 nodetyper
- ✅ Execution engine + run persistence
- ✅ Connector contract + config validation
- ✅ SSE progress reporting
- ✅ **Første rigtige connector (REST) + redact-contract**

Næste milesten: **Sprint 6C — Auth + RLS** (afhænger af Simons prioritering). Alternativt direkte til **AI Executor** for at maksimere produktværdi før auth-arbejdet.
