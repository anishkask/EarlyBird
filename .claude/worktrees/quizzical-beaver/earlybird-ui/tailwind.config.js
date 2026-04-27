/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        navy: {
          DEFAULT: '#0F2940',
          light:   '#1a3d5c',
          lighter: '#234d72',
        },
        jay: {
          blue:  '#1D6FA4',
          sky:   '#4BA3D3',
          crest: '#0B4F78',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
