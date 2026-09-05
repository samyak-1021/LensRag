/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Page images are served by the FastAPI backend (/storage/...). We render them
  // with plain <img> tags, so no next/image remote-loader config is needed.
};

export default nextConfig;
