/**
 * Server-side Supabase client with cookie-based auth.
 *
 * Use this in Server Components, Server Actions, and Route Handlers.
 * Reads/writes auth tokens from cookies so the user's session
 * carries through SSR without client-side hydration.
 *
 * Must be called inside an async context (Server Component or Action).
 */

import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";

export async function createClient() {
  const cookieStore = await cookies();

  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll();
        },
        setAll(cookiesToSet) {
          try {
            for (const { name, value, options } of cookiesToSet) {
              cookieStore.set(name, value, options);
            }
          } catch {
            // setAll is called from a Server Component where cookies
            // can't be set. This is expected during initial page load —
            // the middleware handles session refresh instead.
          }
        },
      },
    },
  );
}
