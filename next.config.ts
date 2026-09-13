import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  // Avoid picking up C:\Users\Darvin\package-lock.json as workspace root
  outputFileTracingRoot: path.join(__dirname),
};

export default nextConfig;
