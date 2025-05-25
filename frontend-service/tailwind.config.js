// tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html",
  ],
  theme: {
    extend: {
      colors: {
        // Clear Stocks Theme
        primary: '#2563EB',        // Electric Blue
        secondary: '#8000FF',      // Purple Glow
        success: '#10B981',        // Neon Green
        danger: '#EF4444',         // Coral Red
        dark: {
          bg: '#04060e',          // Deep Black
          card: '#13151e',        // Dark Gray
          border: '#2A2A2A',      // Charcoal
        },
        text: {
          primary: '#FFFFFF',      // Pure White
          secondary: '#B0B0B0',    // Light Gray
        }
      },
      boxShadow: {
        'blue-glow': '0 0 20px rgba(37, 99, 235, 0.3)',
        'purple-glow': '0 0 20prgba(11, 12, 14, 0.3)3)',
        'green-glow': '0 0 15px rgba(16, 185, 129, 0.3)',
      }
    }
  },
  plugins: [],
}
