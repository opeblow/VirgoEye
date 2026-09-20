/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: "standalone",
  // Keep production builds within the small VPS's memory allowance.
  ...(process.env.VIRGO_SMALL_BUILD === "true" ? { experimental: { cpus: 1 } } : {}),
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${process.env.BACKEND_URL || "http://localhost:8000"}/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
