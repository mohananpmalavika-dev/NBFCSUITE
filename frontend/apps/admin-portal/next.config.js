/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  transpilePackages: ['@nbfc-suite/ui'],
  images: {
    domains: ['localhost'],
  },
}

module.exports = nextConfig
