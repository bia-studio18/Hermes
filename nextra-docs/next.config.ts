import type { NextConfig } from "next";
import nextra from "nextra";

const withNextra = nextra({
  defaultShowCopyCode: true,
  search: {
    codeblocks: false,
  },
});

const nextConfig: NextConfig = {
  /* Nextra handles configuration */
};

export default withNextra(nextConfig);
