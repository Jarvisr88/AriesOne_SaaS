import { extendTheme, ThemeConfig } from '@chakra-ui/react';

const config: ThemeConfig = {
  initialColorMode: 'system',
  useSystemColorMode: true,
};

const colors = {
  brand: {
    50: '#E6F6FF',
    100: '#BAE3FF',
    200: '#7CC4FA',
    300: '#47A3F3',
    400: '#2186EB',
    500: '#0967D2',
    600: '#0552B5',
    700: '#03449E',
    800: '#01337D',
    900: '#002159',
  },
  accent: {
    50: '#FFE6EF',
    100: '#FFB8D2',
    200: '#FF8CBA',
    300: '#F364A2',
    400: '#E8368F',
    500: '#DA127D',
    600: '#BC0A6F',
    700: '#A30664',
    800: '#870557',
    900: '#620042',
  },
  success: {
    50: '#E3F9E5',
    100: '#C1F2C7',
    200: '#91E697',
    300: '#51CA58',
    400: '#31B237',
    500: '#18981D',
    600: '#0F8613',
    700: '#0E7817',
    800: '#07600E',
    900: '#014807',
  },
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
    900: '#8D2B0B',
  },
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
    900: '#610316',
  },
};

const semanticTokens = {
  colors: {
    'bg.primary': {
      default: 'white',
      _dark: 'gray.800',
    },
    'bg.secondary': {
      default: 'gray.50',
      _dark: 'gray.700',
    },
    'bg.tertiary': {
      default: 'gray.100',
      _dark: 'gray.600',
    },
    'text.primary': {
      default: 'gray.900',
      _dark: 'white',
    },
    'text.secondary': {
      default: 'gray.600',
      _dark: 'gray.300',
    },
    'border.primary': {
      default: 'gray.200',
      _dark: 'gray.600',
    },
  },
};

const components = {
  Button: {
    baseStyle: {
      fontWeight: 'semibold',
      borderRadius: 'lg',
    },
    variants: {
      solid: (props: any) => ({
        bg: `${props.colorScheme}.500`,
        color: 'white',
        _hover: {
          bg: `${props.colorScheme}.600`,
        },
        _active: {
          bg: `${props.colorScheme}.700`,
        },
      }),
      outline: (props: any) => ({
        border: '2px solid',
        borderColor: `${props.colorScheme}.500`,
        color: `${props.colorScheme}.500`,
        _hover: {
          bg: `${props.colorScheme}.50`,
        },
        _active: {
          bg: `${props.colorScheme}.100`,
        },
      }),
    },
  },
  Card: {
    baseStyle: {
      container: {
        bg: 'bg.primary',
        borderRadius: 'xl',
        boxShadow: 'lg',
        border: '1px solid',
        borderColor: 'border.primary',
        transition: 'all 0.2s',
        _hover: {
          transform: 'translateY(-2px)',
          boxShadow: 'xl',
        },
      },
    },
  },
  Input: {
    variants: {
      filled: {
        field: {
          bg: 'bg.secondary',
          _hover: {
            bg: 'bg.tertiary',
          },
          _focus: {
            bg: 'bg.tertiary',
          },
        },
      },
    },
    defaultProps: {
      variant: 'filled',
    },
  },
};

const fonts = {
  heading: 'Inter, system-ui, sans-serif',
  body: 'Inter, system-ui, sans-serif',
};

const styles = {
  global: (props: any) => ({
    body: {
      bg: 'bg.primary',
      color: 'text.primary',
    },
    '*::placeholder': {
      color: 'text.secondary',
    },
    '::selection': {
      backgroundColor: `${props.colorMode === 'dark' ? 'brand.600' : 'brand.100'}`,
      color: `${props.colorMode === 'dark' ? 'white' : 'brand.900'}`,
    },
  }),
};

const transitions = {
  easing: {
    'ease-out': 'cubic-bezier(0.16, 1, 0.3, 1)',
    'ease-in': 'cubic-bezier(0.7, 0, 0.84, 0)',
    'ease-in-out': 'cubic-bezier(0.87, 0, 0.13, 1)',
  },
  duration: {
    'ultra-fast': '0.05s',
    faster: '0.1s',
    fast: '0.15s',
    normal: '0.2s',
    slow: '0.3s',
    slower: '0.4s',
    'ultra-slow': '0.5s',
  },
};

const theme = extendTheme({
  config,
  colors,
  semanticTokens,
  components,
  fonts,
  styles,
  transitions,
});

export default theme;
