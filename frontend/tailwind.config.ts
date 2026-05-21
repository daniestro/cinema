import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: {
          base: '#0b0d12',
          elev: '#12151c',
        },
        fg: {
          primary: '#f2f3f5',
          muted: '#9aa0a6',
        },
        accent: {
          DEFAULT: '#ff6a2c',
          hover: '#ff8651',
          fg: '#1a0d05',
        },
      },
      fontFamily: {
        sans: [
          'system-ui',
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'Roboto',
          'Helvetica Neue',
          'Arial',
          'sans-serif',
        ],
      },
      fontSize: {
        hero: ['72px', { lineHeight: '1.05', letterSpacing: '-0.02em', fontWeight: '800' }],
      },
      spacing: {
        section: '96px',
      },
    },
  },
  plugins: [],
};

export default config;
