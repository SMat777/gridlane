-- Add cancel_requested flag to pipeline_runs.
--
-- Used by the run coordinator + cancel endpoint to signal cooperative
-- cancellation to the running engine. The engine checks this flag between
-- steps; the current step is allowed to finish so connectors don't end up
-- in an inconsistent state.

alter table pipeline_runs
  add column cancel_requested boolean not null default false;

comment on column pipeline_runs.cancel_requested is
  'Cooperative cancel flag — set by POST /runs/{id}/cancel, polled by engine between steps';

-- Add unique constraint for upsert of step results.
--
-- The engine writes each step twice (start, then complete) so that reconnecting
-- clients see live state. ON CONFLICT (run_id, node_id) DO UPDATE makes that
-- atomic and idempotent. node_id is unique within a pipeline definition, so
-- (run_id, node_id) uniquely identifies one step within one run.

alter table step_results
  add constraint step_results_run_node_unique unique (run_id, node_id);
