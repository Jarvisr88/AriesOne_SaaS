/**
 * Theme configuration and utilities
 */
import { baseColors, spacing, fontSizes, fontWeights, lineHeights, radii, shadows, transitions, zIndices } from './tokens'

export interface Theme {
  colors: typeof baseColors
  spacing: typeof spacing
  fontSizes: typeof fontSizes
  fontWeights: typeof fontWeights
  lineHeights: typeof lineHeights
  radii: typeof radii
  shadows: typeof shadows
  transitions: typeof transitions
  zIndices: typeof zIndices
}

export const lightTheme: Theme = {
  colors: {
    ...baseColors,
    // Add light theme specific overrides here
    background: {
      primary: baseColors.white,
      secondary: baseColors.neutral[50],
      tertiary: baseColors.neutral[100]
    },
    text: {
      primary: baseColors.neutral[900],
      secondary: baseColors.neutral[700],
      tertiary: baseColors.neutral[500],
      disabled: baseColors.neutral[300]
    }
  },
  spacing,
  fontSizes,
  fontWeights,
  lineHeights,
  radii,
  shadows,
  transitions,
  zIndices
}

export const darkTheme: Theme = {
  colors: {
    ...baseColors,
    // Add dark theme specific overrides here
    background: {
      primary: baseColors.neutral[900],
      secondary: baseColors.neutral[800],
      tertiary: baseColors.neutral[700]
    },
    text: {
      primary: baseColors.neutral[50],
      secondary: baseColors.neutral[200],
      tertiary: baseColors.neutral[400],
      disabled: baseColors.neutral[600]
    }
  },
  spacing,
  fontSizes,
  fontWeights,
  lineHeights,
  radii,
  shadows,
  transitions,
  zIndices
}

export const getThemeValue = (theme: Theme, path: string) => {
  return path.split('.').reduce((acc: any, part: string) => {
    return acc && acc[part]
  }, theme)
}

export const createTheme = (overrides: Partial<Theme> = {}): Theme => {
  return {
    ...lightTheme,
    ...overrides,
    colors: {
      ...lightTheme.colors,
      ...overrides.colors
    }
  }
}
