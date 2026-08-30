/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Base surfaces — command-center dark, layered for depth without pure black
        base: {
          950: '#0A0F1C', // deepest — page background
          900: '#0F172A', // primary surface (spec baseline)
          800: '#141E33', // panel surface
          700: '#1C2A45', // raised card / hover
          600: '#28395A', // borders, dividers
          500: '#3D5075', // muted borders / disabled
        },
        ink: {
          100: '#EAF0FB', // primary text
          300: '#B9C6DE', // secondary text
          500: '#7E8FAE', // tertiary / labels
          700: '#526080', // placeholder / disabled text
        },
        // Threat-tier semantic accents
        threat: {
          kingpin: '#EF4444',   // crimson red
          broker: '#F59E0B',    // amber
          operative: '#06B6D4', // cyan
          inactive: '#64748B',  // muted gray
        },
        signal: {
          DEFAULT: '#3DD9C2', // teal — system-active / live-data accent (the one accent color)
          dim: '#1F8A79',
        },
      },
      fontFamily: {
        display: ['"IBM Plex Sans Condensed"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        body: ['"Inter"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
      boxShadow: {
        panel: '0 0 0 1px rgba(61, 217, 194, 0.06), 0 8px 24px -8px rgba(0,0,0,0.6)',
        glow: '0 0 12px rgba(61, 217, 194, 0.35)',
      },
      animation: {
        'pulse-slow': 'pulse 2.4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        sweep: 'sweep 3.5s linear infinite',
      },
      keyframes: {
        sweep: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' },
        },
      },
    },
  },
  plugins: [],
};
