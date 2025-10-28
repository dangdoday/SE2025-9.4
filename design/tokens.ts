/**
 * Design Tokens for Crypto Trading Bot
 * Auto-generated from design-tokens.json
 * 
 * Usage:
 * import { colors, typography, spacing } from '@/styles/tokens';
 */

export const colors = {
  primary: {
    main: '#F0B90B',
    light: '#FCD535',
    dark: '#C79A00',
  },
  secondary: {
    main: '#1E2026',
    light: '#2B2F36',
    dark: '#0B0E11',
  },
  success: {
    main: '#0ECB81',
    light: '#3DD598',
    dark: '#0A9F6B',
  },
  danger: {
    main: '#F6465D',
    light: '#FF6838',
    dark: '#D93A4D',
  },
  background: {
    default: '#0B0E11',
    paper: '#1E2329',
    elevated: '#2B2F36',
  },
  text: {
    primary: '#EAECEF',
    secondary: '#848E9C',
    disabled: '#474D57',
  },
  divider: '#2B2F36',
  chart: {
    bullish: '#0ECB81',
    bearish: '#F6465D',
    grid: '#2B2F36',
  },
};

export const typography = {
  fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
  h1: {
    fontSize: '32px',
    fontWeight: 700,
    lineHeight: 1.2,
  },
  h2: {
    fontSize: '24px',
    fontWeight: 600,
    lineHeight: 1.3,
  },
  h3: {
    fontSize: '20px',
    fontWeight: 600,
    lineHeight: 1.4,
  },
  body1: {
    fontSize: '16px',
    fontWeight: 400,
    lineHeight: 1.5,
  },
  body2: {
    fontSize: '14px',
    fontWeight: 400,
    lineHeight: 1.5,
  },
  caption: {
    fontSize: '12px',
    fontWeight: 400,
    lineHeight: 1.4,
  },
};

export const spacing = {
  xs: '4px',
  sm: '8px',
  md: '16px',
  lg: '24px',
  xl: '32px',
  xxl: '48px',
};

export const borderRadius = {
  sm: '4px',
  md: '8px',
  lg: '12px',
  xl: '16px',
  full: '9999px',
};

export const shadows = {
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
};

export const breakpoints = {
  mobile: '320px',
  tablet: '768px',
  desktop: '1024px',
  wide: '1440px',
};

// Helper functions
export const rgba = (hex: string, alpha: number): string => {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
};

export const getColor = (path: string): string => {
  const keys = path.split('.');
  let value: any = colors;
  for (const key of keys) {
    value = value[key];
  }
  return value;
};

// CSS Variables export for global styles
export const cssVariables = `
  :root {
    /* Colors - Primary */
    --color-primary-main: ${colors.primary.main};
    --color-primary-light: ${colors.primary.light};
    --color-primary-dark: ${colors.primary.dark};
    
    /* Colors - Secondary */
    --color-secondary-main: ${colors.secondary.main};
    --color-secondary-light: ${colors.secondary.light};
    --color-secondary-dark: ${colors.secondary.dark};
    
    /* Colors - Success */
    --color-success-main: ${colors.success.main};
    --color-success-light: ${colors.success.light};
    --color-success-dark: ${colors.success.dark};
    
    /* Colors - Danger */
    --color-danger-main: ${colors.danger.main};
    --color-danger-light: ${colors.danger.light};
    --color-danger-dark: ${colors.danger.dark};
    
    /* Background */
    --bg-default: ${colors.background.default};
    --bg-paper: ${colors.background.paper};
    --bg-elevated: ${colors.background.elevated};
    
    /* Text */
    --text-primary: ${colors.text.primary};
    --text-secondary: ${colors.text.secondary};
    --text-disabled: ${colors.text.disabled};
    
    /* Spacing */
    --spacing-xs: ${spacing.xs};
    --spacing-sm: ${spacing.sm};
    --spacing-md: ${spacing.md};
    --spacing-lg: ${spacing.lg};
    --spacing-xl: ${spacing.xl};
    --spacing-xxl: ${spacing.xxl};
    
    /* Border Radius */
    --radius-sm: ${borderRadius.sm};
    --radius-md: ${borderRadius.md};
    --radius-lg: ${borderRadius.lg};
    --radius-xl: ${borderRadius.xl};
    
    /* Typography */
    --font-family: ${typography.fontFamily};
  }
`;

export default {
  colors,
  typography,
  spacing,
  borderRadius,
  shadows,
  breakpoints,
  rgba,
  getColor,
  cssVariables,
};
