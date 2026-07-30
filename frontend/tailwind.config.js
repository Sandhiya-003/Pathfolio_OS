/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          950: "#0B0D12",
          900: "#12141C",
          800: "#171A23",
          700: "#1F2330",
          600: "#2B2F3F",
          500: "#3A3F52",
        },
        parchment: {
          DEFAULT: "#ECE7DA",
          dim: "#C7C2B4",
          muted: "#9195AA",
        },
        seal: {
          gold: "#C9A24E",
          teal: "#4FD1C5",
          violet: "#9B8AFB",
          coral: "#E8735C",
        },
      },
      fontFamily: {
        display: ["'Fraunces'", "serif"],
        sans: ["'IBM Plex Sans'", "sans-serif"],
        mono: ["'IBM Plex Mono'", "monospace"],
      },
      backgroundImage: {
        grain: "radial-gradient(circle at 1px 1px, rgba(236,231,218,0.035) 1px, transparent 0)",
      },
      boxShadow: {
        card: "0 1px 0 0 rgba(236,231,218,0.06), 0 8px 24px -12px rgba(0,0,0,0.6)",
        seal: "0 0 0 3px rgba(201,162,78,0.15)",
      },
    },
  },
  plugins: [],
}

