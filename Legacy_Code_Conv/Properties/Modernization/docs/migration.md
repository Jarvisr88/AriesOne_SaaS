# Migration Guide

This guide outlines the process of migrating from the legacy Properties module to the new Icon System.

## Overview

The new Icon System replaces the legacy bitmap-based resources with modern, scalable SVG icons and provides:
- Theme support (light/dark mode)
- CDN integration
- Lazy loading
- Performance optimizations

## Step-by-Step Migration

### 1. Update Dependencies

Add required dependencies to your `package.json`:

```json
{
  "dependencies": {
    "@radix-ui/react-icons": "^1.3.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.0.0"
  }
}
```

### 2. Replace Legacy Imports

#### Before:
```csharp
using DMEWorks.Properties;
var checkedIcon = Resources.Checked;
```

#### After:
```tsx
import { CheckedIcon } from '@/components/IconLibrary';
<CheckedIcon size={24} />;
```

### 3. Setup Icon Provider

Add the IconProvider to your app's root:

```tsx
// _app.tsx or App.tsx
import { IconProvider } from '@/components/IconProvider';

export default function App({ Component, pageProps }) {
  return (
    <IconProvider cdnUrl={process.env.NEXT_PUBLIC_CDN_URL}>
      <Component {...pageProps} />
    </IconProvider>
  );
}
```

### 4. Update Theme Configuration

Add theme configuration to your Tailwind config:

```js
// tailwind.config.js
module.exports = {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          light: '#...',
          dark: '#...',
        },
        // ... other colors
      }
    }
  }
};
```

### 5. Replace Image References

#### Before:
```csharp
pictureBox1.Image = Resources.Reload;
```

#### After:
```tsx
<ReloadIcon className="icon-primary icon-md" />
```

### 6. Implement Lazy Loading

For dynamically loaded icons:

```tsx
<LazyIcon 
  name="reload"
  size={24}
  className="icon-primary"
  fallback={<LoadingSpinner />}
/>
```

## CDN Setup

1. Configure CDN environment:
```env
NEXT_PUBLIC_CDN_URL=https://your-cdn.com/assets
NEXT_PUBLIC_CDN_REGION=us-east-1
```

2. Upload icons to CDN:
```bash
# Example script
./scripts/upload-icons.sh
```

## Performance Optimization

1. Preload common icons:
```tsx
useEffect(() => {
  preloadCommonIcons(process.env.NEXT_PUBLIC_CDN_URL);
}, []);
```

2. Configure caching:
```tsx
// config/cdn.config.ts
export const cacheConfig = {
  maxAge: 24 * 60 * 60 * 1000,
  maxSize: 100
};
```

## Testing Changes

Run the test suite to verify migration:
```bash
npm run test
```

## Troubleshooting

### Common Issues

1. Icons not loading
   - Check CDN URL configuration
   - Verify icon filenames match
   - Check network requests

2. Theme not working
   - Verify IconProvider is at root
   - Check dark mode configuration
   - Inspect HTML classes

3. Performance issues
   - Enable preloading for common icons
   - Verify CDN caching headers
   - Check browser caching

## Rollback Plan

If issues occur, you can temporarily revert to legacy system:

1. Keep legacy Resources.cs
2. Add feature flag:
```tsx
const useLegacyIcons = process.env.USE_LEGACY_ICONS === 'true';
```

3. Conditional rendering:
```tsx
{useLegacyIcons ? <LegacyIcon /> : <ModernIcon />}
```
