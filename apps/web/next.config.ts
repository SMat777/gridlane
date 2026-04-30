import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Transpile workspace packages that ship raw TypeScript (no build step).
  // Without this, Next.js would fail on .ts imports from @gridlane/shared.
  transpilePackages: ["@gridlane/shared"],
};

export default nextConfig;
