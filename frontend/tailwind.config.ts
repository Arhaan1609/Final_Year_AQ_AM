import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0A0D14",
        card: "#111622",
        "card-hover": "#171F30",
        border: "#1E293B",
        "border-glow": "#334155",
        brand: {
          emerald: "#10B981",
          cyan: "#06B6D4",
          amber: "#F59E0B",
          crimson: "#EF4444",
          purple: "#8B5CF6",
        },
      },
      boxShadow: {
        "glow-emerald": "0 0 25px -5px rgba(16, 185, 129, 0.3)",
        "glow-cyan": "0 0 25px -5px rgba(6, 182, 212, 0.3)",
        "glow-amber": "0 0 25px -5px rgba(245, 158, 11, 0.3)",
        "glow-crimson": "0 0 25px -5px rgba(239, 68, 68, 0.4)",
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
