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
        // Apple-style dark palette: near-black base (see globals.css), elevated grey
        // surfaces, one blue accent. Semantic tokens so components stay theme-agnostic.
        accent: { DEFAULT: "#0A84FF", hover: "#409CFF", soft: "#16233B" },
        ink: { DEFAULT: "#F5F5F7", soft: "#98989F" },
        surface: { DEFAULT: "#1C1C1E", muted: "#2C2C2E" },
        ok: "#30D158",
        warn: "#FF9F0A",
        bad: "#FF453A",
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
