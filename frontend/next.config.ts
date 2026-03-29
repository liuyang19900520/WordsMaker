import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  env: {
    LAMBDA_FUNCTION_URL: process.env.LAMBDA_FUNCTION_URL ?? "",
  },
};

export default nextConfig;
