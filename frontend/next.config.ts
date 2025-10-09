import type { NextConfig } from "next";
import { join } from "path";

const nextConfig: NextConfig = {
  // Ensure Next.js traces files from the monorepo root to avoid
  // multiple lockfile workspace inference warnings
  outputFileTracingRoot: join(process.cwd(), ".."),
  experimental: {
    optimizePackageImports: [
      "@chakra-ui/react",
      "@chakra-ui/icons",
      "framer-motion",
    ],
  },
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'a-pag.org',
        pathname: '/wp-content/uploads/**',
      },
    ],
  },
};

export default nextConfig;
