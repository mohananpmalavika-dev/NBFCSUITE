/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  transpilePackages: ['@nbfc-suite/ui'],
  images: {
    domains: ['localhost'],
  },
  experimental: {
    serverActions: true,
  },
}

module.exports = nextConfig
