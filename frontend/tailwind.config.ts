import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#f6f8f4",
          100: "#e8efe2",
          200: "#d0e0c3",
          300: "#aac58f",
          400: "#7fa45a",
          500: "#5f873e",
          600: "#4a6a30",
          700: "#375024",
          800: "#26361a",
          900: "#171f10"
        },
        accent: {
          sand: "#d8c6a5",
          ink: "#1f2a31",
          sky: "#b8d6de"
        }
      },
      fontFamily: {
        display: ["Space Grotesk", "sans-serif"],
        body: ["Manrope", "sans-serif"]
      }
    }
  },
  plugins: []
};

export default config;
