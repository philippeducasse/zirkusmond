/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    '../../templates/**/*.{html,js}',
    './qr-scanner/**/*.vue',
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

