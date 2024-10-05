/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './*.html',         // Include all HTML files in the root of the frontend folder
    './css/**/*.css',   // Include all CSS files in the css folder and any subdirectories
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}

