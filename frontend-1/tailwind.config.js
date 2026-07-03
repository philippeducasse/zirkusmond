/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    '../backend/templates/**/*.{html,js}',
    '../backend/events/templates/**/*.{html,js}',
    './src/components/**/*.vue',
  ],
  theme: {
    extend: {
      colors: {
        'zm-yellow': '#f6ae42',
      },
    },
  },
  plugins: [],
}

