/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#1f2937',
        sand: '#f6efe5',
        ember: '#c2410c',
        tide: '#0f766e',
        cloud: '#fffaf3',
      },
      boxShadow: {
        card: '0 20px 50px rgba(15, 23, 42, 0.12)',
      },
      fontFamily: {
        display: ['"Trebuchet MS"', '"Segoe UI Variable"', 'sans-serif'],
        body: ['"Segoe UI Variable"', '"Tahoma"', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
