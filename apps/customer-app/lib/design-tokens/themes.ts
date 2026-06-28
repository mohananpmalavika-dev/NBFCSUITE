import { colorPalette } from './colors';
import { radius } from './radius';
import { shadows } from './shadows';
import { spacing } from './spacing';
import { typography } from './typography';

export type ThemeName = 'default' | 'dark' | 'high-contrast';

export interface DesignTheme {
  name: string;
  background: {
    default: string;
    surface: string;
    elevated: string;
    header: string;
    sidebar: string;
    accent: string;
  };
  text: {
    primary: string;
    secondary: string;
    muted: string;
    inverse: string;
  };
  border: {
    default: string;
    light: string;
    focus: string;
  };
  accent: {
    primary: string;
    secondary: string;
    success: string;
    warning: string;
    danger: string;
  };
  radius: typeof radius;
  shadows: typeof shadows;
  spacing: typeof spacing;
  typography: typeof typography;
}

const baseTheme = {
  radius,
  shadows,
  spacing,
  typography,
};

export const themes: Record<ThemeName, DesignTheme> = {
  default: {
    name: 'Default',
    background: {
      default: '#f8fafc',
      surface: '#ffffff',
      elevated: '#f8fafc',
      header: 'rgba(255,255,255,0.95)',
      sidebar: '#0f172a',
      accent: '#eff6ff',
    },
    text: {
      primary: '#0f172a',
      secondary: '#475569',
      muted: '#64748b',
      inverse: '#ffffff',
    },
    border: {
      default: '#e2e8f0',
      light: '#f1f5f9',
      focus: colorPalette.primary[600],
    },
    accent: {
      primary: colorPalette.primary[600],
      secondary: colorPalette.cyan[500],
      success: colorPalette.green[600],
      warning: colorPalette.amber[600],
      danger: colorPalette.red[600],
    },
    ...baseTheme,
  },
  dark: {
    name: 'Dark',
    background: {
      default: '#020617',
      surface: '#0f172a',
      elevated: '#111827',
      header: 'rgba(2, 6, 23, 0.95)',
      sidebar: '#020617',
      accent: '#172554',
    },
    text: {
      primary: '#f8fafc',
      secondary: '#cbd5e1',
      muted: '#94a3b8',
      inverse: '#020617',
    },
    border: {
      default: '#334155',
      light: '#1e293b',
      focus: colorPalette.cyan[400],
    },
    accent: {
      primary: colorPalette.primary[400],
      secondary: colorPalette.cyan[400],
      success: colorPalette.green[400],
      warning: colorPalette.amber[400],
      danger: colorPalette.red[400],
    },
    ...baseTheme,
  },
  'high-contrast': {
    name: 'High Contrast',
    background: {
      default: '#000000',
      surface: '#111111',
      elevated: '#1a1a1a',
      header: '#000000',
      sidebar: '#000000',
      accent: '#111111',
    },
    text: {
      primary: '#ffffff',
      secondary: '#f1f5f9',
      muted: '#d1d5db',
      inverse: '#000000',
    },
    border: {
      default: '#ffffff',
      light: '#d1d5db',
      focus: '#fbbf24',
    },
    accent: {
      primary: '#fbbf24',
      secondary: '#38bdf8',
      success: '#4ade80',
      warning: '#fde68a',
      danger: '#f87171',
    },
    ...baseTheme,
  },
};

export function buildCssVariables(theme: DesignTheme) {
  return {
    '--background-default': theme.background.default,
    '--background-surface': theme.background.surface,
    '--background-elevated': theme.background.elevated,
    '--background-header': theme.background.header,
    '--background-sidebar': theme.background.sidebar,
    '--background-accent': theme.background.accent,
    '--text-primary': theme.text.primary,
    '--text-secondary': theme.text.secondary,
    '--text-muted': theme.text.muted,
    '--text-inverse': theme.text.inverse,
    '--border-default': theme.border.default,
    '--border-light': theme.border.light,
    '--border-focus': theme.border.focus,
    '--accent-primary': theme.accent.primary,
    '--accent-secondary': theme.accent.secondary,
    '--accent-success': theme.accent.success,
    '--accent-warning': theme.accent.warning,
    '--accent-danger': theme.accent.danger,
    '--radius-sm': theme.radius.sm,
    '--radius-md': theme.radius.md,
    '--radius-lg': theme.radius.lg,
    '--radius-xl': theme.radius.xl,
    '--shadow-sm': theme.shadows.sm,
    '--shadow-md': theme.shadows.md,
    '--shadow-lg': theme.shadows.lg,
    '--font-body': theme.typography.font.body,
  } as React.CSSProperties;
}
