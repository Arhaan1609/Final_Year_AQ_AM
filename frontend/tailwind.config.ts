import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class", '[data-theme="dark"]'],
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Stitch & Material Design 3 Design Tokens
        primary: {
          DEFAULT: "var(--accent-telemetry, #0891B2)",
          container: "var(--primary-container, #E0F2FE)",
          "fixed-dim": "#ADC6FF",
          "fixed": "#D8E2FF",
        },
        secondary: {
          DEFAULT: "var(--accent-purple, #7C3AED)",
          container: "var(--secondary-container, #EDE9FE)",
          "fixed-dim": "#DDB7FF",
        },
        tertiary: {
          DEFAULT: "var(--accent-warning, #D97706)",
          container: "var(--tertiary-container, #FEF3C7)",
          "fixed-dim": "#FFB786",
        },
        error: {
          DEFAULT: "var(--accent-critical, #DC2626)",
          container: "var(--error-container, #FEE2E2)",
        },
        surface: {
          DEFAULT: "var(--bg-page, #F7F8FA)",
          dim: "var(--bg-page, #F7F8FA)",
          bright: "var(--bg-card, #FFFFFF)",
          variant: "var(--surface-variant, #E2E8F0)",
          container: {
            lowest: "var(--bg-card, #FFFFFF)",
            low: "var(--surface-container-low, #F8FAFC)",
            DEFAULT: "var(--bg-card, #FFFFFF)",
            high: "var(--surface-container-high, #F1F5F9)",
            highest: "var(--surface-container-highest, #E2E8F0)",
          },
        },
        "on-surface": {
          DEFAULT: "var(--text-primary, #0F172A)",
          variant: "var(--text-secondary, #475569)",
        },
        background: "var(--bg-page, #F7F8FA)",
        card: "var(--bg-card, #FFFFFF)",
        "card-hover": "var(--bg-card-hover, #F1F3F7)",
        border: "var(--border-subtle, #E4E7EC)",
        "border-glow": "var(--border-color, #CBD5E1)",
        brand: {
          emerald: "#059669",
          cyan: "#0891B2",
          amber: "#D97706",
          crimson: "#DC2626",
          purple: "#7C3AED",
        },
      },
      boxShadow: {
        "glow-emerald": "0 0 25px -5px rgba(5, 150, 105, 0.3)",
        "glow-cyan": "0 0 25px -5px rgba(8, 145, 178, 0.3)",
        "glow-amber": "0 0 25px -5px rgba(217, 119, 6, 0.3)",
        "glow-crimson": "0 0 25px -5px rgba(220, 38, 38, 0.4)",
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "pulse-fast": "pulse 1.2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
      },
    },
  },
  plugins: [],
};
export default config;
