/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'ge-blue': '#005EB8',
        'clinical-bg': '#F3F4F6',
      }
    },
  },
  plugins: [],
}