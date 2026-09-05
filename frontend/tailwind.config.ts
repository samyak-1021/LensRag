import type { Config } from "tailwindcss";

/**
 * Apple/iOS-inspired design tokens: SF system font, a calm neutral surface, one
 * blue accent, soft shadows and large rounded corners.
 */
const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          "-apple-system",
          "BlinkMacSystemFont",
          '"SF Pro Text"',
          '"SF Pro Display"',
          '"Helvetica Neue"',
          "Arial",
          "sans-serif",
        ],
      },
      colors: {
        accent: { DEFAULT: "#0A84FF", hover: "#0071e3", soft: "#EAF3FF" },
        ink: { DEFAULT: "#1d1d1f", soft: "#6e6e73" },
        surface: { DEFAULT: "#ffffff", muted: "#f5f5f7" },
        ok: "#34C759",
        warn: "#FF9F0A",
        bad: "#FF3B30",
      },
      boxShadow: {
        card: "0 1px 3px rgba(0,0,0,0.04), 0 10px 30px rgba(0,0,0,0.06)",
        soft: "0 1px 2px rgba(0,0,0,0.05)",
      },
      maxWidth: { content: "1140px" },
    },
  },
  plugins: [],
};

export default config;
