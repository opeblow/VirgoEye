/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        virgo: {
          bg: "#f3faf6",
          panel: "#ffffff",
          border: "#d7e8df",
          accent: "#16a34a",
          accent2: "#84cc16",
          danger: "#dc2626",
          warn: "#d97706",
          ok: "#16a34a",
          dim: "#7c8f85",
          text: "#10251b",
          muted: "#55705f",
        },
      },
      fontFamily: {
        mono: ["JetBrains Mono", "ui-monospace", "monospace"],
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      keyframes: {
        scanline: {
          "0%": { transform: "translateY(-100%)" },
          "100%": { transform: "translateY(100%)" },
        },
        pulseDot: {
          "0%, 100%": { opacity: "0.3", transform: "scale(0.8)" },
          "50%": { opacity: "1", transform: "scale(1.2)" },
        },
        typewriterBlink: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0" },
        },
      },
      animation: {
        scanline: "scanline 3s ease-in-out infinite",
        pulseDot: "pulseDot 1.5s ease-in-out infinite",
        typewriterCursor: "typewriterBlink 0.8s step-end infinite",
      },
    },
  },
  plugins: [],
};
