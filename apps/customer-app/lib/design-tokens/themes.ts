import { breakpoints } from './breakpoints';
import { colorPalette } from './colors';
import { motion } from './motion';
import { radius } from './radius';
import { shadows } from './shadows';
import { sizes } from './sizes';
import { spacing } from './spacing';
import { typography } from './typography';
import { zIndex } from './zIndex';

export type ThemeName = 'default' | 'dark' | 'high-contrast';

export interface DesignTheme {
  name: string;
  background: {
    default: string;
    surface: string;
    elevated: string;
    header: string;
    sidebar: string;
    sidebarSubtle: string;
    accent: string;
  };
  text: {
    primary: string;
    secondary: string;
    muted: string;
    inverse: string;
    inverseMuted: string;
  };
  border: {
    default: string;
    light: string;
    focus: string;
  };
  accent: {
    primary: string;
    onPrimary: string;
    secondary: string;
    success: string;
    warning: string;
    danger: string;
  };
  radius: typeof radius;
  shadows: typeof shadows;
  spacing: typeof spacing;
  typography: typeof typography;
  motion: typeof motion;
  sizes: typeof sizes;
  zIndex: typeof zIndex;
  breakpoints: typeof breakpoints;
}

const baseTheme = {
  breakpoints,
  motion,
  radius,
  shadows,
  sizes,
  spacing,
  typography,
  zIndex,
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
      sidebarSubtle: 'rgba(255,255,255,0.08)',
      accent: '#eff6ff',
    },
    text: {
      primary: '#0f172a',
      secondary: '#475569',
      muted: '#64748b',
      inverse: '#ffffff',
      inverseMuted: 'rgba(255,255,255,0.72)',
    },
    border: {
      default: '#e2e8f0',
      light: '#f1f5f9',
      focus: colorPalette.primary[600],
    },
    accent: {
      primary: colorPalette.primary[600],
      onPrimary: '#ffffff',
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
      sidebarSubtle: 'rgba(255,255,255,0.1)',
      accent: '#172554',
    },
    text: {
      primary: '#f8fafc',
      secondary: '#cbd5e1',
      muted: '#94a3b8',
      inverse: '#f8fafc',
      inverseMuted: 'rgba(248,250,252,0.74)',
    },
    border: {
      default: '#334155',
      light: '#1e293b',
      focus: colorPalette.cyan[400],
    },
    accent: {
      primary: colorPalette.primary[400],
      onPrimary: '#020617',
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
      sidebarSubtle: '#1a1a1a',
      accent: '#111111',
    },
    text: {
      primary: '#ffffff',
      secondary: '#f1f5f9',
      muted: '#d1d5db',
      inverse: '#ffffff',
      inverseMuted: '#f1f5f9',
    },
    border: {
      default: '#ffffff',
      light: '#d1d5db',
      focus: colorPalette.amber[400],
    },
    accent: {
      primary: colorPalette.amber[400],
      onPrimary: '#000000',
      secondary: colorPalette.sky[400],
      success: colorPalette.green[400],
      warning: colorPalette.amber[200],
      danger: colorPalette.red[400],
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
    '--background-sidebar-subtle': theme.background.sidebarSubtle,
    '--background-accent': theme.background.accent,
    '--text-primary': theme.text.primary,
    '--text-secondary': theme.text.secondary,
    '--text-muted': theme.text.muted,
    '--text-inverse': theme.text.inverse,
    '--text-inverse-muted': theme.text.inverseMuted,
    '--border-default': theme.border.default,
    '--border-light': theme.border.light,
    '--border-focus': theme.border.focus,
    '--accent-primary': theme.accent.primary,
    '--accent-on-primary': theme.accent.onPrimary,
    '--accent-secondary': theme.accent.secondary,
    '--accent-success': theme.accent.success,
    '--accent-warning': theme.accent.warning,
    '--accent-danger': theme.accent.danger,
    '--space-0': theme.spacing[0],
    '--space-2': theme.spacing[2],
    '--space-4': theme.spacing[4],
    '--space-8': theme.spacing[8],
    '--space-12': theme.spacing[12],
    '--space-16': theme.spacing[16],
    '--space-24': theme.spacing[24],
    '--space-32': theme.spacing[32],
    '--space-40': theme.spacing[40],
    '--space-48': theme.spacing[48],
    '--space-64': theme.spacing[64],
    '--space-80': theme.spacing[80],
    '--space-96': theme.spacing[96],
    '--radius-sm': theme.radius.sm,
    '--radius-md': theme.radius.md,
    '--radius-lg': theme.radius.lg,
    '--radius-xl': theme.radius.xl,
    '--radius-2xl': theme.radius['2xl'],
    '--radius-pill': theme.radius.pill,
    '--shadow-xs': theme.shadows.xs,
    '--shadow-sm': theme.shadows.sm,
    '--shadow-md': theme.shadows.md,
    '--shadow-lg': theme.shadows.lg,
    '--shadow-xl': theme.shadows.xl,
    '--motion-fast': theme.motion.duration.fast,
    '--motion-normal': theme.motion.duration.normal,
    '--motion-slow': theme.motion.duration.slow,
    '--motion-standard': theme.motion.easing.standard,
    '--shell-header-height': theme.sizes.headerHeight,
    '--shell-sidebar-expanded': theme.sizes.sidebarExpanded,
    '--shell-sidebar-collapsed': theme.sizes.sidebarCollapsed,
    '--shell-right-drawer': theme.sizes.rightDrawer,
    '--shell-mobile-nav-height': theme.sizes.mobileNavHeight,
    '--z-header': theme.zIndex.header,
    '--z-sidebar': theme.zIndex.sidebar,
    '--z-drawer': theme.zIndex.drawer,
    '--z-modal': theme.zIndex.modal,
    '--z-ai-panel': theme.zIndex.aiPanel,
    '--font-body': theme.typography.font.body,
  } as React.CSSProperties;
}
