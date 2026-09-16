/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        tactical: {
          green: '#00ff41',
          red: '#ff2a2a',
          dark: '#030712',
          panel: 'rgba(15, 23, 42, 0.75)',
        }
      },
      fontFamily: {
        mono: ['"Share Tech Mono"', 'monospace'],
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}