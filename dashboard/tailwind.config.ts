import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#2563EB',
        'primary-dark': '#1D4ED8',
        'primary-light': '#3B82F6',
        sidebar: '#0F172A',
        'sidebar-hover': '#1E293B',
        success: '#10B981',
        'success-dark': '#059669',
        danger: '#EF4444',
        'danger-dark': '#DC2626',
        warning: '#F59E0B',
        'warning-dark': '#D97706',
        info: '#06B6D4',
        'info-dark': '#0891B2',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      spacing: {
        sidebar: '16rem',
      },
      animation: {
        'spin-slow': 'spin 2s linear infinite',
        'pulse-subtle': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
    },
  },
  plugins: [],
};

export default config;
