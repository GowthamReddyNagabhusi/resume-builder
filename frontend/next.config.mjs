/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  async rewrites() {
    // Only proxy /api/* when a backend URL is explicitly configured.
    // On Vercel (production), the frontend calls the backend URL directly via NEXT_PUBLIC_API_URL,
    // so we skip the rewrite to avoid proxying to localhost:8000 which won't exist.
    const backendUrl = process.env.API_URL;
    if (!backendUrl || backendUrl.includes('localhost')) {
      return [];
    }
    return {
      fallback: [
        {
          source: '/api/:path*',
          destination: `${backendUrl}/api/:path*`,
        },
      ],
    };
  },
};

export default nextConfig;
