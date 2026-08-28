/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        paper: "#F5F2E6",
        panel: "#FFFFFF",
        line: "#E1DCC8",
        ink: "#1F2333",
        "ink-muted": "#4A5068",
        "ink-faint": "#8891A5",
        ledger: "#454d4a",
        "ledger-dark": "#141616",
        "ledger-light": "#E8F5EE",
        "stamp-red": "#A6321C",
        "stamp-amber": "#B8843A",
        "stamp-red-light": "#FDECEA",
        "stamp-amber-light": "#FEF5E7",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        display: ["'Zilla Slab'", "serif"],
        mono: ["'IBM Plex Mono'", "monospace"],
      },
      borderRadius: {
        sm: "0.125rem",
      },
    },
  },
  plugins: [],
};
