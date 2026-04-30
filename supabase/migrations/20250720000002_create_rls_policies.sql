-- RLS policies for Gridlane
--
-- Strategy:
--   - Foundation phase: permissive policies for development
--   - user_id is nullable (no auth yet), so policies allow NULL user_id
--   - When auth is added: tighten to auth.uid() = user_id
--
-- The engine (FastAPI) connects via service_role key which bypasses RLS.
-- Frontend connects via anon key, so RLS applies to all frontend queries.

-- ── Enable RLS on all tables ────────────────────────────────────────

alter table pipelines enable row level security;
alter table pipeline_runs enable row level security;
alter table step_results enable row level security;

-- ── Pipelines ───────────────────────────────────────────────────────
-- Foundation: authenticated users can CRUD their own pipelines.
-- Unauthenticated (anon) can read/write during dev (user_id is NULL).

create policy "Users can read own pipelines"
  on pipelines for select
  to authenticated, anon
  using (
    user_id is null                          -- foundation: no auth yet
    or user_id = auth.uid()                  -- production: own data only
  );

create policy "Users can create pipelines"
  on pipelines for insert
  to authenticated, anon
  with check (
    user_id is null                          -- foundation: no auth yet
    or user_id = auth.uid()                  -- production: own data only
  );

create policy "Users can update own pipelines"
  on pipelines for update
  to authenticated, anon
  using (
    user_id is null
    or user_id = auth.uid()
  )
  with check (
    user_id is null
    or user_id = auth.uid()
  );

create policy "Users can delete own pipelines"
  on pipelines for delete
  to authenticated, anon
  using (
    user_id is null
    or user_id = auth.uid()
  );

-- ── Pipeline Runs ───────────────────────────────────────────────────
-- Users can see their own run history.
-- Engine inserts via service_role (bypasses RLS).

create policy "Users can read own runs"
  on pipeline_runs for select
  to authenticated, anon
  using (
    user_id is null
    or user_id = auth.uid()
  );

-- Anon/authenticated can insert runs during foundation phase.
-- In production, only the engine (service_role) should insert runs.
create policy "Allow run creation during foundation"
  on pipeline_runs for insert
  to authenticated, anon
  with check (
    user_id is null
    or user_id = auth.uid()
  );

-- ── Step Results ────────────────────────────────────────────────────
-- Step results are readable if the parent run is readable.
-- Inserts happen via service_role (engine) only.

create policy "Users can read steps for own runs"
  on step_results for select
  to authenticated, anon
  using (
    exists (
      select 1 from pipeline_runs
      where pipeline_runs.id = step_results.run_id
      and (pipeline_runs.user_id is null or pipeline_runs.user_id = auth.uid())
    )
  );

-- Allow step insertion during foundation phase (engine uses service_role in production)
create policy "Allow step creation during foundation"
  on step_results for insert
  to authenticated, anon
  with check (true);
