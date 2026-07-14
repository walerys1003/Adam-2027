/**
 * ADAM · Tailwind CSS Config
 * Zastąp tym plikiem swój tailwind.config.js
 * 
 * Wymaga: tailwindcss 3.4+
 * Fontsy: Fraunces + Geist (patrz DEVELOPER-HANDOFF.md)
 */

/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ['class'],
  content: [
    './index.html',
    './src/**/*.{ts,tsx,js,jsx}',
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
  ],
  theme: {
    container: {
      center: true,
      padding: '2rem',
      screens: {
        '2xl': '1400px',
      },
    },
    extend: {
      // ============ COLORS ============
      colors: {
        granat: {
          50:  '#f2f4f8',
          100: '#e4e8f0',
          200: '#c2cad9',
          300: '#8b98b3',
          400: '#5a6a8a',
          500: '#3b4a6b',
          600: '#243352',
          700: '#1a2744',   // ★ PRIMARY BRAND
          800: '#14213d',
          900: '#0e1a2e',
          950: '#08111f',
        },
        zloto: {
          50:  '#faf3e6',
          100: '#f5e6cf',
          200: '#ebd0ac',
          300: '#dfba82',
          400: '#d4a75d',
          500: '#c8963e',   // ★ PRIMARY ACCENT
          600: '#b88a35',
          700: '#a67c2e',
          800: '#8a6524',
          900: '#6b4d1a',
        },
        sem: {
          green:    '#2d6a4f',
          'green-bg': '#e8f2ec',
          yellow:   '#b8830d',
          'yellow-bg': '#fbf0d9',
          red:      '#a5121a',
          'red-bg': '#fbe7e9',
          purple:   '#5a0561',
          'purple-bg': '#f3e6f5',
        },
        info: {
          blue:    '#1e40af',
          'blue-bg': '#dbeafe',
        },
        paper: {
          DEFAULT: '#fbfaf7',
          2: '#f5f3ee',
          3: '#eeeadc',
        },
        ink: {
          900: '#0e1a2e',
          700: '#2a3654',
          500: '#5a6a8a',
          400: '#8b98b3',
          300: '#c2cad9',
        },
        line: {
          DEFAULT: '#e4e0d5',
          strong: '#cfc9b8',
        },
      },

      // ============ TYPOGRAPHY ============
      fontFamily: {
        serif: ['Fraunces', 'Iowan Old Style', 'Georgia', 'serif'],
        sans:  ['Geist', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
        mono:  ['Geist Mono', 'SF Mono', 'Menlo', 'monospace'],
      },
      fontSize: {
        'display': ['84px', { lineHeight: '0.95', letterSpacing: '-0.03em' }],
        'h1':      ['56px', { lineHeight: '1.02', letterSpacing: '-0.025em' }],
        'h2':      ['40px', { lineHeight: '1.1',  letterSpacing: '-0.02em' }],
        'h3':      ['28px', { lineHeight: '1.2',  letterSpacing: '-0.015em' }],
        'h4':      ['20px', { lineHeight: '1.3',  letterSpacing: '-0.01em' }],
        'body-l':  ['18px', { lineHeight: '1.55' }],
        'body':    ['15px', { lineHeight: '1.6' }],
        'label':   ['13px', { lineHeight: '1.5', letterSpacing: '0.02em' }],
        'caption': ['11px', { lineHeight: '1.4', letterSpacing: '0.06em' }],
      },
      letterSpacing: {
        'caps': '0.14em',   // For uppercase eyebrows
      },

      // ============ SPACING ============
      // (Tailwind default 0-96 wystarcza, poniżej alias)

      // ============ BORDER RADIUS ============
      borderRadius: {
        'sm':   '4px',
        'md':   '8px',
        'lg':   '12px',   // Adam card default
        'xl':   '16px',
        '2xl':  '24px',
      },

      // ============ SHADOW / ELEVATION ============
      boxShadow: {
        'e1':     '0 1px 2px rgba(14,26,46,0.04), 0 0 0 1px rgba(14,26,46,0.05)',
        'e2':     '0 2px 8px rgba(14,26,46,0.06), 0 0 0 1px rgba(14,26,46,0.05)',
        'e3':     '0 8px 24px rgba(14,26,46,0.08), 0 0 0 1px rgba(14,26,46,0.06)',
        'e4':     '0 20px 48px rgba(14,26,46,0.12), 0 0 0 1px rgba(14,26,46,0.08)',
        'gold':   '0 8px 24px rgba(200,150,62,0.15)',
        'red':    '0 8px 24px rgba(165,18,26,0.25)',
        'purple': '0 8px 24px rgba(90,5,97,0.3)',
        'focus':  '0 0 0 3px rgba(26,39,68,0.1)',
      },

      // ============ MOTION ============
      transitionTimingFunction: {
        'adam-out':    'cubic-bezier(0.22, 1, 0.36, 1)',
        'adam-in-out': 'cubic-bezier(0.65, 0, 0.35, 1)',
      },
      keyframes: {
        // Semafor pulse ring (only for RED/PURPLE)
        'sem-pulse-ring': {
          '0%':   { transform: 'scale(1)',   opacity: '0.7' },
          '100%': { transform: 'scale(1.6)', opacity: '0' },
        },
        // Semafor dot pulse
        'sem-dot-pulse': {
          '0%, 100%': { opacity: '1' },
          '50%':      { opacity: '0.4' },
        },
        // Fade in
        'fade-in': {
          '0%':   { opacity: '0', transform: 'translateY(4px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      animation: {
        'sem-pulse-ring': 'sem-pulse-ring 2s cubic-bezier(0.22, 1, 0.36, 1) infinite',
        'sem-dot-pulse':  'sem-dot-pulse 1.5s ease-in-out infinite',
        'fade-in':        'fade-in 0.2s ease-out',
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('tailwindcss-animate'),

    // Custom utility: text-italic-accent (dla „Adam signature")
    function ({ addUtilities }) {
      addUtilities({
        '.text-italic-accent': {
          fontStyle: 'italic',
          color: '#a67c2e', // zloto-700
          fontWeight: '400',
        },
        '.text-kpi': {
          fontFamily: 'Fraunces, serif',
          fontVariationSettings: "'opsz' 144",
          fontWeight: '500',
          letterSpacing: '-0.03em',
        },
      });
    },
  ],
};
