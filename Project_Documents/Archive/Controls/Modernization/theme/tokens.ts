/**
 * Design system tokens for the UI component library
 */

export const baseColors = {
  // Primary colors
  primary: {
    50: '#E6F6FF',
    100: '#BAE3FF',
    200: '#7CC4FA',
    300: '#47A3F3',
    400: '#2186EB',
    500: '#0967D2', // Primary brand color
    600: '#0552B5',
    700: '#03449E',
    800: '#01337D',
    900: '#002159'
  },

  // Neutral colors
  neutral: {
    50: '#F5F7FA',
    100: '#E4E7EB',
    200: '#CBD2D9',
    300: '#9AA5B1',
    400: '#7B8794',
    500: '#616E7C',
    600: '#52606D',
    700: '#3E4C59',
    800: '#323F4B',
    900: '#1F2933'
  },

  // Success colors
  success: {
    50: '#E3F9E5',
    100: '#C1F2C7',
    200: '#91E697',
    300: '#51CA58',
    400: '#31B237',
    500: '#18981D',
    600: '#0F8613',
    700: '#0A6F0A',
    800: '#065A06',
    900: '#034203'
  },

  // Warning colors
  warning: {
    50: '#FFFBEA',
    100: '#FFF3C4',
    200: '#FCE588',
    300: '#FADB5F',
    400: '#F7C948',
    500: '#F0B429',
    600: '#DE911D',
    700: '#CB6E17',
    800: '#B44D12',
    900: '#8D2B0B'
  },

  // Error colors
  error: {
    50: '#FFE3E3',
    100: '#FFBDBD',
    200: '#FF9B9B',
    300: '#F86A6A',
    400: '#EF4E4E',
    500: '#E12D39',
    600: '#CF1124',
    700: '#AB091E',
    800: '#8A041A',
    900: '#610316'
  },

  // Core colors
  white: '#FFFFFF',
  black: '#000000',
  transparent: 'transparent'
}

export const spacing = {
  none: '0',
  xs: '0.25rem',    // 4px
  sm: '0.5rem',     // 8px
  md: '1rem',       // 16px
  lg: '1.5rem',     // 24px
  xl: '2rem',       // 32px
  '2xl': '2.5rem',  // 40px
  '3xl': '3rem',    // 48px
  '4xl': '4rem'     // 64px
}

export const fontSizes = {
  xs: '0.75rem',    // 12px
  sm: '0.875rem',   // 14px
  md: '1rem',       // 16px
  lg: '1.125rem',   // 18px
  xl: '1.25rem',    // 20px
  '2xl': '1.5rem',  // 24px
  '3xl': '1.875rem',// 30px
  '4xl': '2.25rem', // 36px
  '5xl': '3rem'     // 48px
}

export const fontWeights = {
  thin: 100,
  extralight: 200,
  light: 300,
  normal: 400,
  medium: 500,
  semibold: 600,
  bold: 700,
  extrabold: 800,
  black: 900
}

export const lineHeights = {
  none: 1,
  tight: 1.25,
  snug: 1.375,
  normal: 1.5,
  relaxed: 1.625,
  loose: 2
}

export const radii = {
  none: '0',
  sm: '0.125rem',   // 2px
  md: '0.25rem',    // 4px
  lg: '0.5rem',     // 8px
  xl: '0.75rem',    // 12px
  '2xl': '1rem',    // 16px
  full: '9999px'
}

export const shadows = {
  none: 'none',
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
  inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)'
}

export const transitions = {
  default: 'all 0.2s ease-in-out',
  fast: 'all 0.1s ease-in-out',
  slow: 'all 0.3s ease-in-out'
}

export const zIndices = {
  hide: -1,
  auto: 'auto',
  base: 0,
  docked: 10,
  dropdown: 1000,
  sticky: 1100,
  banner: 1200,
  overlay: 1300,
  modal: 1400,
  popover: 1500,
  skipLink: 1600,
  toast: 1700,
  tooltip: 1800
}
