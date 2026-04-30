-- Append-only event log for pipeline run progress.
--
-- Backs the SSE stream endpoint:
--   - Every state transition during a run is appended here.
--   - Subscribers connecting late, or reconnecting with Last-Event-ID,
--     get a deterministic replay of missed events from this table.
--   - The (run_id, sequence) unique constraint ensures ordered replay
--     even under concurrent writes.

create table run_events (
  id          bigserial primary key,
  run_id      uuid not null references pipeline_runs(id) on delete cascade,
  sequence    integer not null,
  event_type  varchar(32) not null
              check (event_type in (
                'run_started',
                'step_started',
                'step_completed',
                'step_failed',
                'run_completed',
                'run_failed',
                'run_cancelled'
              )),
  payload     jsonb not null,
  created_at  timestamptz not null default now(),
  unique (run_id, sequence)
);

comment on table run_events is
  'Append-only event log for pipeline runs — backs the SSE stream and Last-Event-ID resume';
comment on column run_events.sequence is
  'Per-run monotonically-increasing event id, starts at 0';
comment on column run_events.payload is
  'Event-type-specific JSON: see docs/specs/sse-progress.md for shapes';

create index idx_run_events_run_id_sequence on run_events(run_id, sequence);
