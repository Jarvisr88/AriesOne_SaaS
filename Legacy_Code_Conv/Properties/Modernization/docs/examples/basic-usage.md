# Icon System Examples

This guide provides common usage examples for the Icon System.

## Basic Usage

### Simple Icon

```tsx
import { CheckedIcon } from '@/components/IconLibrary';

function Example() {
  return <CheckedIcon size={24} className="text-primary" />;
}
```

### Dynamic Theme

```tsx
import { useTheme } from '@/hooks/useTheme';
import { ReloadIcon } from '@/components/IconLibrary';

function ThemeExample() {
  const { theme, setTheme } = useTheme();
  
  return (
    <button onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>
      <ReloadIcon className="icon-primary icon-md" />
      Toggle Theme
    </button>
  );
}
```

### Lazy Loading

```tsx
import { LazyIcon } from '@/components/LazyIcon';

function LazyExample() {
  return (
    <LazyIcon
      name="checked"
      size={24}
      className="text-success"
      fallback={<span>Loading...</span>}
    />
  );
}
```

## Advanced Usage

### Custom Animation

```tsx
import { ReloadIcon } from '@/components/IconLibrary';

function LoadingButton({ isLoading, onClick }) {
  return (
    <button 
      onClick={onClick}
      disabled={isLoading}
      className="flex items-center gap-2"
    >
      <ReloadIcon className={cn(
        "icon-primary",
        isLoading && "animate-spin"
      )} />
      {isLoading ? 'Loading...' : 'Refresh'}
    </button>
  );
}
```

### Icon Button

```tsx
import { CheckedIcon, UncheckedIcon } from '@/components/IconLibrary';

function ToggleButton({ isChecked, onChange }) {
  return (
    <button
      onClick={() => onChange(!isChecked)}
      className="p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-800"
    >
      {isChecked ? (
        <CheckedIcon className="icon-success icon-md" />
      ) : (
        <UncheckedIcon className="icon-muted icon-md" />
      )}
    </button>
  );
}
```

### Icon with Badge

```tsx
function IconWithBadge({ count }) {
  return (
    <div className="relative">
      <ReloadIcon className="icon-primary icon-md" />
      {count > 0 && (
        <span className="absolute -top-1 -right-1 bg-red-500 text-white rounded-full w-4 h-4 text-xs flex items-center justify-center">
          {count}
        </span>
      )}
    </div>
  );
}
```

### Dynamic Icon Loading

```tsx
function DynamicIcon({ name, ...props }) {
  const [Icon, setIcon] = useState(null);

  useEffect(() => {
    async function loadIcon() {
      try {
        const module = await import(`@/components/icons/${name}`);
        setIcon(() => module.default);
      } catch (error) {
        console.error(`Failed to load icon: ${name}`, error);
      }
    }
    
    loadIcon();
  }, [name]);

  if (!Icon) return null;
  return <Icon {...props} />;
}
```

### Icon Grid

```tsx
const icons = [
  { name: 'checked', label: 'Checked' },
  { name: 'unchecked', label: 'Unchecked' },
  { name: 'reload', label: 'Reload' },
];

function IconGrid() {
  return (
    <div className="grid grid-cols-3 gap-4">
      {icons.map(({ name, label }) => (
        <div key={name} className="flex flex-col items-center gap-2">
          <LazyIcon
            name={name}
            className="icon-primary icon-lg"
            fallback={<div className="w-8 h-8 bg-gray-200 rounded animate-pulse" />}
          />
          <span className="text-sm text-gray-600 dark:text-gray-400">
            {label}
          </span>
        </div>
      ))}
    </div>
  );
}
```

### Theme-Aware Icon

```tsx
function AdaptiveIcon({ lightIcon, darkIcon, ...props }) {
  const { isDark } = useTheme();
  
  return (
    <LazyIcon
      name={isDark ? darkIcon : lightIcon}
      {...props}
    />
  );
}

// Usage
<AdaptiveIcon
  lightIcon="sun"
  darkIcon="moon"
  className="icon-primary icon-md"
/>
```

## Performance Tips

### Preloading Common Icons

```tsx
import { preloadCommonIcons } from '@/utils/assetLoader';

function App() {
  useEffect(() => {
    preloadCommonIcons(process.env.NEXT_PUBLIC_CDN_URL);
  }, []);

  return <div>Your app content</div>;
}
```

### Optimizing Bundle Size

```tsx
// Import specific icons instead of the whole library
import { CheckedIcon } from '@/components/IconLibrary/CheckedIcon';
import { ReloadIcon } from '@/components/IconLibrary/ReloadIcon';
```
