import { createClient } from "./supabase/client";
import type { PipelineDefinition } from "@gridlane/shared";

/**
 * Pipeline persistence — save and load pipelines from Supabase.
 *
 * The `pipelines` table stores:
 * - id: UUID (primary key)
 * - name: text
 * - definition: JSONB (the full pipeline: nodes, edges, timestamps)
 * - created_at / updated_at: auto-managed timestamps
 *
 * We store the entire PipelineDefinition as JSONB in `definition`.
 * This avoids normalizing nodes/edges into separate tables —
 * simpler for US1, and JSONB queries are fast enough for our scale.
 */

export async function savePipeline(
  pipeline: PipelineDefinition,
): Promise<{ id: string } | { error: string }> {
  const { data, error } = await createClient()
    .from("pipelines")
    .upsert(
      {
        id: pipeline.id,
        name: pipeline.name,
        definition: pipeline,
      },
      { onConflict: "id" },
    )
    .select("id")
    .single();

  if (error) {
    console.error("Failed to save pipeline:", error);
    return { error: error.message };
  }

  return { id: data.id };
}

export async function loadPipeline(
  id: string,
): Promise<PipelineDefinition | { error: string }> {
  const { data, error } = await createClient()
    .from("pipelines")
    .select("definition")
    .eq("id", id)
    .single();

  if (error) {
    console.error("Failed to load pipeline:", error);
    return { error: error.message };
  }

  return data.definition as PipelineDefinition;
}

export async function listPipelines(): Promise<
  Array<{ id: string; name: string; updatedAt: string }> | { error: string }
> {
  const { data, error } = await createClient()
    .from("pipelines")
    .select("id, name, updated_at")
    .order("updated_at", { ascending: false });

  if (error) {
    console.error("Failed to list pipelines:", error);
    return { error: error.message };
  }

  return data.map((row) => ({
    id: row.id,
    name: row.name,
    updatedAt: row.updated_at,
  }));
}
