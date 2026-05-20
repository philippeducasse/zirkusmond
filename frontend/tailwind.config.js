/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    '../zirkusmond_de/templates/**/*.{html,js}',
    '../zirkusmond_de/events/templates/**/*.{html,js}',
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

