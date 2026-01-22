import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'alula': {
          'dark': '#0D1D25',
          'teal': '#104C64',
          'gray': '#C6C6D0',
          'peach': '#D59D80',
          'terra': '#C0754D',
          'rust': '#B6410F',
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
export default config
