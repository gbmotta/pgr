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
        // Cores customizadas do projeto
        institutional: {
          dark: '#1a1a2e',
          primary: '#2c3e50',
          'primary-light': '#34495e',
          accent: '#c0392b',
          'accent-secondary': '#d68910',
        },
        status: {
          pendente: '#ff9800',
          'em-analise': '#2196f3',
          deferido: '#4caf50',
          indeferido: '#f44336',
          vencido: '#d32f2f',
          vencendo: '#ff6f00',
          ok: '#388e3c',
        },
        neutral: {
          'bg-primary': '#ffffff',
          'bg-secondary': '#fafafa',
          'bg-tertiary': '#f5f5f5',
          border: '#e0e0e0',
          'border-light': '#f0f0f0',
          'text-primary': '#212121',
          'text-secondary': '#616161',
          'text-tertiary': '#9e9e9e',
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

