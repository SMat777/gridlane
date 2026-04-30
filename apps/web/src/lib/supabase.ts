import { createClient, type SupabaseClient } from "@supabase/supabase-js";

/**
 * Supabase client — lazy singleton for browser-side access.
 *
 * Uses the anon key which is safe to expose in the browser.
 * RLS policies on the database control what data is accessible.
 * Without auth, the "allow all" dev policy lets everything through.
 *
 * Lazy initialization so `next build` doesn't crash when env vars
 * are missing (they're only needed at runtime, not build time).
 */

let _client: SupabaseClient | null = null;

export function getSupabase(): SupabaseClient {
  if (_client) return _client;

  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

  if (!supabaseUrl || !supabaseAnonKey) {
    throw new Error(
      "Missing NEXT_PUBLIC_SUPABASE_URL or NEXT_PUBLIC_SUPABASE_ANON_KEY in environment",
    );
  }

  _client = createClient(supabaseUrl, supabaseAnonKey);
  return _client;
}
