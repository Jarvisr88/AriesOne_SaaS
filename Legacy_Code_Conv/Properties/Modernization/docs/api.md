# Icon System API Documentation

## Components

### IconProvider

The root component that provides theme and CDN configuration to the icon system.

```tsx
import { IconProvider } from './components/IconProvider';

<IconProvider cdnUrl="https://cdn.example.com">
  {/* Your app content */}
</IconProvider>
```

#### Props
- `cdnUrl` (optional): Base URL for CDN assets. Defaults to `/assets/icons`
- `children`: React nodes to render within the provider

### IconLibrary Components

Pre-built SVG icon components with theme support.

```tsx
import { CheckedIcon, UncheckedIcon, ReloadIcon } from './components/IconLibrary';

<CheckedIcon size={24} className="text-primary" />
```

#### Common Props
- `size` (optional): Icon size in pixels. Defaults to 24
- `className` (optional): Additional CSS classes
- Any valid SVG props

### LazyIcon

Component for lazy-loading icons with caching support.

```tsx
import { LazyIcon } from './components/LazyIcon';

<LazyIcon 
  name="checked"
  size={24}
  className="text-primary"
  fallback={<span>Loading...</span>}
/>
```

#### Props
- `name`: Icon name to load
- `size` (optional): Icon size in pixels
- `className` (optional): Additional CSS classes
- `fallback` (optional): React node to show while loading
- Any valid SVG props

## Hooks

### useTheme

Hook for managing theme state.

```tsx
import { useTheme } from './hooks/useTheme';

function Component() {
  const { theme, setTheme, isDark } = useTheme();
  
  return (
    <button onClick={() => setTheme('dark')}>
      Switch to Dark Mode
    </button>
  );
}
```

#### Returns
- `theme`: Current theme ('light' | 'dark' | 'system')
- `setTheme`: Function to update theme
- `isDark`: Boolean indicating if dark mode is active

## Utilities

### Asset Loader

Utilities for managing icon loading and caching.

```tsx
import { loadIcon, preloadIcon, preloadCommonIcons } from './utils/assetLoader';

// Load single icon
await loadIcon('checked', 'light', 'https://cdn.example.com');

// Preload specific icon
preloadIcon('checked', 'light', 'https://cdn.example.com');

// Preload common icons
preloadCommonIcons('https://cdn.example.com');
```

## Styling

### CSS Classes

The icon system provides utility classes for common styling needs:

```css
/* Size variants */
.icon-sm    /* 16px */
.icon-md    /* 24px */
.icon-lg    /* 32px */
.icon-xl    /* 48px */

/* Color variants */
.icon-primary
.icon-secondary
.icon-muted
.icon-success
.icon-warning
.icon-error

/* Animations */
.icon-spin
.icon-pulse
```

## Theme Support

Icons automatically adapt to light/dark mode:

```css
/* Light mode */
.text-primary {
  color: theme(colors.primary.500);
}

/* Dark mode */
.dark .text-primary {
  color: theme(colors.primary.400);
}
```
