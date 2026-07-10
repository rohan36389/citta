/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: ["./src/**/*.{js,jsx,ts,tsx}", "./public/index.html"],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Geist Sans"', 'Inter', "system-ui", "sans-serif"],
        sans: ['Inter', "system-ui", "sans-serif"],
        mono: ['"JetBrains Mono"', "ui-monospace", "monospace"],
      },
      colors: {
        // Base / Neutral (Living Intelligence tokens from Section 3.1)
        bg: {
          dark:   "#0A0F1E",
          dark2:  "#0F172A",
          light:  "#F8FAFC",
          cardLight: "#FFFFFF",
        },
        ink: { // legacy alias
          950: "#0A0F1E",
          900: "#0F172A",
          800: "#1E293B",
        },
        text: {
          primaryDark: "#0F172A",
          primaryLight: "#F1F5F9",
          muted: "#64748B",
        },
        // Brand
        brand: {
          blue:  "#2563EB",
          light: "#60A5FA",
        },
        // Border subtle
        border: 'hsl(var(--border))',
      },
      keyframes: {
        'accordion-down': { from: { height: '0' }, to: { height: 'var(--radix-accordion-content-height)' } },
        'accordion-up':   { from: { height: 'var(--radix-accordion-content-height)' }, to: { height: '0' } },
        'marquee':        { '0%': { transform: 'translateX(0)' }, '100%': { transform: 'translateX(-50%)' } },
        'float-slow':     { '0%,100%': { transform: 'translateY(0px)' }, '50%': { transform: 'translateY(-10px)' } },
        'pulse-ring':     { '0%':   { boxShadow: '0 0 0 0 rgba(37,99,235,0.4)' },
                            '70%':  { boxShadow: '0 0 0 14px rgba(37,99,235,0)' },
                            '100%': { boxShadow: '0 0 0 0 rgba(37,99,235,0)' } },
        'gradient-drift': {
          '0%,100%': { backgroundPosition: '0% 50%' },
          '50%':     { backgroundPosition: '100% 50%' },
        },
      },
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up':   'accordion-up 0.2s ease-out',
        'marquee':        'marquee 42s linear infinite',
        'float-slow':     'float-slow 7s ease-in-out infinite',
        'pulse-ring':     'pulse-ring 2.6s cubic-bezier(0.4,0,0.6,1) infinite',
        'gradient-drift': 'gradient-drift 10s ease infinite',
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};
