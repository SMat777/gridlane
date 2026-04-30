# Spec: SSE Progress Reporting

> Status: draft → implementation
> Owner: Simon
> Sprint: 6B (Foundation)
> Phase: 1a (split into 3 PRs)

## Goal

Stream live, per-step pipeline execution progress from the FastAPI engine to
the Next.js canvas, with first-class support for cancellation, reconnection,
and proxy/load-balancer compatibility — to match the observability bar that
medium-sized businesses expect when evaluating Gridlane against tools like
n8n, Workato, Prefect, and Zapier.

## Non-Goals (this phase)

- Multi-client viewing of the same run (requires auth/RLS — phase 2)
- Per-step token streaming for AI nodes (lands with the AI executor)
- Backpressure / slow-consumer handling beyond a bounded queue
- WebSocket bidirectional channels
- Persistent event log replay outside DB (no Kafka, no Redis Streams)

## User-Visible Behavior

Run flow from a user's perspective:

1. User clicks **Run**. Toolbar shows *Running step 1 of 4*.
2. Each step transitions visibly: *pending → running → completed/failed*.
3. Cumulative cost and elapsed time tick live in the run-results panel.
4. User can click **Stop**. The current step finishes; remaining steps are
   marked `cancelled` and the run ends with `status=cancelled`.
5. If the network drops, the panel reconnects silently and resumes from where
   it left off (no duplicate or missing events).
6. If the run finishes while the user is on another tab, the panel still shows
   the final result on return — the engine and DB don't depend on the tab.

## API Contract

### POST `/api/v1/runs` — async launch

**Behavior change** from current sync return.

```http
POST /api/v1/runs
Content-Type: application/json

{ "pipeline": { ... } }
```

**Response (202 Accepted):**

```json
{
  "run_id": "uuid",
  "status": "running",
  "stream_url": "/api/v1/runs/{run_id}/stream"
}
```

The engine starts executing in a background task. Existing tests that assert
on the full sync result will need to be migrated.

### POST `/api/v1/runs/{run_id}/cancel` — request cancellation

**Response (200 OK):**

```json
{ "run_id": "uuid", "status": "cancelling" }
```

If run already finished: returns `409 Conflict` with current status.

Cancellation is **cooperative**: a cancel flag is set and the engine checks it
between steps. The current step is allowed to finish (avoid leaving connectors
in an inconsistent state). Remaining steps are marked `cancelled` and the run
finalizes with `status=cancelled`.

### GET `/api/v1/runs/{run_id}/stream` — SSE event stream

**Headers:**

```http
Accept: text/event-stream
Cache-Control: no-cache
Last-Event-ID: <last seen event id>   # optional, for resume
```

**Response:** `Content-Type: text/event-stream`

#### Event Format

Every event has an `id`, an event-`event:` name, and a JSON `data:` payload.

```text
id: 0
event: run_started
data: {"run_id":"...","pipeline_name":"...","total_steps":4,"started_at":"..."}

id: 1
event: step_started
data: {"node_id":"node_1","node_label":"Source","node_type":"datasource","order":0,"started_at":"..."}

id: 2
event: step_completed
data: {"node_id":"node_1","status":"completed","duration_ms":142,"output":{...},"completed_at":"...","cumulative_cost_usd":0.000}

id: 3
event: step_failed
data: {"node_id":"node_2","status":"failed","error":"...","duration_ms":89,"completed_at":"..."}

id: 4
event: run_completed
data: {"run_id":"...","status":"completed","total_duration_ms":1240,"total_cost_usd":0.012,"completed_at":"..."}

id: 5
event: run_failed
data: {"run_id":"...","status":"failed","error":"...","total_duration_ms":234}

id: 6
event: run_cancelled
data: {"run_id":"...","status":"cancelled","completed_at":"..."}
```

Plus heartbeat (comment-event, no `id:`):

```text
: keepalive
```

Sent every 15 seconds while the connection is open.

#### Event ID Semantics

- `id:` is a per-run monotonically increasing integer (0..N).
- IDs are stable: replay with `Last-Event-ID: 3` returns events 4+ in order.
- Persisted to DB so reconnection works after server restart.

#### Stream Lifecycle

| Run state on connect | Behavior |
|---|---|
| Run is `running` | Stream live events as engine emits |
| Run already finished | Replay all events from DB, then close stream |
| Run not found (unknown UUID) | 404 |
| Last-Event-ID provided, run still running | Replay events > Last-Event-ID from DB, then attach to live |
| Last-Event-ID >= latest event AND run finished | Send only the terminal event, then close |

Stream closes after a terminal event (`run_completed`/`run_failed`/`run_cancelled`).

## State Machine

```
                  ┌─ cancel requested
                  ▼
   pending ──► running ──► cancelling ──► cancelled
                  │
                  ├──► completed
                  └──► failed
```

`pending` exists only briefly between `INSERT` and the engine's first action.
The launch endpoint may return `running` immediately if the engine is already
processing.

`cancelling` is the transient state where the cancel flag has been set but the
current step hasn't yet checked it. It is observable via GET /runs/{id} and the
cancel endpoint, but the SSE stream only emits `run_cancelled` (final).

## Database

### `pipeline_runs` (existing)

The `status` CHECK already includes all five states. No schema change needed
for status. We **will** need:

- `cancel_requested` boolean (default false) — to coordinate cancellation
  between the cancel endpoint and the running engine.

### `run_events` (new)

```sql
create table run_events (
  id          bigserial primary key,        -- global event id (DB-assigned)
  run_id      uuid not null references pipeline_runs(id) on delete cascade,
  sequence    integer not null,             -- per-run sequence (0..N)
  event_type  varchar(32) not null
              check (event_type in (
                'run_started', 'step_started', 'step_completed',
                'step_failed', 'run_completed', 'run_failed', 'run_cancelled'
              )),
  payload     jsonb not null,
  created_at  timestamptz not null default now(),
  unique (run_id, sequence)
);

create index idx_run_events_run_id_sequence on run_events(run_id, sequence);
```

Events are append-only. The unique constraint guarantees ordered replay even
under concurrent writes (which we don't have in single-engine mode, but
defensive in case of future scale-out).

### `step_results` (existing)

No schema change. Rows are now upserted progressively as steps complete
(currently inserted in batch when the run finishes).

## In-Process Architecture

```
                   ┌──── HTTP ────┐
   POST /runs ─────► API endpoint ├─► RunService.create_pending_run() ─► DB
                   │              │
                   │              ├─► RunCoordinator.launch(run_id, pipeline)
                   │              │      └─► asyncio.create_task(execute(...))
                   │              │
                   │              └─◄─ 202 { run_id }

   GET /runs/{id}/stream ─────────► API endpoint ─► RunCoordinator.subscribe(run_id)
                                          │             │
                                          │             ├─► if running: live queue
                                          │             └─► if finished: DB replay
                                          │
                                          └─◄─ text/event-stream

   POST /runs/{id}/cancel ────────► API endpoint ─► RunCoordinator.cancel(run_id)
                                                       └─► sets cancel flag

   ExecutionEngine.execute() (per run, in background task)
        │
        ├─► emit('run_started')          ─► Bus + DB
        ├─► for each step:
        │     ├─► check cancel_flag      ─► if set: emit run_cancelled, exit
        │     ├─► emit('step_started')   ─► Bus + DB
        │     ├─► run executor           
        │     ├─► UPSERT step_results
        │     └─► emit('step_completed') ─► Bus + DB
        └─► emit('run_completed')        ─► Bus + DB
```

**RunCoordinator** owns:
- A dict `run_id → RunChannel` for live runs.
- Each `RunChannel` has: a bounded `asyncio.Queue` per subscriber, a cancel
  `asyncio.Event`, and a sequence counter.
- When a subscriber connects, the channel optionally replays missed events
  from DB (if `Last-Event-ID` set or run already terminal), then attaches to
  live events.
- After terminal event: channel is removed from the dict; new subscribers fall
  through to pure DB replay.

**Bounded queue size:** 256 events per subscriber. If a subscriber lags, drop
the oldest non-terminal events first (heartbeats are comment-only, not
buffered). Terminal events are never dropped. (Implementation note: in this
phase we keep it simple — 256 is generous for any realistic step count;
no subscriber should ever lag enough to overflow during foundation phase.)

## PR Plan

### PR a1 — Async run launch + cancel (backend, no SSE yet)

**Scope:**
- `cancel_requested` column on `pipeline_runs` (Supabase migration)
- `RunService.create_pending_run()` — INSERT with status=running
- `RunService.update_run_status()` — transition status + completion fields
- `RunService.upsert_step_result()` — progressive step persistence
- `RunCoordinator` skeleton — owns background tasks, cancel flags
- `POST /api/v1/runs` — returns 202 + run_id, launches `RunCoordinator.launch()`
- `POST /api/v1/runs/{run_id}/cancel` — sets flag, returns 200
- `ExecutionEngine.execute()`:
  - Accepts an optional `cancel_event: asyncio.Event` parameter
  - Checks the event between steps; finishes current step then marks rest as cancelled
  - Calls `RunService.upsert_step_result()` after each step (no DB dep yet — passed via callback)
- Existing GET /runs and GET /runs/{id} unchanged (backward compatible)
- Tests: state transitions, cancel mid-run, background task lifecycle, no-stream-yet returns same shape

**Out of scope for a1:** SSE endpoint, frontend changes, run_events table

**Frontend stays working** because:
- `POST /runs` still returns `{ run: ... }` for backward compat — we add an
  optional shape `{ run_id, status, stream_url }` that the FE can opt into in
  PR a3. For a1, FE keeps working with a polling fallback (already implicit).

Wait — that breaks the new contract. Better: PR a1 keeps POST /runs returning
the **full sync result** for compatibility, and adds NEW endpoints
`POST /api/v1/runs/async` and `POST /api/v1/runs/{id}/cancel`. PR a3 swaps the
frontend over to /runs/async. PR a4 (or follow-up) deprecates the sync /runs.

This avoids any moment where main is in a half-broken state.

### PR a2 — SSE stream endpoint + event bus (backend)

**Scope:**
- `run_events` table migration
- Event emission from engine via callback wired through coordinator
- `RunCoordinator.subscribe(run_id, last_event_id)` — async generator
- `GET /api/v1/runs/{run_id}/stream` — SSE endpoint
- 15-second heartbeat
- Last-Event-ID resume support
- DB replay path for already-finished runs
- Tests: live stream, replay-from-id, finished-run replay-then-close, heartbeat

**Out of scope:** frontend EventSource (stays in a3)

### PR a3 — Frontend EventSource + cancel UI

**Scope:**
- `engineApi.runPipelineStreaming()` — uses POST /runs/async + EventSource
- Pipeline store: `appendStep()`, `updateStepStatus()`, `setRunStatus()`
- `RunResultsPanel` shows pending/running/completed states per step
- Toolbar: "Run" → "Stop" toggle while running
- Cumulative cost ticker
- Reconnect: EventSource handles auto-reconnect; we pass Last-Event-ID via state
- Tests: store actions, panel renders for each state, abort flow

## Test Strategy

### Unit (engine)
- Cancel between steps marks rest as cancelled (PR a1)
- Cancel after final step is a no-op (run already done)
- Failed step still emits run_failed and finalizes status (PR a1)
- Event sequence numbers are 0..N with no gaps (PR a2)

### Integration (FastAPI testclient)
- POST /runs/async returns 202 + run_id immediately
- POST /runs/{id}/cancel transitions to cancelled (PR a1)
- GET /runs/{id}/stream streams events for a live run (PR a2)
- GET /runs/{id}/stream replays for a finished run (PR a2)
- Last-Event-ID resumes from correct point (PR a2)
- Heartbeats emitted every 15s (test with shorter interval) (PR a2)

### Frontend (vitest)
- EventSource integration: live updates → store (PR a3)
- Stop button calls cancel endpoint (PR a3)
- Reconnect after disconnect resumes via Last-Event-ID (PR a3)

### Manual verification (Simon)
- Start a 4-step pipeline, watch it tick live
- Hit Stop — verify current step finishes, rest cancelled
- Disconnect wifi, reconnect — verify state resumes correctly
- Open same run in second tab — both watch progress
  (NOTE: this is non-blocking for foundation; subscriber-fan-out works
   trivially in our architecture as long as RunChannel keeps multiple queues.)

## Security Notes

- Stream endpoint is **public** within foundation phase (matches current /runs).
  When auth lands: enforce that user_id of the run matches authenticated user.
- Cancel endpoint same — auth-gated when auth lands.
- Event payloads MUST NOT include secrets from connector configs (e.g., API
  keys). Connectors must redact in their output before emitting.
- Last-Event-ID is a hint, not a capability — server validates run access and
  ignores invalid IDs (silently starts from beginning of replay).

## Definition of Done (Phase 1a complete)

- All three PRs merged to main with CI green
- 157 → 200+ tests, all passing
- A live demo: 3-step pipeline with one slow step, click Stop mid-run,
  reconnect after browser close, see correct final state
- CONTEXT.md and next-session-plan updated
- Project log entry: SSE pattern, event-bus pattern, async run lifecycle
