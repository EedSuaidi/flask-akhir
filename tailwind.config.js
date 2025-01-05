/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/templates/**/*.html", "./app/static/src/**/*.js"],
  theme: {
    extend: {
      fontFamily: {
        montserrat: ["Montserrat", "sans-serif"],
      },
      backgroundImage: {
        herringbone: "url('/static/img/herringbone.webp')",
      },
    },
  },
  plugins: [],
};
