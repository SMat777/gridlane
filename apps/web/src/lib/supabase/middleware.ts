/**
 * Supabase session refresh for Next.js middleware.
 *
 * Called on every request to keep the auth session alive.
 * Without this, JWT tokens expire after 1 hour and users
 * get silently logged out.
 *
 * During foundation phase (no auth), this is a no-op pass-through
 * that ensures the infrastructure is ready when auth is added.
 */

import { createServerClient } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";

export async function updateSession(request: NextRequest) {
  let supabaseResponse = NextResponse.next({ request });

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(cookiesToSet) {
          for (const { name, value } of cookiesToSet) {
            request.cookies.set(name, value);
          }
          supabaseResponse = NextResponse.next({ request });
          for (const { name, value, options } of cookiesToSet) {
            supabaseResponse.cookies.set(name, value, options);
          }
        },
      },
    },
  );

  // Refresh the session — this is what keeps users logged in.
  // IMPORTANT: don't remove this even if you don't use the user object.
  // It triggers the session refresh on the Supabase side.
  await supabase.auth.getUser();

  return supabaseResponse;
}
