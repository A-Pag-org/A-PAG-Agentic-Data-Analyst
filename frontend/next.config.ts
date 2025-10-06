import type { NextConfig } from "next";

const nextConfig: NextConfig = {
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
