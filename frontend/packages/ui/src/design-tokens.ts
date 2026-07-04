/**
 * NBFC Design Language (NDL) - Design Tokens
 * Banking-grade professional design system
 * Version: 3.0
 */

export const designTokens = {
  // ============================================
  // COLORS - Banking-grade Professional Theme
  // ============================================
  
  colors: {
    // Primary - Trust & Professionalism
    primary: {
      50: '#E3F2FD',
      100: '#BBDEFB',
      200: '#90CAF9',
      300: '#64B5F6',
      400: '#42A5F5',
      500: '#2196F3',  // Main brand color
      600: '#1E88E5',
      700: '#1976D2',
      800: '#1565C0',
      900: '#0D47A1',
    },
    
    // Success - Financial Growth
    success: {
      50: '#E8F5E9',
      100: '#C8E6C9',
      200: '#A5D6A7',
      300: '#81C784',
      400: '#66BB6A',
      500: '#4CAF50',  // Main success color
      600: '#43A047',
      700: '#388E3C',
      800: '#2E7D32',
      900: '#1B5E20',
    },
    
    // Warning - Attention Required
    warning: {
      50: '#FFF3E0',
      100: '#FFE0B2',
      200: '#FFCC80',
      300: '#FFB74D',
      400: '#FFA726',
      500: '#FF9800',  // Main warning color
      600: '#FB8C00',
      700: '#F57C00',
      800: '#EF6C00',
      900: '#E65100',
    },
    
    // Error - Critical Issues
    error: {
      50: '#FFEBEE',
      100: '#FFCDD2',
      200: '#EF9A9A',
      300: '#E57373',
      400: '#EF5350',
      500: '#F44336',  // Main error color
      600: '#E53935',
      700: '#D32F2F',
      800: '#C62828',
      900: '#B71C1C',
    },
    
    // Info - Information
    info: {
      50: '#E1F5FE',
      100: '#B3E5FC',
      200: '#81D4FA',
      300: '#4FC3F7',
      400: '#29B6F6',
      500: '#03A9F4',
      600: '#039BE5',
      700: '#0288D1',
      800: '#0277BD',
      900: '#01579B',
    },
    
    // Neutral - Content & UI Elements
    gray: {
      50: '#FAFAFA',
      100: '#F5F5F5',
      200: '#EEEEEE',
      300: '#E0E0E0',
      400: '#BDBDBD',
      500: '#9E9E9E',
      600: '#757575',
      700: '#616161',
      800: '#424242',
      900: '#212121',
    },
    
    // Text Colors
    text: {
      primary: '#212121',      // Headings, important text
      secondary: '#616161',    // Body text
      tertiary: '#9E9E9E',     // Help text, captions
      disabled: '#BDBDBD',     // Disabled state
      inverse: '#FFFFFF',      // Text on dark backgrounds
    },
    
    // Background Colors
    background: {
      default: '#FFFFFF',
      paper: '#FAFAFA',
      elevated: '#FFFFFF',
      dark: '#1E293B',
      darker: '#0F172A',
    },
    
    // Border Colors
    border: {
      light: '#F5F5F5',
      default: '#E0E0E0',
      dark: '#BDBDBD',
      focus: '#2196F3',
    },
    
    // Semantic Colors
    semantic: {
      approved: '#4CAF50',
      pending: '#FF9800',
      rejected: '#F44336',
      overdue: '#D32F2F',
      npa: '#B71C1C',
      active: '#4CAF50',
      inactive: '#9E9E9E',
      verified: '#03A9F4',
    },
  },
  
  // ============================================
  // TYPOGRAPHY
  // ============================================
  
  typography: {
    // Font Families
    fontFamily: {
      primary: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      headings: "'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      monospace: "'JetBrains Mono', 'Courier New', monospace",
      malayalam: "'Manjari', 'Noto Sans Malayalam', sans-serif",
      hindi: "'Noto Sans Devanagari', sans-serif",
    },
    
    // Font Sizes
    fontSize: {
      xs: '0.75rem',     // 12px
      sm: '0.875rem',    // 14px
      base: '1rem',      // 16px
      lg: '1.125rem',    // 18px
      xl: '1.25rem',     // 20px
      '2xl': '1.5rem',   // 24px
      '3xl': '1.875rem', // 30px
      '4xl': '2.25rem',  // 36px
      '5xl': '3rem',     // 48px
      '6xl': '3.75rem',  // 60px
      '7xl': '4.5rem',   // 72px
    },
    
    // Font Weights
    fontWeight: {
      light: 300,
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
      extrabold: 800,
    },
    
    // Line Heights
    lineHeight: {
      none: 1,
      tight: 1.25,
      snug: 1.375,
      normal: 1.5,
      relaxed: 1.625,
      loose: 2,
    },
    
    // Letter Spacing
    letterSpacing: {
      tighter: '-0.05em',
      tight: '-0.025em',
      normal: '0',
      wide: '0.025em',
      wider: '0.05em',
      widest: '0.1em',
    },
  },
  
  // ============================================
  // SPACING
  // ============================================
  
  spacing: {
    0: '0',
    1: '0.25rem',   // 4px
    2: '0.5rem',    // 8px
    3: '0.75rem',   // 12px
    4: '1rem',      // 16px
    5: '1.25rem',   // 20px
    6: '1.5rem',    // 24px
    7: '1.75rem',   // 28px
    8: '2rem',      // 32px
    10: '2.5rem',   // 40px
    12: '3rem',     // 48px
    14: '3.5rem',   // 56px
    16: '4rem',     // 64px
    20: '5rem',     // 80px
    24: '6rem',     // 96px
    32: '8rem',     // 128px
    40: '10rem',    // 160px
    48: '12rem',    // 192px
    56: '14rem',    // 224px
    64: '16rem',    // 256px
  },
  
  // ============================================
  // SIZING
  // ============================================
  
  sizing: {
    // Component Heights
    input: {
      sm: '2rem',      // 32px
      md: '2.5rem',    // 40px
      lg: '3rem',      // 48px
      xl: '3.5rem',    // 56px
    },
    
    button: {
      sm: '2rem',      // 32px
      md: '2.5rem',    // 40px
      lg: '3rem',      // 48px
      xl: '3.5rem',    // 56px
    },
    
    // Touch Targets (Mobile)
    touchTarget: '2.75rem', // 44px - iOS/Android minimum
    
    // Icon Sizes
    icon: {
      xs: '1rem',      // 16px
      sm: '1.25rem',   // 20px
      md: '1.5rem',    // 24px
      lg: '2rem',      // 32px
      xl: '2.5rem',    // 40px
      '2xl': '3rem',   // 48px
    },
  },
  
  // ============================================
  // BORDERS
  // ============================================
  
  borders: {
    // Border Widths
    width: {
      0: '0',
      1: '1px',
      2: '2px',
      4: '4px',
      8: '8px',
    },
    
    // Border Radius
    radius: {
      none: '0',
      sm: '0.25rem',   // 4px
      md: '0.5rem',    // 8px
      lg: '0.75rem',   // 12px
      xl: '1rem',      // 16px
      '2xl': '1.5rem', // 24px
      full: '9999px',
    },
  },
  
  // ============================================
  // SHADOWS
  // ============================================
  
  shadows: {
    none: 'none',
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
    // Elevation shadows (Material Design inspired)
    elevation1: '0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)',
    elevation2: '0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23)',
    elevation3: '0 10px 20px rgba(0,0,0,0.19), 0 6px 6px rgba(0,0,0,0.23)',
    elevation4: '0 14px 28px rgba(0,0,0,0.25), 0 10px 10px rgba(0,0,0,0.22)',
    elevation5: '0 19px 38px rgba(0,0,0,0.30), 0 15px 12px rgba(0,0,0,0.22)',
  },
  
  // ============================================
  // TRANSITIONS
  // ============================================
  
  transitions: {
    duration: {
      fast: '150ms',
      normal: '200ms',
      slow: '300ms',
      slower: '500ms',
    },
    
    easing: {
      linear: 'linear',
      easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
      easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
      easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    },
  },
  
  // ============================================
  // BREAKPOINTS (Mobile-first)
  // ============================================
  
  breakpoints: {
    mobile: '320px',      // Small phones
    mobileLg: '480px',    // Large phones
    tablet: '768px',      // Tablets
    desktop: '1024px',    // Small desktops
    desktopLg: '1280px',  // Large desktops
    desktopXl: '1536px',  // Extra large screens
    desktop2xl: '1920px', // Full HD
  },
  
  // ============================================
  // Z-INDEX LAYERS
  // ============================================
  
  zIndex: {
    base: 0,
    dropdown: 1000,
    sticky: 1020,
    fixed: 1030,
    overlay: 1040,
    modal: 1050,
    popover: 1060,
    toast: 1070,
    tooltip: 1080,
  },
};

// Export individual token groups for convenience
export const colors = designTokens.colors;
export const typography = designTokens.typography;
export const spacing = designTokens.spacing;
export const sizing = designTokens.sizing;
export const borders = designTokens.borders;
export const shadows = designTokens.shadows;
export const transitions = designTokens.transitions;
export const breakpoints = designTokens.breakpoints;
export const zIndex = designTokens.zIndex;

// Type definitions for TypeScript
export type Color = keyof typeof colors;
export type Spacing = keyof typeof spacing;
export type FontSize = keyof typeof typography.fontSize;
export type FontWeight = keyof typeof typography.fontWeight;
export type BorderRadius = keyof typeof borders.radius;
export type Shadow = keyof typeof shadows;
export type Breakpoint = keyof typeof breakpoints;

export default designTokens;
