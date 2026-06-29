/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api/v1',
    NEXT_PUBLIC_HRMS_API_URL: process.env.NEXT_PUBLIC_HRMS_API_URL || 'http://localhost:8012',
    NEXT_PUBLIC_ACCOUNTING_API_URL: process.env.NEXT_PUBLIC_ACCOUNTING_API_URL || 'http://localhost:8008',
  },
};

module.exports = nextConfig;
