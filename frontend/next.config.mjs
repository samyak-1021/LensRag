/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Produce a self-contained server bundle for a lean production Docker image.
  output: "standalone",
  // Page images are served by the FastAPI backend (/storage/...). We render them
  // with plain <img> tags, so no next/image remote-loader config is needed.
};

export default nextConfig;
