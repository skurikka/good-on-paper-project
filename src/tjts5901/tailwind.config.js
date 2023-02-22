/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./templates/base.html",
    "./static/**/*.js"
  ],
  theme: {
    fontSize: {
      sm: '12px',
      base: '14px',
      lg: '16px',
      xl: '20px',
      '2xl': '24px',
      '3xl': '32px',
      '4xl': '36px',
      '5xl': '40px',
    },
    colors: {
      'primary' : {
        100 : '#F0F7F4',
        500 : '#50727C',
        700 : '#16271F',
      },
      'red' : '#D1462F',
      'white' : '#fff',
      'black' : '#000',
      'gray' : '#d3d3d3',
      'dark-gray' : '#a9a9a9'
    },
    screens: {
      'sm': '640px',
      'md': '1024px',
    },
    extend: {},
  },
  plugins: [],
}
