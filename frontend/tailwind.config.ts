import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/features/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        obsidian: {
          DEFAULT: "#060814",
          depth:   "#0B0F20",
          layer:   "#101428",
        },
        aether: {
          indigo:  "#5B6CF9",
          violet:  "#9B59F5",
          teal:    "#22D3EE",
          purple:  "#A855F7",
          aurora:  "#38BDF8",
          rose:    "#F472B6",
          emerald: "#34D399",
          amber:   "#FBBF24",
        },
        border: "rgba(91, 108, 249, 0.12)",
        input: "rgba(91, 108, 249, 0.15)",
        ring: "#5B6CF9",
        background: "#060814",
        foreground: "#F0F4FF",
        primary: {
          DEFAULT: "#5B6CF9",
          foreground: "#060814",
        },
        secondary: {
          DEFAULT: "#9B59F5",
          foreground: "#F0F4FF",
        },
        destructive: {
          DEFAULT: "#F472B6",
          foreground: "#F0F4FF",
        },
        muted: {
          DEFAULT: "#3D4A6B",
          foreground: "#8892B0",
        },
        accent: {
          DEFAULT: "#22D3EE",
          foreground: "#060814",
        },
      },
      fontFamily: {
        display: ["var(--font-syne)", "Syne", "sans-serif"],
        body: ["var(--font-inter)", "Inter", "sans-serif"],
        mono: ["var(--font-jetbrains)", "JetBrains Mono", "monospace"],
      },
      backgroundImage: {
        "aether-grad": "linear-gradient(135deg, #5B6CF9, #9B59F5, #22D3EE)",
        "aether-card": "linear-gradient(135deg, rgba(91,108,249,0.08), rgba(34,211,238,0.04))",
        "aurora-sweep": "linear-gradient(90deg, #5B6CF9 0%, #9B59F5 40%, #22D3EE 100%)",
        "dot-grid": "radial-gradient(circle, rgba(91,108,249,0.06) 1px, transparent 1px)",
      },
      animation: {
        "orb-drift":   "orb-drift-1 18s ease-in-out infinite",
        "float":       "float 7s ease-in-out infinite",
        "aurora-scan": "aurora-scan 3s linear infinite",
        "shimmer":     "aether-shimmer 2s ease-in-out infinite",
        "pulse-soft":  "pulse 4s cubic-bezier(0.4,0,0.6,1) infinite",
        "spin-slow":   "spin 12s linear infinite",
      },
      keyframes: {
        float: {
          "0%,100%": { transform: "translateY(0)" },
          "50%":     { transform: "translateY(-12px)" },
        },
        "aurora-scan": {
          "0%":   { backgroundPosition: "0% 50%" },
          "100%": { backgroundPosition: "200% 50%" },
        },
        "aether-shimmer": {
          "0%,100%": { opacity: "0.5" },
          "50%":     { opacity: "1" },
        },
      },
      backdropBlur: {
        "aether": "24px",
      },
      borderRadius: {
        "aether": "14px",
        "aether-lg": "20px",
      },
    },
  },
  plugins: [],
};

export default config;
