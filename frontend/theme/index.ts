import { extendTheme } from '@chakra-ui/react';
import { themeConfig } from './config';

const theme = extendTheme({
  config: themeConfig,
  fonts: {
    heading: `'Geist Sans', -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", sans-serif`,
    body: `'Geist Sans', -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", sans-serif`,
  },
  colors: {
    brand: {
      50: '#fffbeb',
      100: '#fef3c7',
      200: '#fde68a',
      300: '#fcd34d',
      400: '#fbbf24',
      500: '#f59e0b',
      600: '#d97706',
      700: '#b45309',
      800: '#92400e',
      900: '#78350f',
    },
    accent: {
      50: '#fef2f2',
      100: '#fee2e2',
      200: '#fecaca',
      300: '#fca5a5',
      400: '#f87171',
      500: '#ef4444',
      600: '#dc2626',
      700: '#b91c1c',
      800: '#991b1b',
      900: '#7f1d1d',
    },
  },
  components: {
    Button: {
      baseStyle: {
        fontWeight: '500',
        borderRadius: '12px',
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        _hover: {
          transform: 'translateY(-2px)',
          boxShadow: '0 12px 24px -10px rgba(0, 0, 0, 0.15)',
        },
        _active: {
          transform: 'translateY(0)',
        },
      },
      variants: {
        solid: {
          bg: 'brand.500',
          color: 'white',
          _hover: {
            bg: 'brand.600',
            _disabled: {
              bg: 'brand.500',
            },
          },
        },
        ghost: {
          _hover: {
            bg: 'rgba(245, 158, 11, 0.08)',
          },
        },
      },
      defaultProps: {
        size: 'lg',
      },
    },
    Input: {
      variants: {
        outline: {
          field: {
            borderRadius: '12px',
            borderWidth: '1.5px',
            borderColor: 'gray.200',
            _dark: {
              borderColor: 'gray.700',
            },
            _hover: {
              borderColor: 'brand.400',
            },
            _focus: {
              borderColor: 'brand.500',
              boxShadow: '0 0 0 1px var(--chakra-colors-brand-500)',
            },
            transition: 'all 0.2s',
          },
        },
      },
    },
    Textarea: {
      variants: {
        outline: {
          borderRadius: '12px',
          borderWidth: '1.5px',
          borderColor: 'gray.200',
          _dark: {
            borderColor: 'gray.700',
          },
          _hover: {
            borderColor: 'brand.400',
          },
          _focus: {
            borderColor: 'brand.500',
            boxShadow: '0 0 0 1px var(--chakra-colors-brand-500)',
          },
          transition: 'all 0.2s',
        },
      },
    },
    Card: {
      baseStyle: {
        container: {
          borderRadius: '20px',
          overflow: 'hidden',
          boxShadow: '0 4px 20px -4px rgba(0, 0, 0, 0.08)',
          backdropFilter: 'blur(20px)',
          borderWidth: '1px',
          borderColor: 'rgba(255, 255, 255, 0.18)',
          _dark: {
            borderColor: 'rgba(255, 255, 255, 0.08)',
            bg: 'rgba(26, 32, 44, 0.6)',
          },
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          _hover: {
            boxShadow: '0 12px 40px -8px rgba(0, 0, 0, 0.12)',
            transform: 'translateY(-2px)',
          },
        },
      },
    },
    Tabs: {
      variants: {
        enclosed: {
          tab: {
            borderRadius: '12px 12px 0 0',
            fontWeight: '500',
            transition: 'all 0.2s',
            _selected: {
              color: 'brand.600',
              borderColor: 'brand.500',
              borderBottomColor: 'white',
              _dark: {
                borderBottomColor: 'gray.800',
              },
            },
          },
        },
      },
    },
    Alert: {
      baseStyle: {
        container: {
          borderRadius: '12px',
        },
      },
    },
  },
  styles: {
    global: {
      body: {
        bg: 'gray.50',
        _dark: {
          bg: '#0a0a0a',
        },
      },
    },
  },
});

export default theme;
