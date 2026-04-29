import { createClient } from "@supabase/supabase-js";

/**
 * Supabase client — singleton for browser-side access.
 *
 * Uses the anon key which is safe to expose in the browser.
 * RLS policies on the database control what data is accessible.
 * Without auth, the "allow all" dev policy lets everything through.
 */

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error(
    "Missing NEXT_PUBLIC_SUPABASE_URL or NEXT_PUBLIC_SUPABASE_ANON_KEY in environment",
  );
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
