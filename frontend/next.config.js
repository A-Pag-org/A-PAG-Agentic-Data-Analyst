/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  // Remove standalone output for Vercel deployment
  // Vercel handles this automatically
  images: {
    domains: ['localhost'],
    unoptimized: process.env.NODE_ENV === 'development',
  },
  env: {
    NEXT_PUBLIC_APP_NAME: 'RAG Data Analyst',
    NEXT_PUBLIC_APP_VERSION: '0.1.0',
  },
  webpack: (config) => {
    config.resolve.alias.canvas = false;
    return config;
  },
  // Ensure proper handling of static exports
  poweredByHeader: false,
  compress: true,
  generateEtags: true,
};

module.exports = nextConfig;