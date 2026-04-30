-- Gridlane schema — consolidated from Alembic + Supabase dashboard
--
-- 3 tables:
--   pipelines      — pipeline definitions (JSONB document store)
--   pipeline_runs  — execution history
--   step_results   — per-node results within a run
--
-- Improvements over previous Alembic migration:
--   - updated_at with auto-trigger
--   - status CHECK constraints (not unconstrained strings)
--   - NUMERIC(10,6) for cost fields (not float)
--   - composite index on (pipeline_id, started_at)
--   - user_id column ready for auth (nullable for now)

-- ── Helper: auto-update updated_at ──────────────────────────────────

create or replace function update_updated_at()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

-- ── Pipelines ───────────────────────────────────────────────────────

create table pipelines (
  id         uuid primary key default gen_random_uuid(),
  user_id    uuid references auth.users(id) on delete cascade,
  name       text not null default 'Untitled Pipeline',
  definition jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

comment on table pipelines is 'Pipeline definitions stored as JSONB documents';
comment on column pipelines.user_id is 'Owner — nullable during foundation phase (no auth yet)';
comment on column pipelines.definition is 'Full PipelineDefinition: nodes, edges, metadata';

create index idx_pipelines_user_id on pipelines(user_id);
create index idx_pipelines_updated_at on pipelines(updated_at desc);

create trigger set_pipelines_updated_at
  before update on pipelines
  for each row execute function update_updated_at();

-- ── Pipeline Runs ───────────────────────────────────────────────────

create table pipeline_runs (
  id                 uuid primary key default gen_random_uuid(),
  pipeline_id        uuid references pipelines(id) on delete set null,
  pipeline_name      varchar(255) not null,
  user_id            uuid references auth.users(id) on delete set null,
  status             varchar(20) not null default 'pending'
                     check (status in ('pending', 'running', 'completed', 'failed', 'cancelled')),
  started_at         timestamptz not null default now(),
  completed_at       timestamptz,
  total_duration_ms  integer,
  total_cost_usd     numeric(10,6),
  pipeline_snapshot  jsonb not null,
  created_at         timestamptz not null default now(),
  updated_at         timestamptz not null default now()
);

comment on table pipeline_runs is 'Execution history — one row per pipeline run';
comment on column pipeline_runs.pipeline_snapshot is 'Immutable copy of pipeline definition at execution time';
comment on column pipeline_runs.total_cost_usd is 'Sum of all step costs (NUMERIC for financial precision)';

create index idx_pipeline_runs_pipeline_id on pipeline_runs(pipeline_id);
create index idx_pipeline_runs_user_id on pipeline_runs(user_id);
create index idx_pipeline_runs_pipeline_started on pipeline_runs(pipeline_id, started_at desc);

create trigger set_pipeline_runs_updated_at
  before update on pipeline_runs
  for each row execute function update_updated_at();

-- ── Step Results ────────────────────────────────────────────────────

create table step_results (
  id             uuid primary key default gen_random_uuid(),
  run_id         uuid not null references pipeline_runs(id) on delete cascade,
  node_id        varchar(255) not null,
  node_type      varchar(50) not null,
  node_label     varchar(255) not null,
  status         varchar(20) not null default 'pending'
                 check (status in ('pending', 'running', 'completed', 'failed', 'cancelled')),
  "order"        integer not null,
  input_data     jsonb,
  output_data    jsonb,
  error          text,
  started_at     timestamptz,
  completed_at   timestamptz,
  duration_ms    integer,
  input_tokens   integer,
  output_tokens  integer,
  total_tokens   integer,
  cost_usd       numeric(10,6)
);

comment on table step_results is 'Per-node execution results within a pipeline run';

create index idx_step_results_run_id on step_results(run_id);
create index idx_step_results_run_order on step_results(run_id, "order");
