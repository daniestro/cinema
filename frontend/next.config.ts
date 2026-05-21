import type { NextConfig } from 'next';

const config: NextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  images: {
    remotePatterns: [
      { protocol: 'http', hostname: 'localhost', pathname: '/media/**' },
      { protocol: 'http', hostname: 'minio', pathname: '/posters/**' },
    ],
  },
};

export default config;
