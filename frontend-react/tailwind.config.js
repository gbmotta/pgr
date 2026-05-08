/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        /** Paleta PGR — 60-30-10 + código jurídico */
        pgr: {
          ice: '#F4F7F6',
          surface: '#FFFFFF',
          navy: '#1B365D',
          'navy-deep': '#142946',
          'navy-muted': '#152a42',
          border: '#E0E0E0',
          text: '#2C3E50',
          muted: '#7F8C8D',
          success: '#27AE60',
          warning: '#E67E22',
          error: '#C0392B',
          info: '#2980B9',
          highlight: '#F1C40F',
          'dark-bg': '#121212',
          'dark-surface': '#1E1E1E',
          'dark-text': '#E0E0E0',
        },
        institutional: {
          dark: '#1B365D',
          primary: '#2C3E50',
          'primary-light': '#34495e',
          accent: '#C0392B',
          'accent-secondary': '#E67E22',
        },
        status: {
          pendente: '#E67E22',
          'em-analise': '#2980B9',
          deferido: '#27AE60',
          indeferido: '#C0392B',
          vencido: '#C0392B',
          vencendo: '#E67E22',
          ok: '#27AE60',
        },
        neutral: {
          'bg-primary': '#FFFFFF',
          'bg-secondary': '#F4F7F6',
          'bg-tertiary': '#edf1ef',
          border: '#E0E0E0',
          'border-light': '#ececec',
          'text-primary': '#2C3E50',
          'text-secondary': '#7F8C8D',
          'text-tertiary': '#95a5a6',
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      spacing: {
        'xs': '4px',
        'sm': '8px',
        'md': '16px',
        'lg': '24px',
        'xl': '32px',
        '2xl': '48px',
      },
      fontFamily: {
        sans: ['Roboto', 'Segoe UI', '-apple-system', 'sans-serif'],
        mono: ['Courier New', 'monospace'],
        serif: ['Playfair Display', 'serif'],
      },
      fontSize: {
        'h1': '28px',
        'h2': '22px',
        'h3': '18px',
        'h4': '16px',
        'body': '14px',
        'body-small': '13px',
        'caption': '12px',
      },
      lineHeight: {
        'tight': '1.3',
        'normal': '1.5',
        'relaxed': '1.7',
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}

