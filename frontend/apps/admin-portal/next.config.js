/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  transpilePackages: ['@nbfc-suite/ui'],
  images: {
    domains: ['localhost'],
  },
  // Fix for workspace and lockfile issues
  experimental: {
    externalDir: true,
  },
  // Optimize bundle for production
  swcMinify: true,
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
  // Output configuration
  output: 'standalone',
}

module.exports = nextConfig
